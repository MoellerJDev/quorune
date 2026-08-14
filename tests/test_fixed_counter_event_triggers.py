from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common import ROOT, keep_all, make_session
from quorune.carddb import CardDatabase
from quorune.compiler.fixed_counter_trigger_nodes import (
    FIXED_COUNTER_EVENT_TRIGGER_MECHANIC,
    FixedCounterTriggerBinding,
    FixedCounterTriggerEvent,
    fixed_counter_trigger_binding,
)
from quorune.compiler.target_effect_corpus_assurance import (
    TargetEffectCorpusCollector,
)
from quorune.deck import DeckLoader
from quorune.model import CardInstance
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
from quorune.trigger_processing import collect_trigger_items, enqueue_trigger_batch
from scripts.build_test_database import build_fixture_database


REGISTRY_PATH = ROOT / "quorune" / "rules" / "capability-registry.json"
TEMPLATE_IDS = {
    "fixed-counter-step-trigger-v1",
    "fixed-counter-controlled-land-entry-trigger-v1",
    "fixed-counter-controller-spell-cast-trigger-v1",
}


def focused_database(directory: str) -> CardDatabase:
    database = Path(directory) / "fixed-counter-event-triggers.sqlite3"
    build_fixture_database(
        [
            ROOT / "tests" / "fixtures" / "scryfall-exact-lists.json",
            ROOT / "tests" / "fixtures" / "counter-replacement-cards.json",
            ROOT
            / "tests"
            / "fixtures"
            / "fixed-counter-event-trigger-cards.json",
        ],
        database,
    )
    return CardDatabase(database)


class FixedCounterEventTriggerCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_database(cls.temporary.name)
        cls.capabilities = load_default_capability_registry()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temporary.cleanup()

    def compile(self, text: str, *, type_line: str = "Artifact"):
        return compile_oracle_card(
            replace(
                self.db.lookup("Scheduled Counter Trigger Fixture"),
                name="Compiler Fixture",
                oracle_text=text,
                type_line=type_line,
                keywords=(),
                faces=(),
            ),
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )

    def test_closed_event_bindings_compile_exact_counter_effect_bodies(self):
        expected = (
            (
                "At the beginning of your upkeep, put two charge counters on this artifact.",
                "Artifact",
                FixedCounterTriggerEvent.STEP_BEGIN,
                "your upkeep",
                "fixed-counter-step-trigger-v1",
                "charge",
                2,
                (),
            ),
            (
                "At the beginning of each end step, put a charge counter on this artifact.",
                "Artifact",
                FixedCounterTriggerEvent.STEP_BEGIN,
                "each end step",
                "fixed-counter-step-trigger-v1",
                "charge",
                1,
                (),
            ),
            (
                "Landfall — Whenever a land you control enters, put a +1/+1 counter on this creature.",
                "Creature — Elemental",
                FixedCounterTriggerEvent.CONTROLLED_LAND_ENTER,
                "controlled_land",
                "fixed-counter-controlled-land-entry-trigger-v1",
                "+1/+1",
                1,
                ("trigger-event-normalized-zone-change",),
            ),
            (
                "Landfall — Whenever a land you control enters, put two +1/+1 counters on target creature you control. It gains vigilance until end of turn.",
                "Creature — Elf Soldier",
                FixedCounterTriggerEvent.CONTROLLED_LAND_ENTER,
                "controlled_land",
                "fixed-counter-controlled-land-entry-trigger-v1",
                "+1/+1",
                2,
                ("trigger-event-normalized-zone-change",),
            ),
            (
                "Whenever you cast a noncreature spell, put a +1/+1 counter on this creature.",
                "Creature — Artificer",
                FixedCounterTriggerEvent.CONTROLLER_SPELL_CAST,
                "noncreature",
                "fixed-counter-controller-spell-cast-trigger-v1",
                "+1/+1",
                1,
                ("trigger-event-normalized-spell-cast",),
            ),
            (
                "Whenever you cast an instant or sorcery spell, put a charge counter on this artifact.",
                "Artifact",
                FixedCounterTriggerEvent.CONTROLLER_SPELL_CAST,
                "instant_or_sorcery",
                "fixed-counter-controller-spell-cast-trigger-v1",
                "charge",
                1,
                ("trigger-event-normalized-spell-cast",),
            ),
        )
        for (
            text,
            type_line,
            event,
            variant,
            template_id,
            counter_name,
            amount,
            event_mechanics,
        ) in expected:
            with self.subTest(text=text):
                binding = fixed_counter_trigger_binding(text)
                self.assertIsNotNone(binding)
                assert binding is not None
                self.assertEqual(event, binding.event)
                self.assertEqual(variant, binding.variant)
                self.assertEqual(template_id, binding.template_id)
                self.assertEqual(event_mechanics, binding.event_mechanics)
                with self.assertRaises(FrozenInstanceError):
                    binding.body = "mutated"

                ir = self.compile(text, type_line=type_line)
                TargetEffectCorpusCollector().observe(
                    replace(
                        self.db.lookup(
                            "Scheduled Counter Trigger Fixture"
                        ),
                        name="Compiler Fixture",
                        oracle_text=text,
                        type_line=type_line,
                        keywords=(),
                        faces=(),
                    ),
                    ir,
                )
                node = next(
                    value
                    for value in ir.faces[0].nodes
                    if value.template_id == template_id
                )
                self.assertEqual("exact", ir.status)
                self.assertTrue(node.exact)
                self.assertEqual("triggered_ability", node.kind)
                self.assertEqual(event.value, node.event)
                self.assertEqual(text, text[node.span.start : node.span.end])
                self.assertEqual(counter_name, node.effects[0]["counter"])
                self.assertEqual(amount, node.effects[0]["amount"])
                self.assertIn(
                    FIXED_COUNTER_EVENT_TRIGGER_MECHANIC,
                    node.mechanics,
                )
                self.assertTrue(
                    {
                        "counter.producer.fixed_effect",
                        "counter.producer.fixed_event_trigger",
                        "trigger.placement.apnap",
                    }.issubset(node.capability_dependencies)
                )
                programs = [
                    program
                    for program in generated_programs(
                        self.db,
                        replace(
                            self.db.lookup(
                                "Scheduled Counter Trigger Fixture"
                            ),
                            name="Compiler Fixture",
                            oracle_text=text,
                            type_line=type_line,
                            keywords=(),
                            faces=(),
                        ),
                        trust_level="trusted",
                        capability_registry=self.capabilities,
                        capability_profile="commander_review",
                    )
                    if program.provenance.get("template_id") == template_id
                ]
                self.assertEqual(1, len(programs))
                self.assertTrue(programs[0].capability_closure["trusted"])

        with self.assertRaises(ValueError):
            FixedCounterTriggerBinding("step.begin", "your upkeep", "body")

    def test_adjacent_event_and_effect_variants_remain_material(self):
        variants = (
            "Whenever you cast or copy a noncreature spell, put a +1/+1 counter on this creature.",
            "Whenever an opponent casts a noncreature spell, put a +1/+1 counter on this creature.",
            "Whenever a land enters, put a +1/+1 counter on this creature.",
            "At the beginning of your upkeep, if you control a creature, put a charge counter on this artifact.",
            "At the beginning of your upkeep, you may put a charge counter on this artifact.",
            "At the beginning of your upkeep, put X charge counters on this artifact.",
            "At the beginning of your upkeep, move a charge counter from this artifact onto target creature.",
            "At the beginning of your upkeep, remove a charge counter from this artifact.",
        )
        for text in variants:
            with self.subTest(text=text):
                ir = self.compile(text, type_line="Creature — Fixture")
                self.assertFalse(
                    any(
                        node.template_id in TEMPLATE_IDS
                        for node in ir.faces[0].nodes
                    )
                )
                self.assertNotEqual("exact", ir.status)
                self.assertTrue(ir.material_residuals)

    def test_fixed_counter_event_trigger_dependencies_and_compiler_mutation_fail_closed(
        self,
    ):
        cases = (
            (
                "Scheduled Counter Trigger Fixture",
                "counter.producer.fixed_event_trigger",
            ),
            (
                "Scheduled Counter Trigger Fixture",
                "counter.placement.quantity_replacement",
            ),
            (
                "Scheduled Counter Trigger Fixture",
                "trigger.placement.apnap",
            ),
            (
                "Landfall Counter Trigger Fixture",
                "trigger.event.normalized_zone_change",
            ),
            (
                "Noncreature Cast Counter Trigger Fixture",
                "trigger.event.normalized_spell_cast",
            ),
        )
        for card_name, dependency_id in cases:
            with self.subTest(card_name=card_name, dependency=dependency_id):
                registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
                dependency = next(
                    row
                    for row in registry["capabilities"]
                    if row["id"] == dependency_id
                )
                dependency["status"] = "blocked"
                dependency["blockers"] = ["focused dependency mutation"]
                ir = compile_oracle_card(
                    self.db.lookup(card_name),
                    capability_registry=CapabilityRegistry(registry),
                    capability_profile="commander_review",
                )
                node = next(
                    value
                    for value in ir.faces[0].nodes
                    if value.template_id in TEMPLATE_IDS
                )
                self.assertFalse(node.exact)
                self.assertTrue(node.residual_ids)
                self.assertNotEqual("exact", ir.status)

        record = self.db.lookup("Landfall Counter Trigger Fixture")
        with patch(
            "quorune.oracle_ir.fixed_counter_event_trigger_node",
            return_value=None,
        ):
            mutated = compile_oracle_card(
                record,
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            )
        self.assertFalse(
            any(
                node.template_id in TEMPLATE_IDS
                for node in mutated.faces[0].nodes
            )
        )
        self.assertNotEqual("exact", mutated.status)


class FixedCounterEventTriggerRuntimeTests(unittest.TestCase):
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
        public = zone == "battlefield"
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
        engine.state.players[seat].zones[zone].append(card.object_id)
        return card

    @staticmethod
    def deck_card(engine, seat: str, name: str) -> CardInstance:
        return next(
            card
            for card in engine.state.cards.values()
            if card.owner == seat and card.printed_name == name
        )

    def register_trigger(self, engine, source: CardInstance):
        programs = [
            program
            for program in generated_programs(
                self.db,
                self.db.by_oracle_id(source.oracle_id),
                trust_level="trusted",
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            )
            if program.provenance.get("template_id") in TEMPLATE_IDS
        ]
        self.assertEqual(1, len(programs))
        engine.semantics.put(programs[0])
        return programs[0]

    @staticmethod
    def resolve_top(engine) -> None:
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine._prepare_stack_resolution()

    def prepare_noncreature_cast(self, engine) -> CardInstance:
        engine.state.active_player = "A"
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = "A"
        engine.state.priority_passes = []
        card = self.deck_card(engine, "A", "Sol Ring")
        if card.zone != "hand":
            engine.move_card(card.object_id, "hand", log=False)
        engine.state.players["A"].mana_pool["C"] += 1
        engine._cast("A", {"card": card.ref, "pay": "auto"})
        return card

    @staticmethod
    def step_context(*, player: str, step: str = "upkeep") -> dict[str, str]:
        return {"phase": "beginning", "step": step, "player": player}

    @staticmethod
    def replacement_options(session, seat: str) -> list[str]:
        decision = StateProjector(
            session.engine.card_db,
            session.state,
        )._decision(f"pilot:{seat}")
        assert decision is not None
        return [option["id"] for option in decision["ctx"]["options"]]

    def finish_replacements(self, session, seat: str) -> None:
        for _ in range(8):
            decision = session.state.pending_decision
            if decision is None or decision.kind != "replacement.order":
                return
            result = session.act(
                f"pilot:{seat}",
                {
                    "action_id": "choose",
                    "choices": {
                        "replacement": self.replacement_options(
                            session,
                            seat,
                        )[0]
                    },
                },
            )
            self.assertTrue(result.ok, result.summary)
        self.fail("Fixed counter event-trigger replacement did not converge")

    def test_cast_counter_trigger_uses_normalized_event(self):
        session = self.session(120001)
        engine = session.engine
        source = self.add_card(
            engine,
            seat="A",
            name="Noncreature Cast Counter Trigger Fixture",
            ref="cast-counter-source",
            zone="battlefield",
        )
        program = self.register_trigger(engine, source)

        spell = self.prepare_noncreature_cast(engine)
        engine._stabilize()

        self.assertEqual("stack", spell.zone)
        self.assertEqual(program.key, engine.state.stack[-1].semantic_key)
        self.assertEqual("spell.cast", engine.state.stack[-1].context["event"])
        self.assertEqual(
            source.logical_object_id,
            engine.state.stack[-1].context["source_logical_object_id"],
        )
        self.resolve_top(engine)
        self.assertEqual(1, source.counters.get("+1/+1"))

    def test_land_entry_counter_trigger_uses_normalized_event(self):
        session = self.session(120002)
        engine = session.engine
        source = self.add_card(
            engine,
            seat="A",
            name="Landfall Counter Trigger Fixture",
            ref="landfall-counter-source",
            zone="battlefield",
        )
        program = self.register_trigger(engine, source)
        land = self.add_card(
            engine,
            seat="A",
            name="Forest",
            ref="landfall-entering-land",
            zone="hand",
        )

        engine.move_card(
            land.object_id,
            "battlefield",
            reason="Fixed counter Landfall fixture",
            semantic_events=True,
        )
        engine._stabilize()

        self.assertEqual(program.key, engine.state.stack[-1].semantic_key)
        self.assertEqual("land.enter", engine.state.stack[-1].context["event"])
        self.assertEqual(land.ref, engine.state.stack[-1].context["card"])
        self.resolve_top(engine)
        self.assertEqual(1, source.counters.get("+1/+1"))

    def test_scheduled_counter_trigger_suspends_for_quantity_replacement(self):
        session = self.session(120003)
        engine = session.engine
        source = self.add_card(
            engine,
            seat="A",
            name="Scheduled Counter Trigger Fixture",
            ref="scheduled-replacement-source",
            zone="battlefield",
        )
        self.add_card(
            engine,
            seat="A",
            name="Doubling Season",
            ref="scheduled-doubling-season",
            zone="battlefield",
        )
        self.add_card(
            engine,
            seat="A",
            name="Doc Samson, Super Psychiatrist",
            ref="scheduled-doc-samson",
            zone="battlefield",
        )
        self.register_trigger(engine, source)

        engine._dispatch_semantic_event(
            "step.begin",
            self.step_context(player="A"),
        )
        engine._stabilize()
        self.resolve_top(engine)

        self.assertEqual("replacement.order", engine.state.pending_decision.kind)
        self.assertFalse(source.counters)
        self.finish_replacements(session, "A")
        self.assertIn(source.counters.get("charge"), {5, 6})

    def test_multiple_scheduled_counter_triggers_use_one_apnap_batch(self):
        session = self.session(120004, players=4)
        engine = session.engine
        engine.state.active_player = "A"
        source_a = self.add_card(
            engine,
            seat="A",
            name="Each Upkeep Counter Trigger Fixture",
            ref="apnap-counter-source-a",
            zone="battlefield",
        )
        source_c = self.add_card(
            engine,
            seat="C",
            name="Each Upkeep Counter Trigger Fixture",
            ref="apnap-counter-source-c",
            zone="battlefield",
        )
        self.register_trigger(engine, source_a)
        self.register_trigger(engine, source_c)

        items = collect_trigger_items(
            engine,
            "step.begin",
            self.step_context(player="A"),
        )
        self.assertEqual({"A", "C"}, {item.controller for item in items})
        enqueue_trigger_batch(engine, items)
        self.assertEqual(1, len(engine.state.pending_trigger_batches))
        self.assertEqual(
            ["A", "B", "C", "D"],
            list(engine.state.pending_trigger_batches[0].apnap_order),
        )

        engine._stabilize()

        self.assertEqual(
            ["A", "C"],
            [item.controller for item in engine.state.stack[-2:]],
        )
        self.assertEqual(
            {source_a.object_id, source_c.object_id},
            {item.source_object_id for item in engine.state.stack[-2:]},
        )

    def test_four_player_counter_trigger_choice_is_private_and_replays_exactly(
        self,
    ):
        session = self.session(120005, players=4)
        engine = session.engine
        source = self.add_card(
            engine,
            seat="C",
            name="Scheduled Counter Trigger Fixture",
            ref="private-counter-trigger-source",
            zone="battlefield",
        )
        self.add_card(
            engine,
            seat="C",
            name="Doubling Season",
            ref="private-trigger-doubling",
            zone="battlefield",
        )
        self.add_card(
            engine,
            seat="C",
            name="Doc Samson, Super Psychiatrist",
            ref="private-trigger-addition",
            zone="battlefield",
        )
        self.register_trigger(engine, source)

        engine._dispatch_semantic_event(
            "step.begin",
            self.step_context(player="C"),
        )
        engine._stabilize()
        self.resolve_top(engine)
        projector = StateProjector(self.db, engine.state)
        for seat in ("A", "B", "D"):
            self.assertIsNone(projector._decision(f"pilot:{seat}"))
        projected = projector._decision("pilot:C")
        self.assertIsNotNone(projected)
        self.assertNotIn(source.object_id, json.dumps(projected, sort_keys=True))

        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        self.finish_replacements(session, "C")

        self.assertIn(source.counters.get("charge"), {5, 6})
        expected_hash = authoritative_state_hash(engine.state)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "fixed-counter-trigger-replay"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_stale_counter_target_rolls_back_trigger_resolution(self):
        session = self.session(120006)
        engine = session.engine
        source = self.add_card(
            engine,
            seat="A",
            name="Targeted Scheduled Counter Trigger Fixture",
            ref="targeted-counter-trigger-source",
            zone="battlefield",
        )
        target = self.add_card(
            engine,
            seat="A",
            name="Scute Swarm",
            ref="stale-counter-trigger-target",
            zone="battlefield",
        )
        self.register_trigger(engine, source)

        engine._dispatch_semantic_event(
            "step.begin",
            self.step_context(player="A", step="beginning_combat"),
        )
        engine._stabilize()
        self.assertEqual("semantic.target", engine.state.pending_decision.kind)
        selected = session.act(
            "pilot:A",
            {"action_id": "choose", "targets": [target.ref]},
        )
        self.assertTrue(selected.ok, selected.summary)
        target = engine.state.cards[target.object_id]
        engine.move_card(target.object_id, "graveyard", log=False)
        counter_snapshot = {
            object_id: dict(card.counters)
            for object_id, card in engine.state.cards.items()
        }

        self.resolve_top(engine)

        self.assertEqual("graveyard", target.zone)
        self.assertEqual(
            counter_snapshot,
            {
                object_id: dict(card.counters)
                for object_id, card in engine.state.cards.items()
            },
        )


if __name__ == "__main__":
    unittest.main()
