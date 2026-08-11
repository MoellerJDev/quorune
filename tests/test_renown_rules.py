from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common import ROOT, keep_all, make_session
from quorune.carddb import CardDatabase
from quorune.damage import damage_proposal, resolve_damage_batch
from quorune.damage_prevention import (
    DamageModifierDuration,
    DamagePreventionShield,
    DamageRedirectionEffect,
    DamageSubject,
    PreventionMode,
)
from quorune.deck import DeckLoader
from quorune.errors import GameRuleError
from quorune.model import CardInstance
from quorune.oracle_ir import compile_oracle_card, generated_programs
from quorune.permanent_designations import (
    BecomeRenownedRequest,
    PermanentDesignationError,
    become_renowned,
)
from quorune.projection import StateProjector
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)
from quorune.renown import RenownError, RenownSpec, renown_condition_holds
from quorune.rules.capabilities import (
    CapabilityRegistry,
    load_default_capability_registry,
)
from scripts.build_test_database import build_fixture_database


REGISTRY_PATH = ROOT / "quorune" / "rules" / "capability-registry.json"


def focused_card_database(directory: str) -> CardDatabase:
    database = Path(directory) / "renown.sqlite3"
    build_fixture_database(
        [
            ROOT / "tests" / "fixtures" / "scryfall-exact-lists.json",
            ROOT / "tests" / "fixtures" / "counter-replacement-cards.json",
            ROOT / "tests" / "fixtures" / "renown-cards.json",
            ROOT / "tests" / "fixtures" / "renown-synthetic-cards.json",
        ],
        database,
    )
    return CardDatabase(database)


class RenownCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_card_database(cls.temporary.name)
        cls.record = cls.db.lookup("Topan Freeblade")
        cls.capabilities = load_default_capability_registry()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temporary.cleanup()

    def test_renown_model_and_compiler_are_strict_source_spanned_and_closed(self):
        with self.assertRaises(RenownError):
            RenownSpec(0)
        with self.assertRaises(RenownError):
            RenownSpec(True)

        text = "Renown 1, Renown 2"
        record = replace(
            self.record,
            oracle_text=text,
            keywords=("Renown",),
        )
        ir = compile_oracle_card(
            record,
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )
        nodes = [
            node
            for node in ir.faces[0].nodes
            if node.template_id
            == "renown-combat-damage-counter-designation-v1"
        ]
        self.assertEqual("exact", ir.status)
        self.assertEqual(2, len(nodes))
        self.assertEqual(2, len({node.node_id for node in nodes}))
        self.assertEqual(
            ["renown 1", "renown 2"],
            [text[node.span.start : node.span.end].casefold() for node in nodes],
        )
        self.assertEqual([1, 2], [node.effects[0]["amount"] for node in nodes])
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
            == "renown-combat-damage-counter-designation-v1"
        ]
        self.assertEqual(2, len({program.key for program in programs}))
        for node in nodes:
            self.assertTrue(node.exact)
            self.assertEqual("damage.dealt.self", node.event)
            self.assertEqual(node.event, node.handlers[0]["event"])
            self.assertEqual(
                {
                    "field": "renown_combat_damage_player_unrenowned",
                    "op": "truthy",
                },
                node.event_condition,
            )
            self.assertIn("intervening_condition", node.runtime_coverage)
            self.assertEqual(
                ("counter.producer.renown",),
                node.capability_dependencies,
            )

    def test_unsupported_renown_values_remain_material_residuals(self):
        for text in ("Renown 0", "Renown X", "Renown — Whenever this attacks"):
            with self.subTest(text=text):
                ir = compile_oracle_card(
                    replace(
                        self.record,
                        oracle_text=text,
                        keywords=("Renown",),
                    ),
                    capability_registry=self.capabilities,
                    capability_profile="commander_review",
                )
                self.assertNotEqual("exact", ir.status)
                self.assertTrue(ir.material_residuals)

    def test_renown_dependencies_and_compiler_mutation_fail_closed(self):
        value = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        dependency = next(
            row
            for row in value["capabilities"]
            if row["id"] == "permanent.designation.renowned"
        )
        dependency["status"] = "blocked"
        dependency["blockers"] = ["test mutation"]
        ir = compile_oracle_card(
            self.record,
            capability_registry=CapabilityRegistry(value),
            capability_profile="commander_review",
        )
        self.assertNotEqual("exact", ir.status)
        self.assertTrue(
            any(
                "permanent.designation.renowned" in blocker
                for residual in ir.material_residuals
                for blocker in residual.blockers
            )
        )

        with patch(
            "quorune.compiler.keyword_nodes.renown_keyword_node",
            return_value=None,
        ):
            ir = compile_oracle_card(
                self.record,
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            )
        self.assertFalse(
            any(
                node.template_id
                == "renown-combat-damage-counter-designation-v1"
                for node in ir.faces[0].nodes
            )
        )


class RenownRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_card_database(cls.temporary.name)
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
        zone: str = "battlefield",
    ) -> CardInstance:
        record = self.db.lookup(name)
        visible = list(engine.seats) if zone == "battlefield" else [seat]
        card = CardInstance(
            object_id=f"fixture:{ref}",
            ref=ref,
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner=seat,
            controller=seat,
            zone=zone,
            zone_timestamp=engine.state.event_sequence + 1,
            known_to=visible,
            revealed_to=visible if zone == "battlefield" else [],
        )
        engine.state.cards[card.object_id] = card
        engine.state.players[seat].zones[zone].append(card.object_id)
        return card

    def register_renown(
        self,
        engine,
        source: CardInstance,
        *,
        expected_instances: int = 1,
    ):
        record = self.db.by_oracle_id(source.oracle_id)
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
            == "renown-combat-damage-counter-designation-v1"
        ]
        self.assertEqual(expected_instances, len(programs))
        for program in programs:
            engine.semantics.put(program)
        return programs

    @staticmethod
    def resolve_top(engine):
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine._prepare_stack_resolution()

    def deal(
        self,
        engine,
        source: CardInstance,
        target,
        *,
        combat: bool,
        amount: int = 1,
        suffix: str = "ordinary",
    ):
        result = resolve_damage_batch(
            engine,
            (
                damage_proposal(
                    engine,
                    proposal_id=f"renown:{suffix}",
                    actor=source.controller,
                    source_ref=source.ref,
                    target=target.ref if hasattr(target, "ref") else target,
                    amount=amount,
                    combat=combat,
                    reason="Renown rules witness",
                ),
            ),
        )
        engine._stabilize()
        return result

    def test_combat_damage_to_player_triggers_counter_and_designation(self):
        engine = self.session(70211201).engine
        source = self.add_card(
            engine, seat="A", name="Citadel Castellan", ref="renown-source"
        )
        program = self.register_renown(engine, source)[0]

        self.deal(engine, source, "B", combat=True, suffix="player")

        self.assertEqual(program.key, engine.state.stack[-1].semantic_key)
        self.resolve_top(engine)
        self.assertEqual(2, source.counters["+1/+1"])
        self.assertTrue(source.renowned)
        self.assertTrue(
            any(event.code == "permanent.renowned" for event in engine.state.events)
        )

    def test_redirected_combat_damage_to_controller_still_triggers(self):
        engine = self.session(70211202).engine
        source = self.add_card(
            engine,
            seat="A",
            name="Topan Freeblade",
            ref="redirected-renown-source",
        )
        program = self.register_renown(engine, source)[0]
        engine.state.damage_redirections.append(
            DamageRedirectionEffect(
                redirection_id="renown-to-controller",
                source_id="fixture:renown-redirection",
                controller="B",
                subject=DamageSubject("B", "player", "B"),
                destination=DamageSubject("A", "player", "A"),
                duration=DamageModifierDuration.UNTIL_END_OF_TURN,
                created_turn_sequence=engine.state.turn_sequence,
                label="Redirect Renown damage to its controller",
            )
        )

        result = self.deal(
            engine,
            source,
            "B",
            combat=True,
            suffix="redirected-controller",
        )

        self.assertEqual("A", result.events[0].target)
        self.assertEqual(39, engine.state.players["A"].life)
        self.assertEqual(40, engine.state.players["B"].life)
        self.assertEqual(program.key, engine.state.stack[-1].semantic_key)
        self.resolve_top(engine)
        self.assertEqual(1, source.counters["+1/+1"])
        self.assertTrue(source.renowned)

    def test_noncombat_permanent_prevented_and_already_renowned_do_not_trigger(self):
        cases = ("noncombat", "permanent", "prevented", "renowned")
        for index, case in enumerate(cases):
            with self.subTest(case=case):
                engine = self.session(70211210 + index).engine
                source = self.add_card(
                    engine,
                    seat="A",
                    name="Topan Freeblade",
                    ref=f"source-{case}",
                )
                target = self.add_card(
                    engine,
                    seat="B",
                    name="Citadel Castellan",
                    ref=f"target-{case}",
                )
                self.register_renown(engine, source)
                if case == "prevented":
                    engine.state.damage_prevention_shields.append(
                        DamagePreventionShield(
                            shield_id="renown-prevention",
                            source_id="fixture:prevention",
                            controller="B",
                            subject=DamageSubject(
                                ref="B",
                                kind="player",
                                controller="B",
                            ),
                            mode=PreventionMode.AMOUNT,
                            remaining=1,
                            duration=DamageModifierDuration.UNTIL_END_OF_TURN,
                            created_turn_sequence=engine.state.turn_sequence,
                            label="Renown prevention fixture",
                        )
                    )
                if case == "renowned":
                    source.renowned = True
                self.deal(
                    engine,
                    source,
                    target if case == "permanent" else "B",
                    combat=case != "noncombat",
                    suffix=case,
                )
                self.assertEqual([], engine.state.stack)
                self.assertEqual({}, source.counters)

    def test_intervening_condition_uses_same_logical_object_and_current_designation(self):
        for index, mutation in enumerate(("designation", "zone", "phasing")):
            with self.subTest(mutation=mutation):
                engine = self.session(70211220 + index).engine
                source = self.add_card(
                    engine,
                    seat="A",
                    name="Topan Freeblade",
                    ref=f"condition-{mutation}",
                )
                self.register_renown(engine, source)
                self.deal(engine, source, "B", combat=True, suffix=mutation)
                self.assertTrue(engine.state.stack)
                if mutation == "designation":
                    source.renowned = True
                elif mutation == "zone":
                    engine.move_card(source.object_id, "exile", log=False)
                    engine.move_card(
                        source.object_id,
                        "battlefield",
                        controller="A",
                        log=False,
                    )
                else:
                    source.phased_out = True
                self.resolve_top(engine)
                self.assertEqual({}, source.counters)

    def test_trigger_uses_frozen_controller_and_current_source_after_control_change(self):
        engine = self.session(70211223).engine
        source = self.add_card(
            engine,
            seat="A",
            name="Topan Freeblade",
            ref="renown-control-change",
        )
        program = self.register_renown(engine, source)[0]
        self.deal(engine, source, "B", combat=True, suffix="control-change")
        self.assertEqual("A", engine.state.stack[-1].controller)

        engine.change_control(source.object_id, "B", reason="Renown fixture")
        self.assertEqual("B", source.controller)
        self.assertEqual(program.key, engine.state.stack[-1].semantic_key)
        self.resolve_top(engine)

        self.assertEqual(1, source.counters["+1/+1"])
        self.assertTrue(source.renowned)

    def test_multiple_renown_instances_only_first_resolution_changes_object(self):
        session = self.session(70211230)
        engine = session.engine
        source = self.add_card(
            engine,
            seat="A",
            name="Renown Twin Fixture",
            ref="double-renown",
        )
        self.register_renown(engine, source, expected_instances=2)
        self.deal(engine, source, "B", combat=True, suffix="double")
        self.assertEqual("trigger.order", engine.state.pending_decision.kind)
        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        refs = [item.ref for item in engine.state.pending_trigger_batches[0].items]
        result = session.act("pilot:A", {"action_id": "order", "triggers": refs})
        self.assertTrue(result.ok, result.summary)

        for _ in range(12):
            if (
                source.renowned
                and not engine.state.stack
                and not engine.state.pending_trigger_batches
            ):
                break
            principals = session.pending_principals()
            self.assertTrue(principals)
            result = session.act(principals[0], {"action_id": "pass"})
            self.assertTrue(result.ok, result.summary)

        self.assertEqual(1, source.counters["+1/+1"])
        self.assertTrue(source.renowned)
        self.assertEqual(
            1,
            sum(event.code == "permanent.renowned" for event in engine.state.events),
        )
        expected_hash = authoritative_state_hash(engine.state)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "multiple-renown-replay"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_counter_replacement_and_zero_result_still_create_renowned_designation(self):
        engine = self.session(70211240).engine
        source = self.add_card(
            engine,
            seat="A",
            name="Topan Freeblade",
            ref="zero-counter-renown",
        )
        self.register_renown(engine, source)
        self.deal(engine, source, "B", combat=True, suffix="zero")
        with patch.object(engine, "place_counters_intent", return_value=[]):
            self.resolve_top(engine)
        self.assertEqual({}, source.counters)
        self.assertTrue(source.renowned)

    def test_renown_designation_failure_rolls_back_counter_placement(self):
        session = self.session(70211241)
        engine = session.engine
        source = self.add_card(
            engine,
            seat="A",
            name="Topan Freeblade",
            ref="renown-rollback",
        )
        self.register_renown(engine, source)
        self.deal(engine, source, "B", combat=True, suffix="rollback")

        with patch(
            "quorune.semantic_choices.intent_host.become_renowned",
            side_effect=PermanentDesignationError("designation mutation"),
        ):
            with self.assertRaises(GameRuleError):
                with engine.transaction():
                    engine._prepare_stack_resolution()

        current = session.state.cards[source.object_id]
        self.assertEqual({}, current.counters)
        self.assertFalse(current.renowned)

    def designation_request(self, card: CardInstance) -> BecomeRenownedRequest:
        return BecomeRenownedRequest(
            object_id=card.object_id,
            object_ref=card.ref,
            logical_object_id=card.logical_object_id,
            actor=card.controller,
            reason="Renown designation witness",
        )

    def test_renowned_designation_survives_control_change_and_phasing(self):
        engine = self.session(70211250).engine
        source = self.add_card(
            engine,
            seat="A",
            name="Topan Freeblade",
            ref="designation-source",
        )
        result = become_renowned(engine, self.designation_request(source))
        self.assertTrue(result.changed)
        engine.change_control(source.object_id, "B", reason="Renown fixture")
        source.phased_out = True
        source.phased_out = False
        self.assertTrue(source.renowned)
        copied = engine.create_card_copy("B", source.ref, zone="battlefield")
        self.assertFalse(copied.renowned)
        projected = StateProjector(self.db, engine.state)._snapshot("pilot:A")
        card = next(
            row
            for player in projected["players"].values()
            for row in player["bf"]
            if row["id"] == source.ref
        )
        self.assertTrue(card["renowned"])

    def test_renowned_designation_is_strict_identity_pinned_and_zone_scoped(self):
        engine = self.session(70211251).engine
        source = self.add_card(
            engine,
            seat="A",
            name="Topan Freeblade",
            ref="designation-strict",
        )
        with self.assertRaises(PermanentDesignationError):
            become_renowned(engine, object())
        stale = replace(
            self.designation_request(source),
            logical_object_id="stale@99",
        )
        self.assertFalse(become_renowned(engine, stale).changed)
        self.assertFalse(source.renowned)

        become_renowned(engine, self.designation_request(source))
        historical = CardInstance.from_dict(source.to_dict())
        self.assertTrue(historical.renowned)
        engine.move_card(source.object_id, "graveyard", log=False)
        self.assertFalse(source.renowned)
        self.assertNotIn("renowned", source.to_dict())

    def test_four_player_renown_trigger_is_public_and_replay_exact(self):
        session = self.session(70211260, players=4)
        engine = session.engine
        source = self.add_card(
            engine,
            seat="A",
            name="Topan Freeblade",
            ref="replay-renown",
        )
        hidden = self.add_card(
            engine,
            seat="B",
            name="Citadel Castellan",
            ref="private-renown-card",
            zone="hand",
        )
        self.register_renown(engine, source)
        self.deal(engine, source, "B", combat=True, suffix="replay")
        engine.state.active_player = "A"
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine._grant_priority("A")
        engine._issue_priority("A")
        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()

        for seat in engine.seats:
            result = session.act(f"pilot:{seat}", {"action_id": "pass"})
            self.assertTrue(result.ok, result.summary)

        self.assertTrue(source.renowned)
        expected_hash = authoritative_state_hash(engine.state)
        projected_a = json.dumps(
            StateProjector(self.db, engine.state)._snapshot("pilot:A"),
            sort_keys=True,
        )
        self.assertNotIn(hidden.ref, projected_a)
        self.assertIn(source.ref, projected_a)
        self.assertIn('"renowned": true', projected_a)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "renown-replay"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_renowned_designation_runtime_mutant_is_killed(self):
        engine = self.session(70211270).engine
        source = self.add_card(
            engine,
            seat="A",
            name="Topan Freeblade",
            ref="designation-mutant",
        )
        request = self.designation_request(source)
        def assert_designated() -> None:
            source.renowned = False
            become_renowned(engine, request)
            self.assertTrue(source.renowned)

        assert_designated()
        with patch(
            "quorune.permanent_designations.become_renowned",
            return_value=None,
        ):
            with self.assertRaises(AssertionError):
                source.renowned = False
                from quorune import permanent_designations

                permanent_designations.become_renowned(engine, request)
                self.assertTrue(source.renowned)

    def test_renown_condition_rejects_malformed_normalized_damage(self):
        source = CardInstance(
            object_id="fixture:condition",
            ref="condition",
            oracle_id="fixture",
            printed_name="Condition",
            owner="A",
            controller="A",
            zone="battlefield",
        )
        valid = {
            "source": source.ref,
            "source_object_id": source.object_id,
            "source_logical_object_id": source.logical_object_id,
            "source_types": ["creature"],
            "target_kind": "player",
            "combat": True,
            "amount": 1,
        }
        self.assertTrue(renown_condition_holds(source, valid))
        for field, value in (
            ("combat", 1),
            ("amount", True),
            ("source_types", "creature"),
            ("source_object_id", ""),
        ):
            with self.subTest(field=field):
                with self.assertRaises(RenownError):
                    renown_condition_holds(source, {**valid, field: value})


if __name__ == "__main__":
    unittest.main()
