from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common import DB_PATH, ROOT, keep_all, make_session
from quorune.carddb import CardDatabase
from quorune.compiler.fixed_target_effect_sequences import (
    fixed_target_effect_sequence_template,
)
from quorune.deck import DeckLoader
from quorune.model import CardInstance, StackItem
from quorune.keyword_counters import (
    KeywordCounterError,
    keyword_counter_abilities,
    keyword_counter_mechanic,
)
from quorune.oracle_ir import compile_oracle_card
from quorune.projection import StateProjector
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)
from quorune.rules.capabilities import (
    CapabilityRegistry,
    capability_dependencies_for_node,
    load_default_capability_registry,
)
from quorune.semantics import SemanticProgram
from scripts.build_test_database import build_fixture_database


REGISTRY_PATH = ROOT / "quorune" / "rules" / "capability-registry.json"
SEQUENCE_CAPABILITY = "resolution.effect_sequence.fixed_target"


def focused_card_database(directory: str) -> CardDatabase:
    database = Path(directory) / "fixed-target-sequences.sqlite3"
    build_fixture_database(
        [
            ROOT / "tests" / "fixtures" / "scryfall-exact-lists.json",
            ROOT / "tests" / "fixtures" / "counter-replacement-cards.json",
        ],
        database,
    )
    return CardDatabase(database)


class FixedTargetEffectSequenceCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = CardDatabase(DB_PATH)
        cls.base = cls.db.lookup("Sol Ring")
        cls.capabilities = load_default_capability_registry()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def compile(self, text: str, *, type_line: str = "Instant"):
        return compile_oracle_card(
            replace(
                self.base,
                name="Fixture",
                oracle_text=text,
                type_line=type_line,
                keywords=(),
                faces=(),
            ),
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        )

    def test_keyword_counter_vocabulary_is_closed_and_strict(self):
        self.assertEqual("flying", keyword_counter_mechanic(" Flying "))
        self.assertEqual(
            "double-strike",
            keyword_counter_mechanic("double   strike"),
        )
        self.assertIsNone(keyword_counter_mechanic("ward {2}"))
        self.assertEqual(
            ("Flying", "Double Strike"),
            keyword_counter_abilities(
                {"double strike": 2, "flying": 1, "charge": 8}
            ),
        )
        for amount in (True, -1, 1.5, "1"):
            with self.subTest(amount=amount):
                with self.assertRaises(KeywordCounterError):
                    keyword_counter_abilities({"flying": amount})

    def test_spell_trigger_and_activated_contexts_share_target_threaded_sequence_lowering(
        self,
    ):
        cases = (
            (
                "Target creature you control gets +1/+1 until end of turn. "
                "Put a flying counter on it.",
                "Instant",
                "spell_ability",
                {"combat.block.flying", "counter.characteristic.keyword"},
            ),
            (
                "When this creature enters, put a +1/+1 counter on target "
                "creature. It gains haste until end of turn.",
                "Creature — Test",
                "triggered_ability",
                {"combat.attack.haste", "activation.tap_untap_cost.haste"},
            ),
            (
                "{1}: Target creature gets +2/+0 and gains vigilance until end "
                "of turn. Put a +1/+1 counter on it.",
                "Creature — Test",
                "activated_ability",
                {"combat.attack.vigilance"},
            ),
        )
        for text, type_line, kind, keyword_capabilities in cases:
            with self.subTest(kind=kind):
                ir = self.compile(text, type_line=type_line)
                node = next(
                    value
                    for value in ir.faces[0].nodes
                    if value.template_id
                    == "fixed-target-counter-characteristics-sequence-v1"
                )
                self.assertEqual("exact", ir.status)
                self.assertTrue(node.exact)
                self.assertEqual(kind, node.kind)
                self.assertEqual(
                    {
                        "continuous.resolution.fixed_characteristics_until_end_of_turn",
                        "counter.producer.fixed_effect",
                        SEQUENCE_CAPABILITY,
                        "target.revalidate_resolution",
                    }
                    | keyword_capabilities,
                    set(node.capability_dependencies)
                    - {
                        "trigger.event.normalized_zone_change",
                        "trigger.placement.apnap",
                    },
                )
                self.assertEqual(
                    text[node.span.start : node.span.end],
                    ir.faces[0].oracle_text[node.span.start : node.span.end],
                )

    def test_target_threaded_sequence_preserves_printed_effect_order(self):
        first = fixed_target_effect_sequence_template(
            "Target creature gets +2/+0 until end of turn. "
            "Put a +1/+1 counter on it. It gains flying until end of turn.",
            card_name="Fixture",
        )
        second = fixed_target_effect_sequence_template(
            "Put a +1/+1 counter on target creature. "
            "It gets +2/+0 until end of turn. It gains flying until end of turn.",
            card_name="Fixture",
        )
        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        assert first is not None and second is not None
        self.assertEqual(
            [
                "modify_stats_until_end_of_turn",
                "place_counters",
                "grant_keyword_until_end_of_turn",
            ],
            [effect["op"] for effect in first.effects],
        )
        self.assertEqual(
            [
                "place_counters",
                "modify_stats_until_end_of_turn",
                "grant_keyword_until_end_of_turn",
            ],
            [effect["op"] for effect in second.effects],
        )
        self.assertNotEqual(first.effects, second.effects)

    def test_standalone_target_characteristics_are_target_revalidated(self):
        for text in (
            "Target creature gets -2/+3 until end of turn.",
            "Target creature an opponent controls gains flying until end of turn.",
            "Target creature you control gets +1/+1 and gains haste until end of turn.",
        ):
            with self.subTest(text=text):
                ir = self.compile(text)
                node = ir.faces[0].nodes[0]
                self.assertEqual("exact", ir.status)
                expected = {
                        "continuous.resolution.fixed_characteristics_until_end_of_turn",
                        "target.revalidate_resolution",
                }
                if "flying" in text.casefold():
                    expected.add("combat.block.flying")
                if "haste" in text.casefold():
                    expected.update(
                        {
                            "combat.attack.haste",
                            "activation.tap_untap_cost.haste",
                        }
                    )
                self.assertEqual(expected, set(node.capability_dependencies))

    def test_unsupported_target_threaded_variants_remain_material_residuals(
        self,
    ):
        texts = (
            "Up to one target creature gets +1/+1 until end of turn. Put a +1/+1 counter on it.",
            "Target creature gets +X/+X until end of turn. Put a +1/+1 counter on it.",
            "Target creature gets +1/+1 until end of turn. You may put a +1/+1 counter on it.",
            "Target creature gains protection from the color of your choice until end of turn. Put a +1/+1 counter on it.",
            "Target creature gets +1/+1 until end of turn. Scry 1. Put a +1/+1 counter on it.",
            "Target creature gets +1/+1 until end of turn. Put a +1/+1 counter on target creature.",
            "Put a +1/+1 counter on it. It gains flying until end of turn.",
            "Target creature gains flying or reach until end of turn. Put a +1/+1 counter on it.",
            "Target creature gets +1/+1 until end of turn. Put a +1/+1 counter and a flying counter on it.",
        )
        for text in texts:
            with self.subTest(text=text):
                self.assertIsNone(
                    fixed_target_effect_sequence_template(
                        text,
                        card_name="Fixture",
                    )
                )
                ir = self.compile(text)
                self.assertNotEqual("exact", ir.status)
                self.assertTrue(ir.material_residuals)

    def test_untrusted_keyword_behavior_blocks_exact_sequence_promotion(self):
        for keyword in ("hexproof", "first strike", "indestructible"):
            text = (
                f"Target creature gains {keyword} until end of turn. "
                "Put a +1/+1 counter on it."
            )
            with self.subTest(keyword=keyword):
                self.assertIsNotNone(
                    fixed_target_effect_sequence_template(
                        text,
                        card_name="Fixture",
                    )
                )
                ir = self.compile(text)
                self.assertNotEqual("exact", ir.status)
                self.assertTrue(ir.material_residuals)

    def test_target_threaded_sequence_shape_mutants_fail_closed(self):
        template = fixed_target_effect_sequence_template(
            "Target creature gets +1/+1 until end of turn. "
            "Put a +1/+1 counter on it. It gains flying until end of turn.",
            card_name="Fixture",
        )
        self.assertIsNotNone(template)
        assert template is not None
        expected = {
            "combat.block.flying",
            "continuous.resolution.fixed_characteristics_until_end_of_turn",
            "counter.producer.fixed_effect",
            SEQUENCE_CAPABILITY,
            "target.revalidate_resolution",
        }
        self.assertEqual(
            expected,
            set(
                capability_dependencies_for_node(
                    effects=template.effects,
                    target_schema=template.target_schema,
                    mechanic_ids=template.compiled()[3],
                )
            ),
        )
        malformed = (
            ({**template.effects[0], "power": True}, *template.effects[1:]),
            (template.effects[0], {**template.effects[1], "amount": True}, template.effects[2]),
            (template.effects[0], {**template.effects[1], "card": "$target.1"}, template.effects[2]),
            (template.effects[0], template.effects[1], {**template.effects[2], "keyword": "Flying", "extra": True}),
            (template.effects[0], template.effects[1], template.effects[2], template.effects[2]),
        )
        for effects in malformed:
            with self.subTest(effects=effects):
                dependencies = capability_dependencies_for_node(
                    effects=effects,
                    target_schema=template.target_schema,
                    mechanic_ids=template.compiled()[3],
                )
                self.assertNotIn(SEQUENCE_CAPABILITY, dependencies)
        self.assertNotIn(
            SEQUENCE_CAPABILITY,
            capability_dependencies_for_node(
                effects=template.effects,
                target_schema={**template.target_schema, "count": 2},
                mechanic_ids=template.compiled()[3],
            ),
        )

    def test_target_threaded_sequence_dependencies_fail_closed(self):
        raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        dependency = next(
            row
            for row in raw["capabilities"]
            if row["id"] == "counter.producer.fixed_effect"
        )
        dependency["status"] = "blocked"
        dependency["blockers"] = ["test mutation"]
        ir = compile_oracle_card(
            replace(
                self.base,
                name="Fixture",
                oracle_text=(
                    "Put a +1/+1 counter on target creature. "
                    "It gains flying until end of turn."
                ),
                type_line="Instant",
                keywords=(),
                faces=(),
            ),
            capability_registry=CapabilityRegistry(raw),
            capability_profile="commander_review",
        )
        self.assertNotEqual("exact", ir.status)
        self.assertTrue(ir.material_residuals)

    def test_target_threaded_sequence_compiler_mutant_is_killed(self):
        text = (
            "Put a +1/+1 counter on target creature. "
            "It gains flying until end of turn."
        )

        def exact() -> None:
            self.assertEqual("exact", self.compile(text).status)

        exact()
        with patch(
            "quorune.compiler.resolution_effect_templates."
            "fixed_target_effect_sequence_template",
            return_value=None,
        ):
            with self.assertRaises(AssertionError):
                exact()


class FixedTargetEffectSequenceRuntimeTests(unittest.TestCase):
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

    def stage_sequence(
        self,
        session,
        *,
        target: CardInstance,
        effects: list[dict[str, object]],
        key: str,
    ) -> None:
        engine = session.engine
        program = SemanticProgram(
            key=key,
            label="Fixed target effect sequence",
            effects=effects,
            target_schema={
                "zones": ["battlefield"],
                "categories": ["permanent"],
                "types_any": ["creature"],
                "count": 1,
            },
            trust_level="provisional",
        )
        engine.semantics.put(program)
        engine.state.stack.append(
            StackItem(
                stack_id=key,
                ref=f"S-{key}",
                kind="triggered_ability",
                controller="A",
                label=program.label,
                semantic_key=program.key,
                targets=[target.ref],
                visibility=list(engine.seats),
            )
        )
        engine.state.active_player = "A"
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine._grant_priority("A")
        engine._issue_priority("A")
        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()

    @staticmethod
    def pass_priority(session) -> None:
        for seat in session.engine.seats:
            result = session.act(f"pilot:{seat}", {"action_id": "pass"})
            if not result.ok:
                raise AssertionError(result.summary)

    def choose_replacements(self, session) -> None:
        for _ in range(8):
            decision = session.engine.state.pending_decision
            if decision is None or decision.kind != "replacement.order":
                return
            projected = StateProjector(
                self.db,
                session.engine.state,
            )._decision("pilot:A")
            selected = projected["ctx"]["options"][0]["id"]
            result = session.act(
                "pilot:A",
                {
                    "action_id": "choose",
                    "choices": {"replacement": selected},
                },
            )
            self.assertTrue(result.ok, result.summary)
        self.fail("Replacement sequence did not converge")

    def test_counter_replacement_suspends_and_resumes_remaining_sequence_exactly(
        self,
    ):
        session = self.session(60812201)
        engine = session.engine
        target = self.add_permanent(
            engine,
            seat="A",
            name="Elves of Deep Shadow",
            ref="sequence-target",
        )
        self.add_permanent(
            engine,
            seat="A",
            name="Doubling Season",
            ref="sequence-doubling",
        )
        self.add_permanent(
            engine,
            seat="A",
            name="Doc Samson, Super Psychiatrist",
            ref="sequence-doc",
        )
        self.stage_sequence(
            session,
            target=target,
            key="counter-sequence-replay",
            effects=[
                {
                    "op": "modify_stats_until_end_of_turn",
                    "card": "$target.0",
                    "power": 2,
                    "toughness": 1,
                },
                {
                    "op": "place_counters",
                    "card": "$target.0",
                    "counter": "flying",
                    "amount": 1,
                    "source": "$source",
                },
                {
                    "op": "grant_keyword_until_end_of_turn",
                    "card": "$target.0",
                    "keyword": "Hexproof",
                },
            ],
        )
        self.pass_priority(session)
        self.assertEqual("replacement.order", engine.state.pending_decision.kind)
        self.assertEqual(3, engine._numeric_stat(target.object_id, "power"))
        self.assertNotIn("hexproof", engine._combat_keywords(target))
        self.assertNotIn("flying", target.counters)

        self.choose_replacements(session)
        self.assertGreater(target.counters["flying"], 1)
        self.assertIn("flying", engine._combat_keywords(target))
        self.assertIn("hexproof", engine._combat_keywords(target))
        self.assertEqual(2, len(engine.state.continuous_effects))
        expected_hash = authoritative_state_hash(engine.state)

        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "counter-sequence-record"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])
        engine._change_permanent_counter(
            target,
            "flying",
            -target.counters["flying"],
        )
        self.assertNotIn("flying", engine._combat_keywords(target))

    def test_four_player_sequence_choice_is_seat_scoped_and_replays(self):
        session = self.session(60812202, players=4)
        engine = session.engine
        target = self.add_permanent(
            engine,
            seat="A",
            name="Elves of Deep Shadow",
            ref="four-player-sequence-target",
        )
        self.add_permanent(
            engine,
            seat="A",
            name="Doubling Season",
            ref="four-player-sequence-doubling",
        )
        self.add_permanent(
            engine,
            seat="A",
            name="Doc Samson, Super Psychiatrist",
            ref="four-player-sequence-doc",
        )
        self.stage_sequence(
            session,
            target=target,
            key="four-player-counter-sequence",
            effects=[
                {
                    "op": "place_counters",
                    "card": "$target.0",
                    "counter": "+1/+1",
                    "amount": 1,
                    "source": "$source",
                },
                {
                    "op": "modify_stats_until_end_of_turn",
                    "card": "$target.0",
                    "power": 1,
                    "toughness": 1,
                },
            ],
        )
        self.pass_priority(session)
        projector = StateProjector(self.db, engine.state)
        projected = projector._decision("pilot:A")
        self.assertIsNotNone(projected)
        for seat in ("B", "C", "D"):
            self.assertIsNone(projector._decision(f"pilot:{seat}"))
        rendered = json.dumps(projected, sort_keys=True)
        self.assertNotIn(target.object_id, rendered)
        self.choose_replacements(session)
        expected_hash = authoritative_state_hash(engine.state)

        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "four-player-sequence-record"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_stale_target_rolls_back_before_sequence_mutation(self):
        session = self.session(60812203)
        engine = session.engine
        target = self.add_permanent(
            engine,
            seat="A",
            name="Elves of Deep Shadow",
            ref="stale-sequence-target",
        )
        self.stage_sequence(
            session,
            target=target,
            key="stale-counter-sequence",
            effects=[
                {
                    "op": "modify_stats_until_end_of_turn",
                    "card": "$target.0",
                    "power": 2,
                    "toughness": 2,
                },
                {
                    "op": "place_counters",
                    "card": "$target.0",
                    "counter": "+1/+1",
                    "amount": 1,
                    "source": "$source",
                },
            ],
        )
        engine.move_card(target.object_id, "graveyard", reason="stale target")
        self.pass_priority(session)

        self.assertEqual({}, target.counters)
        self.assertFalse(engine.state.continuous_effects)
        self.assertFalse(
            any(item.ref == "S-stale-counter-sequence" for item in engine.state.stack)
        )

    def test_keyword_counter_characteristic_mutant_is_killed(self):
        session = self.session(60812204)
        target = self.add_permanent(
            session.engine,
            seat="A",
            name="Elves of Deep Shadow",
            ref="keyword-counter-mutation-target",
        )
        target.counters["flying"] = 1

        def exact() -> None:
            self.assertIn("flying", session.engine._combat_keywords(target))

        exact()
        with patch(
            "quorune.characteristic_evaluation.keyword_counter_abilities",
            return_value=(),
        ):
            with self.assertRaises(AssertionError):
                exact()


if __name__ == "__main__":
    unittest.main()
