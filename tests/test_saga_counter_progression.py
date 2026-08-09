from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common import ROOT, keep_all, make_session
from scripts.build_test_database import build_fixture_database
from quorune.card_programs import CardProgram
from quorune.card_programs.adapters import compile_card_program
from quorune.carddb import CardDatabase, CardRecord
from quorune.deck import DeckLoader
from quorune.engine import TURN_STEPS
from quorune.entry_counter_model import (
    EntryCounterError,
    intrinsic_entry_counters,
)
from quorune.model import CardInstance, StackItem
from quorune.projection import StateProjector
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)
from quorune.replacement import (
    AffectedObject,
    ReplaceableEvent,
    ReplacementClass,
    ReplacementEffect,
    SetField,
    apply_replacement,
    replacement_choice,
)
from quorune.replacement_effects import ReplacementChoiceRequired
from quorune.rules.capabilities import (
    CapabilityRegistry,
    load_default_capability_registry,
)
from quorune.saga_progression import (
    SagaProgressionError,
    advance_active_player_sagas,
    capture_saga_lore_turn_action,
    commit_saga_lore_turn_action,
    dispatch_saga_chapters,
)
from quorune.semantic_runtime import prepare_zone_change_replacement_batch


class SagaCounterProgressionTests(unittest.TestCase):
    """CR 714.3a/714.3c lore counters and the CR 614.16 boundary."""

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        database = Path(cls.temporary.name) / "saga-counters.sqlite3"
        build_fixture_database(
            [
                ROOT / "tests" / "fixtures" / "scryfall-exact-lists.json",
                ROOT
                / "tests"
                / "fixtures"
                / "counter-replacement-cards.json",
            ],
            database,
        )
        cls.db = CardDatabase(database)
        cls.capabilities = load_default_capability_registry()
        loader = DeckLoader(cls.db)
        cls.mishra = loader.load(
            ROOT / "examples" / "mishra-eminent-one.txt",
            commander="Mishra, Eminent One",
            deck_name="Mishra",
        )
        cls.zimone = loader.load(
            ROOT / "examples" / "zimone-and-dina.txt",
            commander="Zimone and Dina",
            deck_name="Zimone",
        )

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temporary.cleanup()

    def session(self, seed: int, *, players: int = 2):
        session = make_session(
            self.db,
            self.mishra,
            self.zimone,
            players=players,
            seed=seed,
            auto_pass_empty=False,
        )
        keep_all(session)
        engine = session.engine
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.state.priority_passes = []
        session.commands.clear()
        session.decisions.clear()
        return session

    @staticmethod
    def card(engine, owner: str, name: str) -> CardInstance:
        return next(
            card
            for card in engine.state.cards.values()
            if card.owner == owner
            and card.is_card_object
            and card.printed_name == name
        )

    def add_permanent(
        self,
        engine,
        *,
        seat: str,
        name: str,
        ref: str,
    ) -> CardInstance:
        record = self.db.lookup(name)
        card = CardInstance(
            object_id=f"fixture:{ref}",
            ref=ref,
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner=seat,
            controller=seat,
            zone="battlefield",
            zone_timestamp=engine.state.event_sequence + 1,
            known_to=list(engine.seats),
            revealed_to=list(engine.seats),
        )
        engine.state.cards[card.object_id] = card
        engine.state.players[seat].zones["battlefield"].append(card.object_id)
        return card

    def add_saga(
        self,
        engine,
        *,
        seat: str,
        ref: str,
        zone: str = "exile",
        oracle_id: str | None = None,
    ) -> CardInstance:
        base = self.db.lookup("Island")
        card = CardInstance(
            object_id=f"fixture:{ref}",
            ref=ref,
            oracle_id=oracle_id or base.oracle_id,
            printed_name=ref,
            owner=seat,
            controller=seat,
            zone=zone,
            annotations={
                "copy_overrides": {
                    "name": ref,
                    "type_line": "Enchantment — Saga",
                    "oracle_text": "",
                }
            },
            known_to=list(engine.seats),
            revealed_to=list(engine.seats),
        )
        engine.state.cards[card.object_id] = card
        if zone in engine.state.players[seat].zones:
            engine.state.players[seat].zones[zone].append(card.object_id)
        return card

    def stage_competing_sources(self, engine, *, seat: str) -> None:
        prefix = seat.casefold()
        self.add_permanent(
            engine,
            seat=seat,
            name="Doubling Season",
            ref=f"{prefix}-doubling",
        )
        self.add_permanent(
            engine,
            seat=seat,
            name="Doc Samson, Super Psychiatrist",
            ref=f"{prefix}-doc",
        )

    @staticmethod
    def saga_record(*, read_ahead: bool = False) -> CardRecord:
        return CardRecord(
            oracle_id=(
                "00000000-0000-4000-8000-714300000001"
                if not read_ahead
                else "00000000-0000-4000-8000-714300000002"
            ),
            name="Saga Card-Form Fixture",
            mana_cost="{2}",
            mana_value=2.0,
            type_line="Enchantment — Saga",
            oracle_text=(
                "Lifelink\n"
                "(As this Saga enters and after your draw step, add a lore "
                "counter. Sacrifice after III.)"
            ),
            power=None,
            toughness=None,
            loyalty=None,
            defense=None,
            colors=(),
            color_identity=(),
            keywords=(
                ("Lifelink", "Read Ahead")
                if read_ahead
                else ("Lifelink",)
            ),
            produced_mana=(),
            layout="normal",
            released_at="2026-01-01",
            legalities={"commander": "legal"},
            faces=(),
            raw={},
        )

    def test_ordinary_saga_card_form_is_source_spanned_and_closed(self):
        record = self.saga_record()
        program = compile_card_program(
            self.db,
            record,
            capability_registry=self.capabilities,
            capability_profile="commander_review",
            trust_level="trusted",
        )

        self.assertIn(
            "counter.producer.saga_lore",
            program.capability_dependencies,
        )
        self.assertTrue(program.trust_closure["trusted"])
        self.assertEqual((), program.residuals)
        ability = next(
            value
            for value in program.to_dict()["abilities"]
            if value["runtime"]["provenance"].get("source_kind")
            == "type_line"
        )
        self.assertEqual(
            {"line": 1, "start": 0, "end": len(record.type_line)},
            ability["source_span"],
        )
        self.assertEqual(
            "lore",
            ability["runtime"]["provenance"]
            ["card_form_descriptor"]["counter_name"],
        )
        self.assertEqual(
            program.to_dict(),
            CardProgram.from_dict(program.to_dict()).to_dict(),
        )

    def test_read_ahead_and_untrusted_chapters_fail_closed(self):
        program = compile_card_program(
            self.db,
            self.saga_record(read_ahead=True),
            capability_registry=self.capabilities,
            capability_profile="commander_review",
            trust_level="provisional",
        )
        residual = next(
            value
            for value in program.residuals
            if value["kind"] == "card_form_rule"
        )
        self.assertTrue(residual["material"])
        self.assertEqual(
            ["counter.producer.saga_lore"], residual["blockers"]
        )
        self.assertIn("Read Ahead", residual["reason"])

        session = self.session(7143001)
        engine = session.engine
        unsupported = self.add_saga(
            engine,
            seat="A",
            ref="untrusted-saga",
            zone="battlefield",
        )
        before = authoritative_state_hash(engine.state)
        with self.assertRaisesRegex(
            SagaProgressionError, "trusted typed chapter programs"
        ):
            capture_saga_lore_turn_action(engine, "A")
        self.assertEqual(0, unsupported.counters.get("lore", 0))
        self.assertEqual(before, authoritative_state_hash(engine.state))

        with self.assertRaisesRegex(EntryCounterError, "Read Ahead"):
            intrinsic_entry_counters(
                {},
                card_types=("enchantment",),
                card_subtypes=("saga",),
                keywords=("Read Ahead",),
            )

    def test_entry_and_precombat_lore_use_distinct_counter_paths(self):
        session = self.session(7143002)
        engine = session.engine
        saga = self.card(engine, "A", "Urza's Saga")
        engine.move_card(
            saga.object_id,
            "battlefield",
            controller="A",
            log=False,
            semantic_events=True,
        )

        self.assertEqual(1, saga.counters["lore"])
        self.assertTrue(engine.state.pending_trigger_batches)
        self.assertIn(
            "chapter I",
            engine.state.pending_trigger_batches[-1].items[0].label,
        )
        engine.state.pending_trigger_batches.clear()
        engine.state.stack.clear()

        advance_active_player_sagas(engine, "A")

        self.assertEqual(2, saga.counters["lore"])
        self.assertTrue(engine.state.pending_trigger_batches)
        self.assertIn(
            "chapter II",
            engine.state.pending_trigger_batches[-1].items[0].label,
        )

    def test_saga_entry_counter_uses_quantity_replacement_but_turn_action_does_not(
        self,
    ):
        session = self.session(7143003)
        engine = session.engine
        self.add_permanent(
            engine,
            seat="A",
            name="Doubling Season",
            ref="a-doubling",
        )
        saga = self.card(engine, "A", "Urza's Saga")
        engine.move_card(
            saga.object_id,
            "battlefield",
            controller="A",
            log=False,
            semantic_events=False,
        )

        self.assertEqual(2, saga.counters["lore"])
        advance_active_player_sagas(engine, "A")
        self.assertEqual(3, saga.counters["lore"])

    def test_multiple_sagas_commit_lore_before_any_chapter_dispatch(self):
        session = self.session(7143004)
        engine = session.engine
        first = self.card(engine, "A", "Urza's Saga")
        engine.move_card(
            first.object_id,
            "battlefield",
            controller="A",
            log=False,
            semantic_events=False,
        )
        second = CardInstance(
            object_id="fixture:second-urzas-saga",
            ref="second-urzas-saga",
            oracle_id=first.oracle_id,
            printed_name=first.printed_name,
            owner="A",
            controller="A",
            zone="battlefield",
            known_to=list(engine.seats),
            revealed_to=list(engine.seats),
            counters={"lore": 1},
        )
        engine.state.cards[second.object_id] = second
        engine.state.players["A"].zones["battlefield"].append(
            second.object_id
        )
        observed: list[tuple[int, int]] = []
        waiting_triggers: list[StackItem] = []
        original = dispatch_saga_chapters

        def observe(*args, **kwargs):
            observed.append(
                (first.counters["lore"], second.counters["lore"])
            )
            return original(*args, **kwargs)

        with patch(
            "quorune.saga_progression.dispatch_saga_chapters",
            side_effect=observe,
        ):
            advance_active_player_sagas(
                engine,
                "A",
                trigger_batch=waiting_triggers,
            )

        self.assertEqual((2, 2), observed[0])
        self.assertEqual((2, 2), observed[-1])
        self.assertEqual(2, len(waiting_triggers))
        self.assertEqual([], engine.state.pending_trigger_batches)

    def test_stale_saga_snapshot_rolls_back_without_partial_mutation(self):
        session = self.session(7143005)
        engine = session.engine
        first = self.card(engine, "A", "Urza's Saga")
        engine.move_card(
            first.object_id,
            "battlefield",
            controller="A",
            log=False,
            semantic_events=False,
        )
        second = CardInstance(
            object_id="fixture:stale-urzas-saga",
            ref="stale-urzas-saga",
            oracle_id=first.oracle_id,
            printed_name=first.printed_name,
            owner="A",
            controller="A",
            zone="battlefield",
            known_to=list(engine.seats),
            revealed_to=list(engine.seats),
            counters={"lore": 1},
        )
        engine.state.cards[second.object_id] = second
        engine.state.players["A"].zones["battlefield"].append(
            second.object_id
        )
        action = capture_saga_lore_turn_action(engine, "A")
        second.controller = "B"
        before = authoritative_state_hash(engine.state)

        with self.assertRaisesRegex(
            SagaProgressionError, "snapshot changed before commit"
        ):
            commit_saga_lore_turn_action(engine, action)

        self.assertEqual(1, first.counters["lore"])
        self.assertEqual(1, second.counters["lore"])
        self.assertEqual(before, authoritative_state_hash(engine.state))

    def test_competing_saga_entry_replacements_order_to_three_or_four(self):
        results: set[int] = set()
        for seed in (7143006, 7143007):
            session = self.session(seed)
            engine = session.engine
            self.stage_competing_sources(engine, seat="A")
            saga = self.add_saga(
                engine,
                seat="A",
                ref=f"saga-order-{seed}",
            )
            before = authoritative_state_hash(engine.state)
            with self.assertRaises(ReplacementChoiceRequired) as raised:
                engine.move_card(
                    saga.object_id,
                    "battlefield",
                    controller="A",
                    semantic_events=False,
                )
            self.assertEqual(before, authoritative_state_hash(engine.state))
            selected = raised.exception.pending.choice.options[seed % 2]
            engine.move_card(
                saga.object_id,
                "battlefield",
                controller="A",
                replacement_selections=(selected,),
                semantic_events=False,
            )
            results.add(saga.counters["lore"])
        self.assertEqual({3, 4}, results)

    def test_destination_redirect_retargets_nested_saga_counter(self):
        event = ReplaceableEvent(
            event_id="saga-entry-retarget",
            kind="zone.change",
            affected_player=None,
            affected_object=AffectedObject(
                object_id="saga-object",
                owner="A",
                controller=None,
            ),
            payload={
                "origin": "graveyard",
                "destination": "battlefield",
                "destination_controller": "A",
                "object_kind": "card",
                "object_ref": "saga-ref",
                "object_types": ["enchantment", "saga"],
                "logical_object_id": "saga-object:1",
                "owner": "A",
            },
        )
        counter = intrinsic_entry_counters(
            {},
            card_types=("enchantment",),
            card_subtypes=("saga",),
        )[0]
        from quorune.entry_counters import intrinsic_entry_counter_effects

        entry = intrinsic_entry_counter_effects(
            object_ref="saga-ref",
            destination_controller="A",
            counters=(counter,),
        )[0]
        created = apply_replacement(
            replacement_choice(event, (entry,)),
            (entry,),
            entry.effect_id,
        )
        redirect = ReplacementEffect(
            effect_id="redirect-saga-to-exile",
            source_id="replacement-source",
            event_kind="zone.change",
            replacement_class=ReplacementClass.OTHER,
            conditions={"destination": {"eq": "battlefield"}},
            operations=(SetField(field="destination", value="exile"),),
        )
        redirected = apply_replacement(
            replacement_choice(created, (redirect,)),
            (redirect,),
            redirect.effect_id,
        )

        self.assertEqual("exile", redirected.payload["destination"])
        self.assertEqual("exile", redirected.children[0].payload["target_zone"])

    def test_four_player_saga_entry_replacement_choices_follow_apnap(self):
        session = self.session(7143008, players=4)
        engine = session.engine
        self.stage_competing_sources(engine, seat="A")
        self.stage_competing_sources(engine, seat="B")
        saga_a = self.add_saga(engine, seat="A", ref="saga-apnap-a")
        saga_b = self.add_saga(engine, seat="B", ref="saga-apnap-b")
        changes = (
            (saga_b.object_id, "battlefield"),
            (saga_a.object_id, "battlefield"),
        )
        controllers = {saga_a.object_id: "A", saga_b.object_id: "B"}
        before = authoritative_state_hash(engine.state)

        with self.assertRaises(ReplacementChoiceRequired) as first:
            prepare_zone_change_replacement_batch(
                engine,
                changes,
                destination_controllers=controllers,
                error_type=EntryCounterError,
            )
        self.assertEqual("A", first.exception.pending.choice.chooser)
        first_selection = first.exception.pending.choice.options[0]
        with self.assertRaises(ReplacementChoiceRequired) as second:
            prepare_zone_change_replacement_batch(
                engine,
                changes,
                destination_controllers=controllers,
                selections=(first_selection,),
                error_type=EntryCounterError,
            )
        self.assertEqual("B", second.exception.pending.choice.chooser)
        self.assertEqual(before, authoritative_state_hash(engine.state))

    def test_four_player_precombat_lore_only_advances_active_players_sagas(
        self,
    ):
        session = self.session(7143013, players=4)
        engine = session.engine
        active_saga = self.card(engine, "A", "Urza's Saga")
        engine.move_card(
            active_saga.object_id,
            "battlefield",
            controller="A",
            log=False,
            semantic_events=False,
        )
        other_saga = CardInstance(
            object_id="fixture:nonactive-urzas-saga",
            ref="nonactive-urzas-saga",
            oracle_id=active_saga.oracle_id,
            printed_name=active_saga.printed_name,
            owner="B",
            controller="B",
            zone="battlefield",
            known_to=list(engine.seats),
            revealed_to=list(engine.seats),
            counters={"lore": 1},
        )
        engine.state.cards[other_saga.object_id] = other_saga
        engine.state.players["B"].zones["battlefield"].append(
            other_saga.object_id
        )

        advance_active_player_sagas(engine, "A")

        self.assertEqual(2, active_saga.counters["lore"])
        self.assertEqual(1, other_saga.counters["lore"])

    def test_saga_entry_replacement_choice_replays_exactly(self):
        session = self.session(7143009, players=4)
        engine = session.engine
        self.stage_competing_sources(engine, seat="A")
        saga = self.card(engine, "A", "Urza's Saga")
        engine._remove_from_zone(saga)
        engine._reset_zone_change(saga, "stack")
        saga.zone = "stack"
        saga.controller = "A"
        saga.known_to = list(engine.seats)
        saga.revealed_to = list(engine.seats)
        item = StackItem(
            stack_id="saga-resolution-stack",
            ref="S-saga-resolution",
            kind="spell",
            controller="A",
            label="Saga Entry Fixture",
            card_object_id=saga.object_id,
            default_destination="battlefield",
            visibility=list(engine.seats),
        )
        engine.state.stack.append(item)
        engine._continue_resolution(
            stack_ref=item.ref,
            effects=[],
            destination=None,
            note="Saga entry replacement replay",
        )

        self.assertEqual("replacement.order", engine.state.pending_decision.kind)
        projector = StateProjector(self.db, engine.state)
        projected_a = projector._decision("pilot:A")
        self.assertIsNotNone(projected_a)
        for seat in ("B", "C", "D"):
            self.assertIsNone(projector._decision(f"pilot:{seat}"))
        serialized = json.dumps(projected_a, sort_keys=True)
        self.assertNotIn("replacement_batch", serialized)
        self.assertNotIn(saga.object_id, serialized)

        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        selection = projected_a["ctx"]["options"][0]["id"]
        result = session.act(
            "pilot:A",
            {
                "action_id": "choose",
                "choices": {"replacement": selection},
            },
        )
        self.assertTrue(result.ok, result.summary)
        self.assertEqual("battlefield", saga.zone)
        self.assertIn(saga.counters["lore"], {3, 4})
        expected_hash = authoritative_state_hash(engine.state)

        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "saga-entry-record"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_precombat_saga_progression_replays_exactly(self):
        session = self.session(7143014)
        engine = session.engine
        saga = self.card(engine, "A", "Urza's Saga")
        engine.move_card(
            saga.object_id,
            "battlefield",
            controller="A",
            log=False,
            semantic_events=False,
        )
        engine.state.active_player = "A"
        engine.state.phase_index = TURN_STEPS.index(("beginning", "draw"))
        engine.state.stack.clear()
        engine.state.pending_trigger_batches.clear()
        engine._grant_priority("A")
        engine.pump()
        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()

        for seat in ("A", "B"):
            result = session.act(
                f"pilot:{seat}",
                {"a": "pass", "reason": "Advance to the main phase."},
            )
            self.assertTrue(result.ok, result.summary)

        self.assertEqual(2, saga.counters["lore"])
        expected_hash = authoritative_state_hash(engine.state)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "saga-precombat-record"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_saga_counter_producer_mutations_are_killed(self):
        def assert_entry_counter_created(seed: int) -> None:
            session = self.session(seed)
            engine = session.engine
            saga = self.add_saga(
                engine,
                seat="A",
                ref=f"saga-mutation-{seed}",
            )
            engine.move_card(
                saga.object_id,
                "battlefield",
                controller="A",
                semantic_events=False,
            )
            self.assertEqual(1, saga.counters.get("lore", 0))

        assert_entry_counter_created(7143015)
        with patch(
            "quorune.semantic_runtime.zone_replacements."
            "intrinsic_entry_counter_effects",
            return_value=(),
        ):
            with self.assertRaises(AssertionError):
                assert_entry_counter_created(7143016)

    def test_blocked_dependency_prevents_trusted_saga_card_form(self):
        registry_value = json.loads(
            (ROOT / "quorune" / "rules" / "capability-registry.json")
            .read_text(encoding="utf-8")
        )
        dependency = next(
            row
            for row in registry_value["capabilities"]
            if row["id"] == "counter.placement.quantity_replacement"
        )
        dependency["status"] = "blocked"
        dependency["blockers"] = ["test mutation"]
        registry = CapabilityRegistry(copy.deepcopy(registry_value))
        registry.mark_evidence_verified("0" * 64)

        with self.assertRaisesRegex(
            ValueError, "intrinsic entry-counter capability is blocked"
        ):
            compile_card_program(
                self.db,
                self.saga_record(),
                capability_registry=registry,
                capability_profile="commander_review",
                trust_level="trusted",
            )


if __name__ == "__main__":
    unittest.main()
