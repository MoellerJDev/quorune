from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from common import ROOT, keep_all, make_session
from quorune.carddb import CardDatabase
from quorune.compiler import flashback_nodes as flashback_nodes_module
from quorune.deck import DeckLoader
from quorune.errors import GameRuleError
from quorune.flashback import (
    compile_fixed_mana_flashback,
    FixedManaFlashbackSpec,
    FlashbackError,
    flashback_handler_descriptor,
    FLASHBACK_CAPABILITY_ID,
    FLASHBACK_CAST_ANNOTATION,
    FLASHBACK_CAST_OPTION_ID,
    FLASHBACK_HANDLER_ID,
)
from quorune.model import CardInstance
from quorune.oracle_ir import compile_oracle_card, register_generated_programs
from quorune.record import authoritative_state_hash, checkpoint_envelope, replay_record
from quorune.rules.capabilities import CapabilityRegistry, load_default_capability_registry
from quorune.semantic_runtime.flashback import default_fixed_mana_flashback_registry
from quorune.semantics import SemanticRegistry
from scripts.build_test_database import build_fixture_database


REGISTRY_PATH = ROOT / "quorune" / "rules" / "capability-registry.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "flashback-cards.json"


def focused_card_database(directory: str) -> CardDatabase:
    database = Path(directory) / "flashback.sqlite3"
    build_fixture_database(
        [
            ROOT / "tests" / "fixtures" / "scryfall-exact-lists.json",
            FIXTURE_PATH,
        ],
        database,
    )
    return CardDatabase(database)


class FixedManaFlashbackModelTests(unittest.TestCase):
    def test_flashback_descriptor_and_registry_are_strict(self):
        spec = compile_fixed_mana_flashback(
            material_line="Flashback {2}{U}",
            oracle_line=(
                "Flashback {2}{U} (You may cast this card from your graveyard "
                "for its flashback cost. Then exile it.)"
            ),
            line_index=1,
        )
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual("ab2", spec.ability_id)
        self.assertEqual(
            {
                "GENERIC": 2,
                "W": 0,
                "U": 1,
                "B": 0,
                "R": 0,
                "G": 0,
                "C": 0,
            },
            dict(spec.to_dict()["mana_cost"]),
        )
        self.assertEqual(spec, FixedManaFlashbackSpec.from_dict(spec.to_dict()))
        self.assertEqual(
            (spec,),
            default_fixed_mana_flashback_registry().lower(
                flashback_handler_descriptor(spec),
                None,
            ),
        )
        malformed = spec.to_dict()
        malformed["unknown"] = True
        with self.assertRaisesRegex(FlashbackError, "closed schema"):
            FixedManaFlashbackSpec.from_dict(malformed)

        life_spec = compile_fixed_mana_flashback(
            material_line="Flashback—{1}{U}, Pay 3 life",
            oracle_line=(
                "Flashback—{1}{U}, Pay 3 life. (You may cast this card from "
                "your graveyard for its flashback cost. Then exile it.)"
            ),
            line_index=1,
        )
        self.assertIsNotNone(life_spec)
        assert life_spec is not None
        self.assertEqual(3, life_spec.life_payment)
        self.assertEqual(
            [
                {
                    "schema_version": 1,
                    "kind": "fixed_life_payment",
                    "amount": 3,
                }
            ],
            life_spec.cast_cost_option()["_additional_option_costs"],
        )


class FixedManaFlashbackCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.db = focused_card_database(cls.temporary.name)
        cls.record = cls.db.lookup("Think Twice")
        cls.capabilities = load_default_capability_registry()
        cls.registry_value = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temporary.cleanup()

    def compile(self, record=None, *, capabilities=None):
        return compile_oracle_card(
            record or self.record,
            capability_registry=capabilities or self.capabilities,
            capability_profile="commander_review",
        )

    @staticmethod
    def flashback_node(ir):
        return next(
            node
            for node in ir.faces[0].nodes
            if "flashback" in node.mechanics
        )

    def test_fixed_mana_flashback_compiles_source_spanned_typed_program(self):
        ir = self.compile()
        node = self.flashback_node(ir)
        self.assertTrue(node.exact, ir.material_residuals)
        self.assertEqual("keyword_ability", node.kind)
        self.assertEqual("all", node.active_zone)
        self.assertEqual("cast.cost", node.event)
        self.assertEqual("ordinary-fixed-mana-flashback-v1", node.template_id)
        self.assertEqual((FLASHBACK_CAPABILITY_ID,), node.capability_dependencies)
        self.assertEqual(FLASHBACK_HANDLER_ID, node.handlers[0]["handler_id"])
        self.assertEqual(
            self.record.oracle_text[node.span.start : node.span.end],
            node.text,
        )

        registry = SemanticRegistry(include_builtin_packs=False)
        register_generated_programs(
            self.db,
            registry,
            (self.record,),
            capability_registry=self.capabilities,
            capability_profile="commander_review",
            promote_exact_runtime_handlers=True,
            promote_exact_effect_programs=True,
        )
        card_program = registry.card_program_for_oracle(self.record.oracle_id)
        self.assertIsNotNone(card_program)
        assert card_program is not None
        self.assertTrue(card_program.trust_closure["trusted"])
        program = next(
            program
            for program in registry.programs_for_oracle(self.record.oracle_id)
            if program.event == "cast.cost"
        )
        self.assertEqual("trusted", program.trust_level)
        self.assertEqual(
            "exact",
            program.provenance["card_program_admission"]["oracle_ir_status"],
        )

    def test_nonordinary_flashback_costs_remain_residual(self):
        unsupported = (
            self.db.lookup("Devil's Play"),
            replace(
                self.record,
                oracle_text=(
                    "Draw a card.\n"
                    "Flashback—Sacrifice a creature. (You may cast this card "
                    "from your graveyard for its flashback cost. Then exile it.)"
                ),
            ),
        )
        for record in unsupported:
            with self.subTest(name=record.name):
                ir = self.compile(record)
                node = self.flashback_node(ir)
                self.assertFalse(node.exact)
                self.assertFalse(node.lowerable)
                self.assertEqual("ordinary-flashback-residual-v1", node.template_id)
                self.assertTrue(ir.material_residuals)

    def test_fixed_life_flashback_adds_the_existing_payment_capability(self):
        ir = self.compile(self.db.lookup("Deep Analysis"))
        node = self.flashback_node(ir)
        self.assertTrue(node.exact, ir.material_residuals)
        self.assertEqual(
            (
                "casting.additional_cost.fixed_life_payment",
                FLASHBACK_CAPABILITY_ID,
            ),
            node.capability_dependencies,
        )
        spec = FixedManaFlashbackSpec.from_dict(
            node.handlers[0]["flashback"]
        )
        self.assertEqual(3, spec.life_payment)

    def test_flashback_dependency_and_compiler_mutations_fail_closed(self):
        capability = next(
            row
            for row in self.registry_value["capabilities"]
            if row["id"] == FLASHBACK_CAPABILITY_ID
        )
        for blocked in (FLASHBACK_CAPABILITY_ID, *capability["dependencies"]):
            with self.subTest(blocked=blocked):
                value = deepcopy(self.registry_value)
                row = next(
                    item for item in value["capabilities"] if item["id"] == blocked
                )
                row["status"] = "blocked"
                row["blockers"] = ["focused Flashback dependency mutation"]
                node = self.flashback_node(
                    self.compile(capabilities=CapabilityRegistry(value))
                )
                self.assertFalse(node.exact)
                self.assertTrue(node.residual_ids)

        value = deepcopy(self.registry_value)
        life_payment = next(
            item
            for item in value["capabilities"]
            if item["id"] == "casting.additional_cost.fixed_life_payment"
        )
        life_payment["status"] = "blocked"
        life_payment["blockers"] = ["focused Flashback life-payment mutation"]
        life_node = self.flashback_node(
            self.compile(
                self.db.lookup("Deep Analysis"),
                capabilities=CapabilityRegistry(value),
            )
        )
        self.assertFalse(life_node.exact)
        self.assertTrue(life_node.residual_ids)

        def assert_exact() -> None:
            node = self.flashback_node(self.compile())
            self.assertTrue(node.exact)
            self.assertEqual(FLASHBACK_HANDLER_ID, node.handlers[0]["handler_id"])

        assert_exact()
        with mock.patch.object(
            flashback_nodes_module,
            "compile_fixed_mana_flashback",
            return_value=None,
        ):
            with self.assertRaises(AssertionError):
                assert_exact()


class FixedManaFlashbackRuntimeTests(unittest.TestCase):
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

    def session(self, seed: int, *, players: int = 4):
        session = make_session(
            self.db,
            self.mishra,
            self.zimone,
            players=players,
            seed=seed,
            auto_pass_empty=False,
        )
        keep_all(session)
        session.engine.permissions.invalidate_current()
        session.engine.state.pending_decision = None
        session.engine.state.priority_player = None
        session.engine.state.priority_passes = []
        session.commands.clear()
        session.decisions.clear()
        return session

    def add_card(
        self,
        session,
        *,
        name: str,
        ref: str,
        seat: str = "B",
        zone: str = "graveyard",
        controller: str | None = None,
    ) -> CardInstance:
        engine = session.engine
        record = self.db.lookup(name)
        card = CardInstance(
            object_id=f"fixture:{ref}",
            ref=ref,
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner=seat,
            controller=controller or seat,
            zone=zone,
            zone_timestamp=engine.state.event_sequence + 1,
            acquired_control_turn_count=-1,
            known_to=list(engine.seats) if zone != "hand" else [seat],
            revealed_to=list(engine.seats) if zone != "hand" else [],
        )
        engine.state.cards[card.object_id] = card
        engine.state.players[seat].zones[zone].append(card.object_id)
        register_generated_programs(
            self.db,
            engine.semantics,
            (record,),
            capability_registry=self.capabilities,
            capability_profile=engine.state.config.review_profile,
            promote_exact_runtime_handlers=True,
            promote_exact_effect_programs=True,
        )
        return card

    @staticmethod
    def prepare_main(session, seat: str = "B") -> None:
        engine = session.engine
        engine.state.active_player = seat
        engine.state.started = True
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine.state.stack.clear()
        engine.state.priority_passes = []
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.permissions.invalidate_current()
        engine._grant_priority(seat)
        engine.pump()

    @staticmethod
    def cast_action(engine, card, seat: str = "B"):
        return next(
            action
            for action in engine._priority_action_hints(seat)["actions"]
            if action.get("card") == card.ref and action.get("action") == "cast"
        )

    @staticmethod
    def resolve_stack_with_passes(session) -> None:
        for _ in range(16):
            if not session.engine.state.stack:
                return
            principal = session.pending_principals()[0]
            result = session.act(principal, {"action_id": "pass"})
            if not result.ok:
                raise AssertionError(result.summary)
        raise AssertionError("Flashed-back spell did not resolve")

    def test_flashback_cast_resolves_to_exile_and_replays(self):
        session = self.session(70234001, players=4)
        engine = session.engine
        card = self.add_card(session, name="Think Twice", ref="FLASH1")
        engine.state.players["B"].mana_pool["U"] = 3
        self.prepare_main(session)

        action = self.cast_action(engine, card)
        options = {row["id"]: row for row in action["cost_options"]}
        self.assertEqual({FLASHBACK_CAST_OPTION_ID}, set(options))
        self.assertEqual(2, options[FLASHBACK_CAST_OPTION_ID]["requirements"]["GENERIC"])
        self.assertEqual(1, options[FLASHBACK_CAST_OPTION_ID]["requirements"]["U"])
        self.assertFalse(
            any(
                row.get("card") == card.ref
                for row in engine._priority_action_hints("A")["actions"]
            )
        )
        starting_hand = len(engine.state.players["B"].zones["hand"])
        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        result = session.act(
            "pilot:B",
            {"action_id": action["id"], "cost_option": FLASHBACK_CAST_OPTION_ID},
        )
        self.assertTrue(result.ok, result.summary)
        self.assertEqual("stack", card.zone)
        self.assertIs(True, card.annotations.get(FLASHBACK_CAST_ANNOTATION))
        self.resolve_stack_with_passes(session)

        self.assertEqual("exile", card.zone)
        self.assertNotIn(FLASHBACK_CAST_ANNOTATION, card.annotations)
        self.assertEqual(
            starting_hand + 1,
            len(engine.state.players["B"].zones["hand"]),
        )
        for principal in ("pilot:A", "pilot:B", "pilot:C", "pilot:D"):
            packet = json.dumps(session.packet(principal, full=True), sort_keys=True)
            self.assertNotIn(card.object_id, packet)

        expected_hash = authoritative_state_hash(engine.state)
        with tempfile.TemporaryDirectory() as temporary:
            game_dir = Path(temporary) / "flashback-replay"
            session.save(game_dir)
            replay = replay_record(game_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(expected_hash, replay["final_state_hash"])

    def test_countered_flashback_uses_self_replacement_before_competing_destination(self):
        session = self.session(70234002, players=4)
        engine = session.engine
        card = self.add_card(session, name="Think Twice", ref="FLASH2")
        voidwalker = self.add_card(
            session,
            name="Dauthi Voidwalker",
            ref="FLASH-VOIDWALKER",
            seat="A",
            zone="battlefield",
        )
        engine.state.players["B"].mana_pool["U"] = 3
        self.prepare_main(session)
        engine.permissions.invalidate_current()
        engine._cast(
            "B",
            {
                "card": card.ref,
                "from": "graveyard",
                "cost_option": FLASHBACK_CAST_OPTION_ID,
                "pay": "auto",
            },
        )
        item = engine.state.stack[-1]
        before_events = len(engine.state.events)
        engine._counter_stack_item(
            item.ref,
            reason="Flashback counter interaction",
            countered_by="A",
        )

        self.assertEqual("exile", card.zone)
        applied = [
            event
            for event in engine.state.events[before_events:]
            if event.code == "replacement.apply"
        ]
        self.assertEqual([card.ref], [event.details["source"] for event in applied])
        self.assertFalse(
            any(event.details.get("source") == voidwalker.ref for event in applied)
        )

    def test_flashback_and_independent_graveyard_permission_offer_distinct_costs(self):
        session = self.session(70234003, players=2)
        engine = session.engine
        card = self.add_card(session, name="Think Twice", ref="FLASH3")
        card.annotations["cast_from"] = ["graveyard"]
        engine.state.players["B"].mana_pool["U"] = 3
        self.prepare_main(session)
        action = self.cast_action(engine, card)
        self.assertEqual(
            {"normal", FLASHBACK_CAST_OPTION_ID},
            {row["id"] for row in action["cost_options"]},
        )

    def test_fixed_life_flashback_pays_life_and_exiles(self):
        session = self.session(70234007, players=2)
        engine = session.engine
        card = self.add_card(session, name="Deep Analysis", ref="FLASH7")
        engine.state.players["B"].mana_pool["U"] = 2
        self.prepare_main(session)
        starting_life = engine.state.players["B"].life
        starting_hand = len(engine.state.players["B"].zones["hand"])
        engine.permissions.invalidate_current()
        engine._cast(
            "B",
            {
                "card": card.ref,
                "from": "graveyard",
                "cost_option": FLASHBACK_CAST_OPTION_ID,
                "targets": ["B"],
                "pay": "auto",
            },
        )
        self.assertEqual(starting_life - 3, engine.state.players["B"].life)
        engine.state.priority_player = None
        engine._prepare_stack_resolution()
        self.assertEqual("exile", card.zone)
        self.assertEqual(
            starting_hand + 2,
            len(engine.state.players["B"].zones["hand"]),
        )

    def test_normal_cast_does_not_apply_flashback_departure(self):
        session = self.session(70234006, players=2)
        engine = session.engine
        card = self.add_card(
            session,
            name="Think Twice",
            ref="FLASH6",
            zone="hand",
        )
        engine.state.players["B"].mana_pool["U"] = 2
        self.prepare_main(session)
        action = self.cast_action(engine, card)
        self.assertEqual(
            {"normal"},
            {row["id"] for row in action["cost_options"]},
        )
        engine.permissions.invalidate_current()
        engine._cast(
            "B",
            {"card": card.ref, "cost_option": "normal", "pay": "auto"},
        )
        engine.state.priority_player = None
        engine._prepare_stack_resolution()
        self.assertEqual("graveyard", card.zone)
        self.assertNotIn(FLASHBACK_CAST_ANNOTATION, card.annotations)

    def test_partial_card_withholds_flashback_permission(self):
        session = self.session(70234004, players=2)
        engine = session.engine
        card = self.add_card(session, name="Alter Reality", ref="FLASH4")
        engine.state.players["B"].mana_pool["U"] = 2
        self.prepare_main(session)
        self.assertFalse(
            any(
                row.get("card") == card.ref
                for row in engine._priority_action_hints("B")["actions"]
            )
        )

    def test_stale_flashback_contract_rolls_back(self):
        session = self.session(70234005, players=2)
        engine = session.engine
        card = self.add_card(session, name="Think Twice", ref="FLASH5")
        engine.state.players["B"].mana_pool["U"] = 3
        self.prepare_main(session)
        before_pool = dict(engine.state.players["B"].mana_pool)
        with mock.patch(
            "quorune.rules.casting.commit.compiled_fixed_mana_flashback_spec",
            return_value=None,
        ):
            with self.assertRaisesRegex(GameRuleError, "contract changed"):
                engine._cast(
                    "B",
                    {
                        "card": card.ref,
                        "from": "graveyard",
                        "cost_option": FLASHBACK_CAST_OPTION_ID,
                        "pay": "auto",
                    },
                )
        self.assertEqual("graveyard", card.zone)
        self.assertEqual(before_pool, engine.state.players["B"].mana_pool)
        self.assertFalse(engine.state.stack)


if __name__ == "__main__":
    unittest.main()
