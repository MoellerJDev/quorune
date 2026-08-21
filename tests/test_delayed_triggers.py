from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common import (
    ROOT,
    advance_fixture_turn,
    keep_all,
    make_session,
    pass_current,
    set_fixture_turn,
)
from quorune.card_programs import bind_card_program_runtime
from quorune.card_programs.adapters import (
    compile_best_available_card_program,
)
from quorune.carddb import CardDatabase
from quorune.compiler.delayed_draw_templates import (
    FIXED_NEXT_TURN_DRAW_CAPABILITY,
    FIXED_NEXT_TURN_DRAW_MECHANIC,
    FIXED_NEXT_TURN_DRAW_TEMPLATE,
    fixed_next_turn_upkeep_draw_effect,
    fixed_next_turn_upkeep_draw_effect_template,
)
from quorune.compiler.program_generation import register_generated_programs
from quorune.deck import DeckLoader
from quorune.delayed_triggers import materialize_delayed_trigger
from quorune.engine import TURN_STEPS
from quorune.model import CardInstance, DelayedTrigger
from quorune.oracle_ir import compile_oracle_card, generated_programs
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)
from quorune.rules.capabilities import (
    CapabilityRegistry,
    load_default_capability_registry,
)
from quorune.rules.delayed_draw_capability_shapes import (
    fixed_next_turn_draw_node_capabilities,
)
from quorune.semantics import SemanticRegistry
from scripts.build_test_database import build_fixture_database


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "fixed-next-turn-draw-cards.json"
REGISTRY_PATH = ROOT / "quorune" / "rules" / "capability-registry.json"


def focused_database(directory: str, *, runtime: bool = False) -> CardDatabase:
    path = Path(directory) / "fixed-next-turn-draw.sqlite3"
    fixtures = [FIXTURE_PATH]
    if runtime:
        fixtures.insert(0, ROOT / "tests" / "fixtures" / "scryfall-exact-lists.json")
    build_fixture_database(fixtures, path)
    return CardDatabase(path)


class DelayedTriggerMaterializationTests(unittest.TestCase):
    def test_materialization_preserves_typed_referred_object_provenance(self):
        trigger = DelayedTrigger(
            trigger_id="delayed-1",
            ref="DT1",
            controller="A",
            label="Delayed effect",
            source_object_id="source-object",
            event_kind="phase.begin",
            condition={"phase": "ending"},
            stack_template={
                "label": "Materialized effect",
                "semantic_key": "program:delayed",
                "targets": ["B"],
                "context": {"nested": {"value": 1}},
            },
            referred_object_ids=["former-zone-object"],
        )

        item = materialize_delayed_trigger(
            trigger,
            ref="S1",
            stack_id="stack-1",
            visibility=("A", "B"),
        )

        self.assertEqual(["former-zone-object"], item.referred_object_ids)
        self.assertEqual("DT1", item.context["delayed_trigger_ref"])
        self.assertEqual(["A", "B"], item.visibility)
        self.assertEqual("Materialized effect", item.label)

        trigger.stack_template["context"]["nested"]["value"] = 2
        self.assertEqual(1, item.context["nested"]["value"])

    def test_materialization_keeps_historical_empty_provenance_shape(self):
        trigger = DelayedTrigger(
            trigger_id="delayed-2",
            ref="DT2",
            controller="A",
            label="Historical trigger",
            source_object_id=None,
            event_kind="turn.begin",
            condition={},
            stack_template={},
        )

        item = materialize_delayed_trigger(
            trigger,
            ref="S2",
            stack_id="stack-2",
            visibility=("A",),
        )

        self.assertEqual([], item.referred_object_ids)
        self.assertNotIn("referred_object_ids", item.to_dict())


class FixedNextTurnDrawCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_database(cls.temporary.name)
        cls.capabilities = load_default_capability_registry()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temporary.cleanup()

    def test_fixed_next_turn_draw_template_is_exact_shape(self):
        template = fixed_next_turn_upkeep_draw_effect_template(
            "Draw a card at the beginning of the next turn's upkeep."
        )
        self.assertIsNotNone(template)
        assert template is not None
        template_id, effects, target_schema, mechanics = template.compiled()

        self.assertEqual(FIXED_NEXT_TURN_DRAW_TEMPLATE, template_id)
        self.assertEqual((fixed_next_turn_upkeep_draw_effect(),), effects)
        self.assertEqual(
            "$turn_sequence",
            effects[0]["condition"]["next_turn_after_sequence"],
        )
        self.assertNotIn(
            "after_turn_sequence",
            effects[0]["condition"],
        )
        self.assertIsNone(target_schema)
        self.assertIn(FIXED_NEXT_TURN_DRAW_MECHANIC, mechanics)
        self.assertEqual(
            {
                FIXED_NEXT_TURN_DRAW_CAPABILITY,
                "trigger.placement.apnap",
                "zone.draw.library_to_hand",
            },
            set(
                fixed_next_turn_draw_node_capabilities(
                    effects=effects,
                    target_schema=target_schema,
                    mechanic_ids=mechanics,
                )
            ),
        )

    def test_real_next_turn_draw_family_compiles_and_closes_complete_cards(self):
        records = list(self.db.iter_cards(commander_legal_only=True))
        self.assertTrue(records)
        for record in records:
            with self.subTest(card=record.name):
                ir = compile_oracle_card(
                    record,
                    capability_registry=self.capabilities,
                    capability_profile="commander_review",
                )
                nodes = [
                    node
                    for face in ir.faces
                    for node in face.nodes
                    if node.template_id == FIXED_NEXT_TURN_DRAW_TEMPLATE
                ]
                self.assertEqual(1, len(nodes))
                node = nodes[0]
                self.assertTrue(node.exact, ir.material_residuals)
                common_dependencies = {
                    FIXED_NEXT_TURN_DRAW_CAPABILITY,
                    "trigger.placement.apnap",
                    "zone.draw.library_to_hand",
                }
                dependencies = set(node.capability_dependencies)
                self.assertTrue(common_dependencies.issubset(dependencies))
                self.assertEqual(
                    (
                        {"trigger.event.normalized_zone_change"}
                        if node.kind == "triggered_ability"
                        else set()
                    ),
                    dependencies - common_dependencies,
                )
                self.assertIn(
                    "next turn's upkeep",
                    record.oracle_text[node.span.start : node.span.end].casefold(),
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
                    == FIXED_NEXT_TURN_DRAW_TEMPLATE
                    or any(
                        component.get("template_id")
                        == FIXED_NEXT_TURN_DRAW_TEMPLATE
                        for component in program.provenance.get("components", ())
                    )
                ]
                self.assertLessEqual(len(programs), 1)
                if ir.status == "exact":
                    self.assertEqual(1, len(programs))
                self.assertTrue(
                    all(
                        program.capability_closure["trusted"]
                        for program in programs
                    )
                )

        complete = compile_best_available_card_program(
            self.db,
            self.db.lookup("Blessed Wine"),
            semantic_registry=SemanticRegistry(),
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )
        self.assertEqual((), complete.residuals)
        self.assertEqual(
            "capability_closed",
            complete.trust_closure["trust_basis"],
        )

    def test_adjacent_delayed_draw_grammar_remains_residual(self):
        base = self.db.lookup("Blessed Wine")
        variants = (
            "Draw two cards at the beginning of the next turn's upkeep.",
            "You may draw a card at the beginning of the next turn's upkeep.",
            "Draw a card at the beginning of your next upkeep.",
            "Draw a card at the beginning of the next end step.",
            "Draw a card at the beginning of the next turn's upkeep, then lose 1 life.",
        )
        for index, text in enumerate(variants, start=1):
            with self.subTest(text=text):
                self.assertIsNone(
                    fixed_next_turn_upkeep_draw_effect_template(text)
                )
                ir = compile_oracle_card(
                    replace(
                        base,
                        oracle_id=f"60370000-0000-4000-8000-{index:012d}",
                        oracle_text=text,
                    ),
                    capability_registry=self.capabilities,
                    capability_profile="commander_review",
                )
                self.assertTrue(ir.material_residuals)
                self.assertFalse(
                    any(
                        node.template_id == FIXED_NEXT_TURN_DRAW_TEMPLATE
                        for face in ir.faces
                        for node in face.nodes
                    )
                )

    def test_blocked_delayed_draw_dependencies_and_compiler_mutation_fail_closed(
        self,
    ):
        record = self.db.lookup("Blessed Wine")
        for dependency_id in (
            "trigger.placement.apnap",
            "zone.draw.library_to_hand",
        ):
            with self.subTest(dependency=dependency_id):
                value = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
                dependency = next(
                    row
                    for row in value["capabilities"]
                    if row["id"] == dependency_id
                )
                dependency["status"] = "blocked"
                dependency["blockers"] = ["focused test mutation"]
                registry = CapabilityRegistry(value)
                registry.mark_evidence_verified("0" * 64)
                ir = compile_oracle_card(
                    record,
                    capability_registry=registry,
                    capability_profile="commander_review",
                )
                self.assertNotEqual("exact", ir.status)
                self.assertTrue(
                    any(
                        dependency_id in blocker
                        for residual in ir.material_residuals
                        for blocker in residual.blockers
                    )
                )

        with patch(
            "quorune.oracle_ir.fixed_next_turn_upkeep_draw_effect_template",
            return_value=None,
        ):
            mutated = compile_oracle_card(
                record,
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            )
        self.assertNotEqual("exact", mutated.status)
        self.assertTrue(mutated.material_residuals)


class FixedNextTurnDrawRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_database(cls.temporary.name, runtime=True)
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

    def session(self, seed: int):
        session = make_session(
            self.db,
            self.mishra,
            self.zimone,
            players=4,
            seed=seed,
            auto_pass_empty=False,
        )
        keep_all(session)
        engine = session.engine
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.pending_trigger_batches.clear()
        engine.state.stack.clear()
        engine.state.priority_player = None
        engine.state.priority_passes = []
        session.commands.clear()
        session.decisions.clear()
        return session

    def register(self, engine, *names: str) -> None:
        selected = names or ("Blessed Wine",)
        register_generated_programs(
            self.db,
            engine.semantics,
            tuple(self.db.lookup(name) for name in selected),
            trust_level="provisional",
            capability_registry=self.capabilities,
            capability_profile=engine.state.config.review_profile,
            promote_exact_runtime_handlers=True,
            promote_exact_trigger_programs=True,
            promote_exact_effect_programs=True,
            promote_exact_capability_declarations=True,
        )

    def stage_spell(self, engine) -> CardInstance:
        record = self.db.lookup("Blessed Wine")
        spell = CardInstance(
            object_id=f"fixture:blessed-wine:{engine.state.config.seed}",
            ref=f"blessed-wine-{engine.state.config.seed}",
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner="A",
            controller="A",
            zone="hand",
            known_to=["A"],
        )
        engine.state.cards[spell.object_id] = spell
        engine.state.players["A"].zones["hand"].append(spell.object_id)
        return spell

    def test_partial_enchant_card_keeps_cardprogram_admission_fail_closed(self):
        session = self.session(6037003)
        engine = session.engine
        self.register(engine, "Krovikan Plague")
        record = self.db.lookup("Krovikan Plague")
        program = compile_best_available_card_program(
            self.db,
            record,
            semantic_registry=engine.semantics,
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )
        self.assertEqual("unresolved", program.trust_closure["trust_basis"])
        self.assertTrue(program.residuals)
        binding = bind_card_program_runtime(
            program,
            capability_registry=self.capabilities,
            profile="commander_review",
        )
        self.assertFalse(binding["strict_capability_ready"])
        self.assertFalse(binding["compatible_ready"])
        self.assertIn("trust_basis:unresolved", binding["blockers"])
        self.assertFalse(engine.state.delayed_triggers)

    @staticmethod
    def resolve_top(engine) -> None:
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.state.priority_passes = []
        engine._prepare_stack_resolution()

    def cast_and_schedule(self, session):
        engine = session.engine
        self.register(engine)
        spell = self.stage_spell(engine)
        set_fixture_turn(engine, 10)
        engine.state.active_player = "A"
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine.state.phase_index = TURN_STEPS.index(
            ("precombat_main", "main")
        )
        engine.state.priority_player = "A"
        engine.state.players["A"].mana_pool.update({"C": 1, "W": 1})
        engine._cast(
            "A",
            {
                "card": spell.ref,
                "pay": "manual",
                "payment": {"C": 1, "W": 1},
            },
        )
        self.resolve_top(engine)
        trigger = next(
            trigger
            for trigger in engine.state.delayed_triggers
            if trigger.label
            == "Draw at the beginning of the next turn's upkeep"
        )
        return spell, trigger

    def test_next_turn_draw_waits_and_resolves_through_apnap_draw_owner(self):
        session = self.session(6037001)
        engine = session.engine
        life_before = engine.state.players["A"].life
        _spell, trigger = self.cast_and_schedule(session)
        hand_before = len(engine.state.players["A"].zones["hand"])
        created_turn = engine.state.turn_sequence
        competing = engine.schedule_delayed_trigger(
            controller="B",
            label="Competing active-player upkeep trigger",
            event_kind="step.begin",
            condition={
                "phase": "beginning",
                "step": "upkeep",
                "after_turn_sequence": created_turn,
            },
            stack_template={"label": "Competing active-player upkeep trigger"},
        )

        same_turn = engine._matching_delayed_triggers(
            "step.begin",
            {"phase": "beginning", "step": "upkeep", "player": "A"},
        )
        self.assertEqual([], same_turn)
        self.assertTrue(trigger.active)
        self.assertTrue(competing.active)
        self.assertEqual(life_before + 1, engine.state.players["A"].life)

        advance_fixture_turn(engine)
        engine.state.active_player = "B"
        matches = engine._matching_delayed_triggers(
            "step.begin",
            {"phase": "beginning", "step": "upkeep", "player": "B"},
        )
        engine._start_trigger_batch(matches, after="grant_priority")
        self.assertEqual(
            ["B", "A"],
            [item.controller for item in engine.state.stack[-2:]],
        )
        self.assertEqual(
            "Draw at the beginning of the next turn's upkeep",
            engine.state.stack[-1].label,
        )

        self.resolve_top(engine)
        self.assertEqual(
            hand_before + 1,
            len(engine.state.players["A"].zones["hand"]),
        )
        self.assertFalse(trigger.active)

    def test_four_player_next_turn_draw_is_private_and_replays_exactly(self):
        session = self.session(6037002)
        engine = session.engine
        _spell, trigger = self.cast_and_schedule(session)
        advance_fixture_turn(engine)
        engine.state.active_player = "B"
        matches = engine._matching_delayed_triggers(
            "step.begin",
            {"phase": "beginning", "step": "upkeep", "player": "B"},
        )
        engine._start_trigger_batch(matches, after="grant_priority")
        engine.pump()
        top_id = engine.state.players["A"].zones["library"][-1]
        top = engine.state.cards[top_id]
        hand_before = len(engine.state.players["A"].zones["hand"])
        for seat in "BCD":
            self.assertNotIn(
                top.ref,
                json.dumps(session.packet(f"pilot:{seat}", full=True)),
            )

        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        for _ in range(8):
            if not engine.state.stack:
                break
            pass_current(session)
        self.assertFalse(engine.state.stack)
        self.assertEqual(
            hand_before + 1,
            len(engine.state.players["A"].zones["hand"]),
        )
        self.assertFalse(trigger.active)
        for seat in "BCD":
            self.assertNotIn(
                top.ref,
                json.dumps(session.packet(f"pilot:{seat}", full=True)),
            )

        expected_hash = authoritative_state_hash(engine.state)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "fixed-next-turn-draw-record"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_next_turn_draw_expires_when_that_turn_has_no_upkeep(self):
        session = self.session(6037003)
        engine = session.engine
        _spell, trigger = self.cast_and_schedule(session)
        hand_before = len(engine.state.players["A"].zones["hand"])

        advance_fixture_turn(engine, 2)
        engine.state.active_player = "C"
        matches = engine._matching_delayed_triggers(
            "step.begin",
            {"phase": "beginning", "step": "upkeep", "player": "C"},
        )

        self.assertEqual([], matches)
        self.assertFalse(trigger.active)
        self.assertEqual(
            hand_before,
            len(engine.state.players["A"].zones["hand"]),
        )
        self.assertFalse(
            any(
                item.label
                == "Draw at the beginning of the next turn's upkeep"
                for item in engine.state.stack
            )
        )


if __name__ == "__main__":
    unittest.main()
