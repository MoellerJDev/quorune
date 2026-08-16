from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest import mock

from common import keep_all, load_assets, make_session
from quorune.card_programs import compile_card_program
from quorune.carddb import CardRecord
from quorune.compiler.action_permission_templates import (
    static_action_permission_handler,
)
from quorune.model import CardInstance
from quorune.oracle_ir import register_generated_programs
from quorune.record import checkpoint_envelope, replay_record
from quorune.rules.capabilities import load_default_capability_registry
from quorune.semantic_runtime.action_permissions import (
    ACTION_PERMISSION_EVENT,
    ACTIVATE_CONTROLLED_CREATURE_AS_HASTE_HANDLER_ID,
    LAND_PLAY_FROM_OWN_GRAVEYARD_HANDLER_ID,
    ActionPermissionKind,
    controller_action_permissions,
    default_action_permission_registry,
)
from quorune.semantic_runtime.context import SemanticNodeError


class _NoRulingsDatabase:
    @staticmethod
    def rulings(record):
        del record
        return ()


def _permanent(
    text: str,
    *,
    suffix: int,
    name: str = "Action Permission Fixture",
    faces: tuple[dict[str, object], ...] = (),
) -> CardRecord:
    return CardRecord(
        oracle_id=f"00000000-0000-4000-8000-{suffix:012d}",
        name=name,
        mana_cost="{3}",
        mana_value=3.0,
        type_line="Artifact",
        oracle_text=text,
        power=None,
        toughness=None,
        loyalty=None,
        defense=None,
        colors=(),
        color_identity=(),
        keywords=(),
        produced_mana=(),
        layout="transform" if faces else "normal",
        released_at="2026-01-01",
        legalities={"commander": "legal"},
        faces=faces,
        raw={},
    )


class StaticActionPermissionCompilerTests(unittest.TestCase):
    def setUp(self):
        self.capabilities = load_default_capability_registry()

    def compile(self, record: CardRecord, *, trust_level: str = "trusted"):
        return compile_card_program(
            _NoRulingsDatabase(),
            record,
            capability_registry=self.capabilities,
            capability_profile="commander_review",
            trust_level=trust_level,
        )

    def test_closed_permission_sentences_compile_face_pinned_typed_programs(
        self,
    ):
        cases = (
            (
                "You may play lands from your graveyard.",
                LAND_PLAY_FROM_OWN_GRAVEYARD_HANDLER_ID,
                "land.play.from_own_graveyard",
            ),
            (
                "You may activate abilities of creatures you control as "
                "though those creatures had haste.",
                ACTIVATE_CONTROLLED_CREATURE_AS_HASTE_HANDLER_ID,
                "activation.permission.controlled_creature_as_haste",
            ),
        )
        for index, (text, handler_id, capability_id) in enumerate(cases, 1):
            with self.subTest(text=text):
                card_program = self.compile(
                    _permanent(text, suffix=116_300_000 + index)
                )
                self.assertEqual((), card_program.residuals)
                ability = next(
                    ability
                    for ability in card_program.abilities
                    if any(
                        descriptor.get("handler_id") == handler_id
                        for descriptor in ability.handlers
                    )
                )
                self.assertEqual("battlefield", ability.active_zone)
                self.assertEqual(ACTION_PERMISSION_EVENT, ability.event)
                self.assertEqual("front", ability.provenance["face_id"])
                self.assertEqual(1, ability.provenance["source_span"]["line"])
                self.assertEqual(
                    len(text),
                    ability.provenance["source_span"]["end"]
                    - ability.provenance["source_span"]["start"],
                )
                self.assertIn(capability_id, ability.capability_dependencies)

        back_text = cases[0][0]
        two_face = _permanent(
            f"Front text\n//\n{back_text}",
            suffix=116_300_003,
            name="Permission Front // Permission Back",
            faces=(
                {
                    "name": "Permission Front",
                    "mana_cost": "{3}",
                    "type_line": "Artifact",
                    "oracle_text": "Front text",
                    "keywords": [],
                },
                {
                    "name": "Permission Back",
                    "mana_cost": "",
                    "type_line": "Artifact",
                    "oracle_text": back_text,
                    "keywords": [],
                },
            ),
        )
        permission = next(
            ability
            for ability in self.compile(two_face).abilities
            if any(
                descriptor.get("handler_id")
                == LAND_PLAY_FROM_OWN_GRAVEYARD_HANDLER_ID
                for descriptor in ability.handlers
            )
        )
        self.assertEqual("Permission Back", permission.provenance["face_id"])

    def test_unsupported_permission_wording_and_malformed_descriptors_fail_closed(
        self,
    ):
        unsupported = (
            "You may play an additional land from your graveyard.",
            "You may play lands from graveyards.",
            "You may activate abilities of creatures your opponents control "
            "as though those creatures had haste.",
        )
        for index, text in enumerate(unsupported, 1):
            with self.subTest(text=text):
                card_program = self.compile(
                    _permanent(text, suffix=116_301_000 + index),
                    trust_level="provisional",
                )
                self.assertTrue(card_program.residuals)
                self.assertIn(
                    text,
                    {row["text"] for row in card_program.residuals},
                )
                self.assertFalse(
                    any(
                        ability.event == ACTION_PERMISSION_EVENT
                        for ability in card_program.abilities
                    )
                )

        compiled = static_action_permission_handler(
            "You may play lands from your graveyard."
        )
        self.assertIsNotNone(compiled)
        registry = default_action_permission_registry()
        descriptor = compiled[1]
        registry.validate(descriptor)
        malformed_values = (
            {**descriptor, "unknown": True},
            {**descriptor, "schema_version": True},
            {**descriptor, "schema_version": 2},
            {**descriptor, "event": "continuous"},
            {
                **descriptor,
                "permission": (
                    ActionPermissionKind.ACTIVATE_CONTROLLED_CREATURE_AS_HASTE.value
                ),
            },
        )
        for malformed in malformed_values:
            with self.subTest(malformed=malformed):
                with self.assertRaises(SemanticNodeError):
                    registry.validate(malformed)

    def test_action_permission_compiler_mutant_is_killed(self):
        records = (
            _permanent(
                "You may play lands from your graveyard.",
                suffix=116_302_001,
            ),
            _permanent(
                "You may activate abilities of creatures you control as "
                "though those creatures had haste.",
                suffix=116_302_002,
            ),
        )

        def assert_compiler_boundary() -> None:
            for record in records:
                card_program = self.compile(
                    record,
                    trust_level="provisional",
                )
                self.assertTrue(
                    any(
                        ability.event == ACTION_PERMISSION_EVENT
                        for ability in card_program.abilities
                    )
                )

        assert_compiler_boundary()
        with mock.patch(
            "quorune.compiler.runtime_templates."
            "static_action_permission_handler",
            return_value=None,
        ):
            with self.assertRaises(AssertionError):
                assert_compiler_boundary()


class StaticActionPermissionRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db, cls.mishra, cls.zimone = load_assets()
        cls.capabilities = load_default_capability_registry()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def session(self, seed: int):
        session = make_session(
            self.db,
            self.mishra,
            self.zimone,
            players=4,
            seed=seed,
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
    def card(engine, owner: str, name: str):
        return next(
            card
            for card in engine.state.cards.values()
            if card.owner == owner and card.printed_name == name
        )

    def add_permanent(
        self,
        session,
        *,
        seat: str,
        name: str,
        ref: str,
    ) -> CardInstance:
        engine = session.engine
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
            acquired_control_turn_count=-1,
            known_to=list(engine.seats),
            revealed_to=list(engine.seats),
        )
        engine.state.cards[card.object_id] = card
        engine.state.players[seat].zones["battlefield"].append(card.object_id)
        register_generated_programs(
            self.db,
            engine.semantics,
            (record,),
            trust_level="provisional",
            capability_registry=self.capabilities,
            capability_profile=engine.state.config.review_profile,
            promote_exact_runtime_handlers=True,
            promote_exact_capability_declarations=True,
        )
        return card

    @staticmethod
    def prepare_main(session, seat: str) -> None:
        engine = session.engine
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.state.priority_passes = []
        engine.state.active_player = seat
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine.state.started = True
        engine._grant_priority(seat)
        engine.pump()

    def test_land_play_permission_is_typed_active_and_seat_scoped(self):
        session = self.session(116_303_001)
        engine = session.engine
        crucible = self.add_permanent(
            session,
            seat="B",
            name="Crucible of Worlds",
            ref="B-crucible",
        )
        land = self.card(engine, "B", "Island")
        engine.move_card(land.object_id, "graveyard", log=False)
        engine.state.players["B"].land_plays_remaining = 1
        self.prepare_main(session, "B")

        permissions = controller_action_permissions(engine, "B")
        self.assertEqual(
            [ActionPermissionKind.LAND_PLAY_FROM_OWN_GRAVEYARD],
            [permission.kind for permission in permissions],
        )
        self.assertIn(land.ref, engine._priority_action_hints("B")["lands"])
        self.assertFalse(engine._compiled_land_play_permission("A", land))

        crucible.phased_out = True
        self.assertFalse(engine._compiled_land_play_permission("B", land))
        crucible.phased_out = False
        engine._play_land("B", {"card": land.ref, "from": "graveyard"})
        self.assertEqual("battlefield", land.zone)

    def test_creature_activation_permission_is_typed_active_and_seat_scoped(
        self,
    ):
        session = self.session(116_303_002)
        engine = session.engine
        elixir = self.add_permanent(
            session,
            seat="B",
            name="Thousand-Year Elixir",
            ref="B-elixir",
        )
        bird = self.card(engine, "B", "Birds of Paradise")
        engine.move_card(bird.object_id, "battlefield", controller="B", log=False)
        bird.acquired_control_turn_count = engine.state.players["B"].turns_begun
        ability = engine._activated_abilities(bird)[0]

        self.assertTrue(engine._may_activate_creature_as_haste("B", bird))
        self.assertFalse(engine._may_activate_creature_as_haste("A", bird))
        self.assertEqual(
            ("payable", None),
            engine._ability_availability("B", bird, ability),
        )

        elixir.phased_out = True
        self.assertFalse(engine._may_activate_creature_as_haste("B", bird))
        self.assertNotEqual(
            "payable",
            engine._ability_availability("B", bird, ability)[0],
        )

    def test_raw_oracle_text_without_typed_permission_fails_closed(self):
        session = self.session(116_303_003)
        engine = session.engine
        crucible = self.add_permanent(
            session,
            seat="B",
            name="Crucible of Worlds",
            ref="B-raw-crucible",
        )
        elixir = self.add_permanent(
            session,
            seat="B",
            name="Thousand-Year Elixir",
            ref="B-raw-elixir",
        )
        land = self.card(engine, "B", "Island")
        bird = self.card(engine, "B", "Birds of Paradise")
        engine.move_card(land.object_id, "graveyard", log=False)
        engine.move_card(bird.object_id, "battlefield", controller="B", log=False)

        self.assertIn(
            "play lands from your graveyard",
            self.db.lookup(crucible.printed_name).oracle_text.casefold(),
        )
        self.assertIn(
            "as though those creatures had haste",
            self.db.lookup(elixir.printed_name).oracle_text.casefold(),
        )
        for source in (crucible, elixir):
            for program in tuple(
                engine.semantics.runtime_handler_programs_for_oracle(
                    source.oracle_id,
                    active_zone="battlefield",
                    event=ACTION_PERMISSION_EVENT,
                )
            ):
                engine.semantics.remove(program.key)

        self.assertFalse(engine._compiled_land_play_permission("B", land))
        self.assertFalse(engine._may_activate_creature_as_haste("B", bird))

    def test_permission_offers_are_principal_scoped(self):
        session = self.session(116_303_005)
        engine = session.engine
        self.add_permanent(
            session,
            seat="B",
            name="Crucible of Worlds",
            ref="B-private-crucible",
        )
        self.add_permanent(
            session,
            seat="B",
            name="Thousand-Year Elixir",
            ref="B-private-elixir",
        )
        land = self.card(engine, "B", "Island")
        bird = self.card(engine, "B", "Birds of Paradise")
        engine.move_card(land.object_id, "graveyard", log=False)
        engine.move_card(bird.object_id, "battlefield", controller="B", log=False)
        bird.acquired_control_turn_count = engine.state.players["B"].turns_begun
        engine.state.players["B"].land_plays_remaining = 1
        self.prepare_main(session, "B")

        owner_decision = session.packet("pilot:B", full=True)["decision"]
        opposing_decision = session.packet("pilot:A", full=True)["decision"]
        owner_actions = owner_decision["ctx"]["legal"]["actions"]
        opposing_actions = (
            opposing_decision.get("ctx", {}).get("legal", {}).get("actions", [])
            if isinstance(opposing_decision, dict)
            else []
        )
        self.assertIn(
            land.ref,
            {
                action.get("card")
                for action in owner_actions
                if action.get("kind") == "play_land"
            },
        )
        self.assertIn(
            bird.ref,
            {
                action.get("source")
                for action in owner_actions
                if action.get("kind") == "activate"
            },
        )
        self.assertNotIn(
            land.ref,
            {action.get("card") for action in opposing_actions},
        )
        self.assertNotIn(
            bird.ref,
            {action.get("source") for action in opposing_actions},
        )

    def test_land_play_from_graveyard_replays_exactly(self):
        session = self.session(116_303_004)
        engine = session.engine
        self.add_permanent(
            session,
            seat="B",
            name="Crucible of Worlds",
            ref="B-replay-crucible",
        )
        land = self.card(engine, "B", "Island")
        engine.move_card(land.object_id, "graveyard", log=False)
        engine.state.players["B"].land_plays_remaining = 1
        self.prepare_main(session, "B")
        session.initial_checkpoint = checkpoint_envelope(session.state)
        session.commands.clear()
        session.decisions.clear()

        action = next(
            action
            for action in engine._priority_action_hints("B")["actions"]
            if action.get("kind") == "play_land"
            and action.get("card") == land.ref
        )
        result = session.act(
            "pilot:B",
            {"action_id": action["id"]},
        )
        self.assertTrue(result.ok, result.summary)
        self.assertEqual("battlefield", land.zone)

        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "graveyard-land-play-replay"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)


if __name__ == "__main__":
    unittest.main()
