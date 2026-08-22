from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common import ROOT, keep_all, make_session
from quorune.carddb import CardDatabase
from quorune.compiler.fixed_self_entry_counter_templates import (
    FIXED_SELF_ENTRY_COUNTER_CAPABILITY,
    FIXED_SELF_ENTRY_COUNTER_TEMPLATE,
    fixed_self_entry_counter_handler,
)
from quorune.deck import DeckLoader
from quorune.fixed_keyword_entry_counters import (
    FIXED_KEYWORD_ENTRY_CAPABILITY,
    FixedKeywordEntryCounterError,
    FixedKeywordEntryCounterSpec,
)
from quorune.model import CardInstance, StackItem
from quorune.oracle_ir import compile_oracle_card, generated_programs
from quorune.projection import StateProjector
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)
from quorune.rules.capabilities import (
    CapabilityRegistry,
    load_default_capability_registry,
)
from quorune.semantic_runtime import zone_replacements
from scripts.build_test_database import build_fixture_database


REGISTRY_PATH = ROOT / "quorune" / "rules" / "capability-registry.json"
TEMPLATE_IDS = {
    "fading-fixed-entry-counter-v1",
    "graft-fixed-entry-counter-v1",
    "vanishing-fixed-entry-counter-v1",
}
ALL_ENTRY_TEMPLATE_IDS = TEMPLATE_IDS | {FIXED_SELF_ENTRY_COUNTER_TEMPLATE}


def focused_database(directory: str) -> CardDatabase:
    database = Path(directory) / "fixed-keyword-entry.sqlite3"
    build_fixture_database(
        [
            ROOT / "tests" / "fixtures" / "scryfall-exact-lists.json",
            ROOT / "tests" / "fixtures" / "counter-replacement-cards.json",
            ROOT
            / "tests"
            / "fixtures"
            / "fixed-keyword-entry-counter-cards.json",
            ROOT
            / "tests"
            / "fixtures"
            / "fixed-self-entry-counter-cards.json",
        ],
        database,
    )
    return CardDatabase(database)


class FixedKeywordEntryCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_database(cls.temporary.name)
        cls.capabilities = load_default_capability_registry()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temporary.cleanup()

    def test_fixed_keyword_entry_models_and_compiler_split_are_closed(self):
        expected = {
            "Fading Entry Fixture": ("fading", 5, "fade", "702.32a"),
            "Graft Entry Fixture": ("graft", 2, "+1/+1", "702.58a"),
            "Vanishing Entry Fixture": ("vanishing", 3, "time", "702.63a"),
        }
        for name, (mechanic, amount, counter_name, rule_id) in expected.items():
            with self.subTest(name=name):
                spec = FixedKeywordEntryCounterSpec(mechanic, amount)
                self.assertEqual(counter_name, spec.counter_name)
                self.assertEqual(rule_id, spec.rule_id)
                descriptor = spec.handler_descriptor()
                self.assertEqual(counter_name, descriptor["counter_name"])
                self.assertEqual(amount, descriptor["amount"])
                self.assertIs(False, descriptor["optional"])

                record = self.db.lookup(name)
                ir = compile_oracle_card(
                    record,
                    capability_registry=self.capabilities,
                    capability_profile="commander_review",
                )
                entry = next(
                    node
                    for node in ir.faces[0].nodes
                    if node.template_id in TEMPLATE_IDS
                )
                lifecycle = next(
                    node
                    for node in ir.faces[0].nodes
                    if node.node_id.endswith(":lifecycle")
                )
                self.assertTrue(entry.exact)
                self.assertEqual((FIXED_KEYWORD_ENTRY_CAPABILITY,), entry.capability_dependencies)
                self.assertEqual((mechanic,), entry.mechanics)
                self.assertEqual((mechanic,), lifecycle.mechanics)
                self.assertTrue(lifecycle.residual_ids)
                keyword_end = record.oracle_text.index(" (")
                self.assertEqual(
                    (0, keyword_end),
                    (entry.span.start, entry.span.end),
                )
                programs = [
                    program
                    for program in generated_programs(
                        self.db,
                        record,
                        trust_level="trusted",
                        capability_registry=self.capabilities,
                        capability_profile="commander_review",
                    )
                    if program.provenance.get("template_id") in TEMPLATE_IDS
                ]
                self.assertEqual(1, len(programs))
                self.assertTrue(programs[0].capability_closure["trusted"])

        repeated = replace(
            self.db.lookup("Fading Entry Fixture"),
            oracle_text="Fading 2, Fading 3",
            keywords=("Fading",),
        )
        repeated_programs = [
            program
            for program in generated_programs(
                self.db,
                repeated,
                trust_level="trusted",
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            )
            if program.provenance.get("template_id")
            == "fading-fixed-entry-counter-v1"
        ]
        self.assertEqual(2, len(repeated_programs))
        self.assertEqual(2, len({program.key for program in repeated_programs}))
        self.assertEqual(
            [2, 3],
            sorted(program.handlers[0]["amount"] for program in repeated_programs),
        )

        for mechanic, amount in (("fading", 0), ("unknown", 1), ("graft", True)):
            with self.subTest(mechanic=mechanic, amount=amount):
                with self.assertRaises(FixedKeywordEntryCounterError):
                    FixedKeywordEntryCounterSpec(mechanic, amount)

    def test_nonfixed_forms_and_remaining_lifecycles_stay_material(self):
        source = self.db.lookup("Vanishing Entry Fixture")
        for text, keyword in (
            ("Vanishing", "Vanishing"),
            ("Vanishing X", "Vanishing"),
            ("Fading 0", "Fading"),
            ("Graft X", "Graft"),
        ):
            with self.subTest(text=text):
                ir = compile_oracle_card(
                    replace(source, oracle_text=text, keywords=(keyword,)),
                    capability_registry=self.capabilities,
                    capability_profile="commander_review",
                )
                self.assertFalse(
                    any(node.template_id in TEMPLATE_IDS for node in ir.faces[0].nodes)
                )
                self.assertTrue(ir.material_residuals)

        for name in (
            "Fading Entry Fixture",
            "Graft Entry Fixture",
            "Vanishing Entry Fixture",
        ):
            ir = compile_oracle_card(
                self.db.lookup(name),
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            )
            self.assertNotEqual("exact", ir.status)
            self.assertTrue(
                any(
                    "remaining-lifecycle" in blocker
                    for residual in ir.material_residuals
                    for blocker in residual.blockers
                )
            )

    def test_fixed_keyword_entry_dependency_and_compiler_mutations_fail_closed(self):
        record = self.db.lookup("Graft Entry Fixture")
        value = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        dependency = next(
            row
            for row in value["capabilities"]
            if row["id"] == "counter.placement.quantity_replacement"
        )
        dependency["status"] = "blocked"
        dependency["blockers"] = ["test mutation"]
        ir = compile_oracle_card(
            record,
            capability_registry=CapabilityRegistry(value),
            capability_profile="commander_review",
        )
        entry = next(
            node for node in ir.faces[0].nodes if node.template_id in TEMPLATE_IDS
        )
        self.assertFalse(entry.exact)
        self.assertTrue(entry.residual_ids)

        with patch("quorune.oracle_ir.fixed_keyword_entry_nodes", return_value=()):
            mutated = compile_oracle_card(
                record,
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            )
        self.assertFalse(
            any(node.template_id in TEMPLATE_IDS for node in mutated.faces[0].nodes)
        )

    def test_fixed_self_entry_counter_grammar_is_closed(self):
        expected = {
            "Fixed Counter Entrant": ("+1/+1", 3, False),
            "Fixed Charge Vessel": ("charge", 3, False),
            "Named Counter Entrant": ("deathtouch", 1, True),
        }
        for name, (counter_name, amount, keyword_counter) in expected.items():
            with self.subTest(name=name):
                record = self.db.lookup(name)
                compiled = fixed_self_entry_counter_handler(
                    record.oracle_text,
                    source_name=record.name,
                )
                self.assertIsNotNone(compiled)
                assert compiled is not None
                self.assertEqual(FIXED_SELF_ENTRY_COUNTER_TEMPLATE, compiled[0])
                self.assertEqual(counter_name, compiled[1]["counter_name"])
                self.assertEqual(amount, compiled[1]["amount"])
                self.assertIs(False, compiled[1]["optional"])

                ir = compile_oracle_card(
                    record,
                    capability_registry=self.capabilities,
                    capability_profile="commander_review",
                )
                node = next(
                    node
                    for node in ir.faces[0].nodes
                    if node.template_id == FIXED_SELF_ENTRY_COUNTER_TEMPLATE
                )
                self.assertTrue(node.exact, ir.material_residuals)
                self.assertEqual("replacement_effect", node.kind)
                self.assertEqual("zone.change", node.event)
                self.assertEqual("all", node.active_zone)
                self.assertIn(
                    FIXED_SELF_ENTRY_COUNTER_CAPABILITY,
                    node.capability_dependencies,
                )
                self.assertEqual(
                    keyword_counter,
                    "counter.characteristic.keyword"
                    in node.capability_dependencies,
                )
                self.assertEqual(
                    record.oracle_text,
                    record.oracle_text[node.span.start : node.span.end],
                )
                programs = [
                    program
                    for program in generated_programs(
                        self.db,
                        record,
                        trust_level="trusted",
                        capability_registry=self.capabilities,
                        capability_profile="commander_review",
                    )
                    if program.provenance.get("template_id")
                    == FIXED_SELF_ENTRY_COUNTER_TEMPLATE
                ]
                self.assertEqual(1, len(programs))
                self.assertTrue(programs[0].capability_closure["trusted"])

    def test_unsupported_fixed_self_entry_forms_and_dependency_fail_closed(self):
        source = self.db.lookup("Fixed Counter Entrant")
        unsupported = (
            "This creature enters with X +1/+1 counters on it.",
            "This creature enters with zero +1/+1 counters on it.",
            "This creature enters with eleven +1/+1 counters on it.",
            "This creature enters with an additional +1/+1 counter on it.",
            "If you cast this spell, this creature enters with a +1/+1 counter on it.",
            "You may have this creature enter with a +1/+1 counter on it.",
            "Another creature enters with a +1/+1 counter on it.",
            "This creature enters with a +1/+1 counter and a shield counter on it.",
            "This creature enters with two +1/+1 counter on it.",
        )
        for text in unsupported:
            with self.subTest(text=text):
                ir = compile_oracle_card(
                    replace(source, oracle_text=text),
                    capability_registry=self.capabilities,
                    capability_profile="commander_review",
                )
                self.assertFalse(
                    any(
                        node.template_id == FIXED_SELF_ENTRY_COUNTER_TEMPLATE
                        for node in ir.faces[0].nodes
                    )
                )
                self.assertTrue(ir.material_residuals)

        value = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        dependency = next(
            row
            for row in value["capabilities"]
            if row["id"] == "counter.placement.quantity_replacement"
        )
        dependency["status"] = "blocked"
        dependency["blockers"] = ["test mutation"]
        ir = compile_oracle_card(
            source,
            capability_registry=CapabilityRegistry(value),
            capability_profile="commander_review",
        )
        node = next(
            node
            for node in ir.faces[0].nodes
            if node.template_id == FIXED_SELF_ENTRY_COUNTER_TEMPLATE
        )
        self.assertFalse(node.exact)
        self.assertTrue(node.residual_ids)

    def test_fixed_self_entry_compiler_mutation_is_killed(self):
        record = self.db.lookup("Fixed Counter Entrant")
        current = compile_oracle_card(
            record,
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )
        self.assertTrue(
            any(
                node.template_id == FIXED_SELF_ENTRY_COUNTER_TEMPLATE
                for node in current.faces[0].nodes
            )
        )
        with patch(
            "quorune.compiler.runtime_templates."
            "fixed_self_entry_counter_handler",
            return_value=None,
        ):
            mutated = compile_oracle_card(
                record,
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            )
        self.assertFalse(
            any(
                node.template_id == FIXED_SELF_ENTRY_COUNTER_TEMPLATE
                for node in mutated.faces[0].nodes
            )
        )
        self.assertTrue(mutated.material_residuals)


class FixedKeywordEntryRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_database(cls.temporary.name)
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
        cls.capabilities = load_default_capability_registry()

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
        engine.state.pending_trigger_batches.clear()
        engine.state.stack.clear()
        session.commands.clear()
        session.decisions.clear()
        return session

    def add_card(
        self,
        engine,
        *,
        seat: str,
        name: str,
        ref: str,
        zone: str,
        controller: str | None = None,
    ) -> CardInstance:
        record = self.db.lookup(name)
        current_controller = controller or seat
        public = zone in {"battlefield", "graveyard", "exile", "command", "stack"}
        card = CardInstance(
            object_id=f"fixture:{ref}",
            ref=ref,
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner=seat,
            controller=current_controller,
            zone=zone,
            zone_timestamp=engine.state.event_sequence + 1,
            known_to=list(engine.seats) if public else [seat],
            revealed_to=list(engine.seats) if public else [],
        )
        engine.state.cards[card.object_id] = card
        if zone in engine.state.players[seat].zones:
            engine.state.players[seat].zones[zone].append(card.object_id)
        return card

    def register_entry(self, engine, card: CardInstance) -> None:
        programs = [
            program
            for program in generated_programs(
                self.db,
                self.db.by_oracle_id(card.oracle_id),
                trust_level="trusted",
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            )
            if program.provenance.get("template_id") in ALL_ENTRY_TEMPLATE_IDS
        ]
        self.assertEqual(1, len(programs))
        engine.semantics.put(programs[0])

    def begin_entry(self, session, card: CardInstance) -> None:
        item = StackItem(
            stack_id=f"stack:{card.ref}",
            ref=f"S-{card.ref}",
            kind="spell",
            controller=card.controller,
            label=card.printed_name,
            card_object_id=card.object_id,
            default_destination="battlefield",
            visibility=list(session.engine.seats),
        )
        session.engine.state.stack.append(item)
        session.engine._continue_resolution(
            stack_ref=item.ref,
            effects=[],
            destination=None,
            note="Fixed keyword entry fixture",
        )

    @staticmethod
    def replacement_options(session, seat: str) -> tuple[dict, list[str]]:
        decision = StateProjector(session.engine.card_db, session.state)._decision(
            f"pilot:{seat}"
        )
        return decision, [option["id"] for option in decision["ctx"]["options"]]

    def finish_replacements(self, session, seat: str) -> None:
        for _ in range(8):
            decision = session.state.pending_decision
            if decision is None or decision.kind != "replacement.order":
                return
            _projected, options = self.replacement_options(session, seat)
            result = session.act(
                f"pilot:{seat}",
                {
                    "action_id": "choose",
                    "choices": {"replacement": options[0]},
                },
            )
            self.assertTrue(result.ok, result.summary)
        self.fail("Fixed keyword entry replacement ordering did not converge")

    def test_fixed_keyword_entries_use_quantity_replacement(self):
        session = self.session(7025801)
        engine = session.engine
        card = self.add_card(
            engine,
            seat="A",
            name="Fading Entry Fixture",
            ref="fading-replacement",
            zone="stack",
        )
        self.add_card(
            engine,
            seat="A",
            name="Doubling Season",
            ref="doubling-season",
            zone="battlefield",
        )
        self.register_entry(engine, card)
        self.begin_entry(session, card)
        self.finish_replacements(session, "A")
        self.assertEqual("battlefield", card.zone)
        self.assertEqual(10, card.counters.get("fade"))

    def test_four_player_fixed_keyword_entry_is_seat_scoped_and_replays_exactly(self):
        session = self.session(7026301, players=4)
        engine = session.engine
        card = self.add_card(
            engine,
            seat="A",
            controller="C",
            name="Vanishing Entry Fixture",
            ref="controlled-vanishing",
            zone="stack",
        )
        self.add_card(
            engine,
            seat="C",
            name="Doubling Season",
            ref="controlled-vanishing-doubling",
            zone="battlefield",
        )
        self.add_card(
            engine,
            seat="C",
            name="Doc Samson, Super Psychiatrist",
            ref="controlled-vanishing-addition",
            zone="battlefield",
        )
        self.register_entry(engine, card)
        self.begin_entry(session, card)
        for seat in ("A", "B", "D"):
            self.assertIsNone(
                StateProjector(self.db, engine.state)._decision(f"pilot:{seat}")
            )
        projected, _options = self.replacement_options(session, "C")
        self.assertIsNotNone(projected)
        self.assertNotIn(card.object_id, json.dumps(projected, sort_keys=True))

        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        self.finish_replacements(session, "C")
        self.assertEqual("battlefield", card.zone)
        self.assertEqual("C", card.controller)
        self.assertIn(card.counters.get("time"), {7, 8})
        expected_hash = authoritative_state_hash(engine.state)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "fixed-keyword-entry-replay"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_stale_fixed_keyword_entry_choice_aborts_without_card_mutation(self):
        session = self.session(7023201)
        engine = session.engine
        card = self.add_card(
            engine,
            seat="A",
            name="Fading Entry Fixture",
            ref="stale-fading",
            zone="stack",
        )
        self.add_card(
            engine,
            seat="A",
            name="Doubling Season",
            ref="stale-fading-doubling",
            zone="battlefield",
        )
        self.add_card(
            engine,
            seat="A",
            name="Doc Samson, Super Psychiatrist",
            ref="stale-fading-addition",
            zone="battlefield",
        )
        self.register_entry(engine, card)
        self.begin_entry(session, card)
        engine.move_card(card.object_id, "graveyard", log=False)
        before_cards = {
            object_id: (
                current.zone,
                current.logical_object_id,
                current.controller,
                dict(current.counters),
            )
            for object_id, current in engine.state.cards.items()
        }
        result = None
        for _ in range(8):
            if (
                engine.state.pending_decision is None
                or engine.state.pending_decision.kind != "replacement.order"
            ):
                break
            _projected, options = self.replacement_options(session, "A")
            result = session.act(
                "pilot:A",
                {
                    "action_id": "choose",
                    "choices": {"replacement": options[0]},
                },
            )
            if not result.ok:
                break
        self.assertIsNotNone(result)
        self.assertTrue(result.ok, result.summary)
        self.assertEqual(
            before_cards,
            {
                object_id: (
                    current.zone,
                    current.logical_object_id,
                    current.controller,
                    dict(current.counters),
                )
                for object_id, current in engine.state.cards.items()
            },
        )
        self.assertEqual("graveyard", card.zone)
        self.assertFalse(card.counters)

    def test_fixed_keyword_entry_runtime_mutation_is_killed(self):
        def assert_counter(seed: int) -> None:
            session = self.session(seed)
            card = self.add_card(
                session.engine,
                seat="A",
                name="Graft Entry Fixture",
                ref=f"graft-mutant-{seed}",
                zone="stack",
            )
            self.register_entry(session.engine, card)
            self.begin_entry(session, card)
            self.finish_replacements(session, "A")
            self.assertEqual(2, card.counters.get("+1/+1", 0))

        assert_counter(7025802)
        original = zone_replacements._zone_change_snapshot_effects

        def remove_fixed_entry_effects(host, subjects, active_sources):
            return tuple(
                effect
                for effect in original(host, subjects, active_sources)
                if not effect.effect_id.startswith(
                    "replacement.zone.self-entry-counter.v1:"
                )
            )

        with patch(
            "quorune.semantic_runtime.zone_replacements."
            "_zone_change_snapshot_effects",
            side_effect=remove_fixed_entry_effects,
        ):
            with self.assertRaises(AssertionError):
                assert_counter(7025803)

    def test_fixed_self_entry_keyword_counter_uses_shared_characteristics(self):
        session = self.session(6140100)
        engine = session.engine
        card = self.add_card(
            engine,
            seat="A",
            name="Named Counter Entrant",
            ref="fixed-self-entry-keyword",
            zone="stack",
        )
        self.register_entry(engine, card)
        self.begin_entry(session, card)
        self.finish_replacements(session, "A")
        self.assertEqual(1, card.counters.get("deathtouch"))
        self.assertIn("Deathtouch", engine._effective_card_data(card)["keywords"])

    def test_fixed_self_entry_uses_quantity_replacement(self):
        session = self.session(6140101)
        engine = session.engine
        card = self.add_card(
            engine,
            seat="A",
            name="Fixed Counter Entrant",
            ref="fixed-self-entry",
            zone="stack",
        )
        self.add_card(
            engine,
            seat="A",
            name="Doubling Season",
            ref="fixed-self-entry-doubling",
            zone="battlefield",
        )
        self.register_entry(engine, card)
        self.begin_entry(session, card)
        self.finish_replacements(session, "A")
        self.assertEqual("battlefield", card.zone)
        self.assertEqual(6, card.counters.get("+1/+1"))

    def test_four_player_fixed_self_entry_is_private_and_replays_exactly(self):
        session = self.session(6140102, players=4)
        engine = session.engine
        card = self.add_card(
            engine,
            seat="A",
            controller="C",
            name="Fixed Charge Vessel",
            ref="fixed-charge-controlled",
            zone="stack",
        )
        self.add_card(
            engine,
            seat="C",
            name="Doubling Season",
            ref="fixed-charge-doubling",
            zone="battlefield",
        )
        self.add_card(
            engine,
            seat="C",
            name="Doc Samson, Super Psychiatrist",
            ref="fixed-charge-addition",
            zone="battlefield",
        )
        self.register_entry(engine, card)
        self.begin_entry(session, card)
        for seat in ("A", "B", "D"):
            self.assertIsNone(
                StateProjector(self.db, engine.state)._decision(f"pilot:{seat}")
            )
        projected, _options = self.replacement_options(session, "C")
        self.assertIsNotNone(projected)
        self.assertNotIn(card.object_id, json.dumps(projected, sort_keys=True))

        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        self.finish_replacements(session, "C")
        self.assertEqual("battlefield", card.zone)
        self.assertEqual("C", card.controller)
        self.assertIn(card.counters.get("charge"), {7, 8})
        expected_hash = authoritative_state_hash(engine.state)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "fixed-self-entry-replay"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_stale_fixed_self_entry_aborts_without_card_mutation(self):
        session = self.session(6140103)
        engine = session.engine
        card = self.add_card(
            engine,
            seat="A",
            name="Fixed Counter Entrant",
            ref="stale-fixed-self-entry",
            zone="stack",
        )
        self.add_card(
            engine,
            seat="A",
            name="Doubling Season",
            ref="stale-fixed-self-entry-doubling",
            zone="battlefield",
        )
        self.add_card(
            engine,
            seat="A",
            name="Doc Samson, Super Psychiatrist",
            ref="stale-fixed-self-entry-addition",
            zone="battlefield",
        )
        self.register_entry(engine, card)
        self.begin_entry(session, card)
        engine.move_card(card.object_id, "graveyard", log=False)
        before_cards = {
            object_id: (
                current.zone,
                current.logical_object_id,
                current.controller,
                dict(current.counters),
            )
            for object_id, current in engine.state.cards.items()
        }
        result = None
        for _ in range(8):
            decision = engine.state.pending_decision
            if decision is None or decision.kind != "replacement.order":
                break
            _projected, options = self.replacement_options(session, "A")
            result = session.act(
                "pilot:A",
                {
                    "action_id": "choose",
                    "choices": {"replacement": options[0]},
                },
            )
            if not result.ok:
                break
        self.assertIsNotNone(result)
        self.assertTrue(result.ok, result.summary)
        self.assertEqual(
            before_cards,
            {
                object_id: (
                    current.zone,
                    current.logical_object_id,
                    current.controller,
                    dict(current.counters),
                )
                for object_id, current in engine.state.cards.items()
            },
        )
        self.assertEqual("graveyard", card.zone)
        self.assertFalse(card.counters)

    def test_fixed_self_entry_runtime_mutation_is_killed(self):
        def assert_counter(seed: int) -> None:
            session = self.session(seed)
            card = self.add_card(
                session.engine,
                seat="A",
                name="Fixed Counter Entrant",
                ref=f"fixed-self-mutant-{seed}",
                zone="stack",
            )
            self.register_entry(session.engine, card)
            self.begin_entry(session, card)
            self.finish_replacements(session, "A")
            self.assertEqual(3, card.counters.get("+1/+1", 0))

        assert_counter(6140104)
        original = zone_replacements._zone_change_snapshot_effects

        def remove_fixed_entry_effects(host, subjects, active_sources):
            return tuple(
                effect
                for effect in original(host, subjects, active_sources)
                if not effect.effect_id.startswith(
                    "replacement.zone.self-entry-counter.v1:"
                )
            )

        with patch(
            "quorune.semantic_runtime.zone_replacements."
            "_zone_change_snapshot_effects",
            side_effect=remove_fixed_entry_effects,
        ):
            with self.assertRaises(AssertionError):
                assert_counter(6140105)


if __name__ == "__main__":
    unittest.main()
