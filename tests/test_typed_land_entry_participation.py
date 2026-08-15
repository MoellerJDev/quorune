from __future__ import annotations

from dataclasses import replace
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common import DB_PATH, keep_all, load_assets, make_session
from quorune.card_programs.adapters import compile_card_program
from quorune.carddb import CardDatabase, CardRecord
from quorune.compiler.entry_state_templates import static_entry_state_handler
from quorune.engine import GameRuleError
from quorune.entry_counters import capture_prospective_entry_characteristics
from quorune.model import CardInstance
from quorune.oracle_ir import generated_programs
from quorune.projection import StateProjector
from quorune.record import (
    authoritative_state_hash,
    checkpoint_envelope,
    replay_record,
)
from quorune.replacement_effects import ReplacementChoiceRequired
from quorune.rules.capabilities import load_default_capability_registry
from quorune.semantic_runtime import prepare_zone_change_replacement
from quorune.semantic_runtime import typed_entry_life_payment_amount
from quorune.targets import TargetGroup


def _record(text: str, *, name: str = "Typed Entry Fixture") -> CardRecord:
    return CardRecord(
        oracle_id="00000000-0000-4000-8000-000000614012",
        name=name,
        mana_cost="",
        mana_value=0,
        type_line="Land",
        oracle_text=text,
        power=None,
        toughness=None,
        loyalty=None,
        defense=None,
        colors=(),
        color_identity=(),
        keywords=(),
        produced_mana=("G",),
        layout="normal",
        released_at="2026-01-01",
        legalities={"commander": "legal"},
        faces=(),
        raw={},
    )


class TypedLandEntryCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db = CardDatabase(DB_PATH)
        cls.capabilities = load_default_capability_registry()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

    def test_closed_entry_state_family_lowers_to_capability_closed_programs(self):
        cases = (
            ("This land enters tapped.", "zone-entry-state-self-tapped-v1"),
            (
                "This land enters tapped unless you have two or more opponents.",
                "zone-entry-state-self-minimum-2-opponents-v1",
            ),
            (
                "This land enters tapped unless you control a Forest or an Island.",
                "zone-entry-state-self-controlled-basic-types-v1",
            ),
            (
                "As this land enters, you may pay 2 life. If you don't, it enters tapped.",
                "zone-entry-state-self-pay-2-life-v1",
            ),
            (
                "Lands you control enter untapped.",
                "zone-entry-state-controlled-lands-untapped-v1",
            ),
        )
        for index, (text, template_id) in enumerate(cases):
            with self.subTest(text=text):
                lowered = static_entry_state_handler(
                    text, source_name="Typed Entry Fixture"
                )
                self.assertIsNotNone(lowered)
                self.assertEqual(template_id, lowered[0])
                self.assertEqual("zone.entry.tapped_state", lowered[2])
                program = compile_card_program(
                    self.db,
                    replace(
                        _record(text),
                        oracle_id=(
                            f"00000000-0000-4000-8000-{614012 + index:012d}"
                        ),
                    ),
                    capability_registry=self.capabilities,
                    capability_profile="commander_review",
                    trust_level="trusted",
                )
                self.assertEqual(
                    ("zone.entry.tapped_state",),
                    program.capability_dependencies,
                )
                self.assertTrue(program.trust_closure["trusted"])
                self.assertEqual([], program.to_dict()["residuals"])

    def test_entry_state_near_misses_remain_residual(self):
        variants = (
            "This land enters tapped unless you control a Gate.",
            "This land enters tapped unless an opponent has two creatures.",
            "As this land enters, you may pay X life. If you don't, it enters tapped.",
            "Lands your opponents control enter untapped.",
            "This land may enter tapped.",
        )
        for text in variants:
            with self.subTest(text=text):
                self.assertIsNone(
                    static_entry_state_handler(
                        text, source_name="Typed Entry Fixture"
                    )
                )

    def test_entry_state_probe_without_source_identity_fails_closed(self):
        self.assertIsNone(
            static_entry_state_handler(
                "If you would draw a card, draw two cards instead.",
                source_name="",
            )
        )
        self.assertIsNotNone(
            static_entry_state_handler(
                "This land enters tapped.",
                source_name="",
            )
        )

    def test_entry_state_compiler_mutation_is_killed(self):
        record = _record("This land enters tapped.")
        ordinary = compile_card_program(
            self.db,
            record,
            capability_registry=self.capabilities,
            capability_profile="commander_review",
            trust_level="trusted",
        )
        self.assertTrue(ordinary.trust_closure["trusted"])
        with patch(
            "quorune.compiler.runtime_templates.static_entry_state_handler",
            return_value=None,
        ):
            mutant = compile_card_program(
                self.db,
                record,
                capability_registry=self.capabilities,
                capability_profile="commander_review",
                trust_level="provisional",
            )
        self.assertFalse(mutant.trust_closure["trusted"])
        self.assertTrue(mutant.to_dict()["residuals"])


class TypedLandEntryRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db, cls.mishra, cls.zimone = load_assets()
        cls.capabilities = load_default_capability_registry()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

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
        engine = session.engine
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine.state.priority_passes = []
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
        zone: str = "hand",
        register_all: bool = False,
    ) -> CardInstance:
        record = self.db.lookup(name)
        self.assertIsNotNone(record, name)
        card = CardInstance(
            object_id=f"typed-entry:{ref}",
            ref=ref,
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner=seat,
            controller=seat,
            zone=zone,
            zone_timestamp=engine.state.timestamp_sequence + 1,
            known_to=list(engine.seats),
            revealed_to=list(engine.seats),
        )
        engine.state.cards[card.object_id] = card
        engine.state.players[seat].zones[zone].append(card.object_id)
        if register_all or any(
            static_entry_state_handler(line, source_name=record.name)
            is not None
            for line in record.oracle_text.splitlines()
        ):
            for program in generated_programs(
                self.db,
                record,
                trust_level="trusted",
                capability_registry=self.capabilities,
                capability_profile="commander_review",
            ):
                if register_all or any(
                    handler.get("handler_id")
                    == "replacement.zone.entry-state.v1"
                    for handler in program.handlers
                ):
                    engine.semantics.put(program)
        return card

    @staticmethod
    def stage_main(engine, seat: str = "A") -> None:
        engine.state.active_player = seat
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine.state.priority_player = seat
        engine.state.priority_passes = []
        engine.state.players[seat].land_plays_remaining = 2

    @staticmethod
    def issue_priority(engine, seat: str = "A") -> None:
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = seat
        engine.state.priority_passes = []
        engine._grant_priority(seat)
        engine._issue_priority(seat)

    def legal_actions(self, session, seat: str = "A") -> list[dict]:
        decision = session.packet(f"pilot:{seat}", full=True)["decision"]
        self.assertIsNotNone(decision)
        return list(decision["legal_actions"])

    def existing_creature(self, engine, seat: str):
        return next(
            card
            for card in engine.state.cards.values()
            if card.owner == seat
            and not card.is_commander
            and "creature"
            in str(
                engine._effective_card_data(card).get("type_line") or ""
            ).casefold()
        )

    def test_land_entry_families_use_typed_snapshot_and_canonical_owners(self):
        session = self.session(6140121)
        engine = session.engine
        shock = self.add_card(engine, seat="A", name="Steam Vents", ref="L1")
        bond = self.add_card(engine, seat="A", name="Sea of Clouds", ref="L2")
        check = self.add_card(engine, seat="A", name="Hinterland Harbor", ref="L3")
        forest = self.add_card(engine, seat="A", name="Forest", ref="L4")

        life_before = engine.state.players["A"].life
        engine.move_card(
            shock.object_id,
            "battlefield",
            controller="A",
            entry_pay_life=True,
            log=False,
        )
        self.assertFalse(shock.tapped)
        self.assertEqual(life_before - 2, engine.state.players["A"].life)
        engine.move_card(bond.object_id, "battlefield", controller="A", log=False)
        self.assertFalse(bond.tapped)
        engine.move_card(forest.object_id, "battlefield", controller="A", log=False)
        engine.move_card(check.object_id, "battlefield", controller="A", log=False)
        self.assertFalse(check.tapped)

    def test_bond_land_uses_current_four_player_opponent_count(self):
        four = self.session(6140122, players=4)
        bond = self.add_card(
            four.engine, seat="A", name="Sea of Clouds", ref="L5"
        )
        four.engine.move_card(
            bond.object_id, "battlefield", controller="A", log=False
        )
        self.assertFalse(bond.tapped)

        duel = self.session(6140123, players=2)
        duel_bond = self.add_card(
            duel.engine, seat="A", name="Sea of Clouds", ref="L6"
        )
        duel.engine.move_card(
            duel_bond.object_id, "battlefield", controller="A", log=False
        )
        self.assertTrue(duel_bond.tapped)

    def test_shock_land_payment_is_prepared_before_zone_mutation(self):
        session = self.session(6140124)
        engine = session.engine
        shock = self.add_card(engine, seat="A", name="Steam Vents", ref="L7")
        engine.state.players["A"].life = 1
        before = copy.deepcopy(engine.state)
        with self.assertRaisesRegex(GameRuleError, "Cannot pay more life"):
            engine.move_card(
                shock.object_id,
                "battlefield",
                controller="A",
                entry_pay_life=True,
                log=False,
            )
        self.assertEqual("hand", shock.zone)
        self.assertEqual(before.players["A"].life, engine.state.players["A"].life)
        self.assertIn(shock.object_id, engine.state.players["A"].zones["hand"])

    def test_ambient_untapped_competes_with_intrinsic_tapped_entry(self):
        session = self.session(6140125)
        engine = session.engine
        ambient = self.add_card(
            engine, seat="A", name="Spelunking", ref="E1", zone="battlefield"
        )
        ambient.controller = "A"
        land = self.add_card(
            engine, seat="A", name="Temple of Mystery", ref="L8"
        )
        with self.assertRaises(ReplacementChoiceRequired) as caught:
            engine.move_card(
                land.object_id, "battlefield", controller="A", log=False
            )
        self.assertEqual("hand", land.zone)
        legal = caught.exception.pending.choice.legal_selections
        intrinsic = next(value for value in legal if land.ref in value)
        engine.move_card(
            land.object_id,
            "battlefield",
            controller="A",
            replacement_selections=(intrinsic,),
            log=False,
        )
        self.assertFalse(land.tapped)

    def test_entry_preparation_rejects_stale_face_and_rolls_back(self):
        session = self.session(6140126)
        engine = session.engine
        card = self.add_card(
            engine,
            seat="A",
            name="Barkchannel Pathway // Tidechannel Pathway",
            ref="M1",
        )
        front, _ = capture_prospective_entry_characteristics(
            engine, card=card, enter_face="Barkchannel Pathway"
        )
        prepared = prepare_zone_change_replacement(
            engine,
            card,
            "battlefield",
            destination_controller="A",
            entry_characteristics=front,
            error_type=GameRuleError,
        )
        back, _ = capture_prospective_entry_characteristics(
            engine, card=card, enter_face="Tidechannel Pathway"
        )
        with self.assertRaisesRegex(GameRuleError, "does not match"):
            prepare_zone_change_replacement(
                engine,
                card,
                "battlefield",
                destination_controller="A",
                entry_characteristics=back,
                prepared=prepared,
                error_type=GameRuleError,
            )
        self.assertEqual("hand", card.zone)

    def test_selected_mdfc_face_isolates_entry_program(self):
        session = self.session(61401261)
        engine = session.engine
        record = self.db.lookup(
            "Agadeem's Awakening // Agadeem, the Undercrypt"
        )
        self.assertIsNotNone(record)
        card = CardInstance(
            object_id="typed-entry:mdfc-shock",
            ref="M2",
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner="A",
            controller="A",
            zone="hand",
            known_to=["A"],
            revealed_to=[],
        )
        engine.state.cards[card.object_id] = card
        engine.state.players["A"].zones["hand"].append(card.object_id)
        for program in generated_programs(
            self.db,
            record,
            trust_level="trusted",
            capability_registry=self.capabilities,
            capability_profile="commander_review",
        ):
            engine.semantics.put(program)
        self.assertEqual(
            0,
            typed_entry_life_payment_amount(
                engine,
                record,
                card=card,
                prospective_name="Agadeem's Awakening",
            ),
        )
        self.assertEqual(
            3,
            typed_entry_life_payment_amount(
                engine,
                record,
                card=card,
                prospective_name="Agadeem, the Undercrypt",
            ),
        )

    def test_glasswing_faces_compose_aura_attachment_with_tapped_entry(self):
        session = self.session(61401263)
        engine = session.engine
        land = self.add_card(
            engine,
            seat="A",
            name="Glasswing Grace // Age-Graced Chapel",
            ref="G1",
            register_all=True,
        )
        aura = self.add_card(
            engine,
            seat="A",
            name="Glasswing Grace // Age-Graced Chapel",
            ref="G2",
            register_all=True,
        )
        target_ref = engine.create_token(
            "A",
            name="Assurance Creature",
            characteristics={
                "type_line": "Token Creature — Test",
                "colors": ["W"],
                "power": "2",
                "toughness": "2",
                "keywords": [],
            },
        )[0]
        target = engine._resolve_object(
            "A", target_ref, zones={"battlefield"}
        )
        engine.state.players["A"].mana_pool["W"] = 5
        self.stage_main(engine)
        self.issue_priority(engine)

        land_action = next(
            action
            for action in self.legal_actions(session)
            if action["id"] == f"play-land:{land.ref}"
        )
        played = session.act("pilot:A", {"action_id": land_action["id"]})
        self.assertTrue(played.ok, played.summary)
        self.assertEqual("battlefield", land.zone)
        self.assertEqual("Age-Graced Chapel", land.active_face)
        self.assertTrue(land.tapped)

        cast_action = next(
            action
            for action in self.legal_actions(session)
            if action["id"] == f"cast:{aura.ref}"
        )
        self.assertIn(target.ref, cast_action["target_schema"]["legal_refs"])
        cast = session.act(
            "pilot:A",
            {
                "action_id": cast_action["id"],
                "targets": [target.ref],
                "pay": "manual",
                "payment": {"W": 5},
            },
        )
        self.assertTrue(cast.ok, cast.summary)
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine._prepare_stack_resolution()

        self.assertEqual("battlefield", aura.zone)
        self.assertEqual("Glasswing Grace", aura.active_face)
        self.assertEqual(target.object_id, aura.attached_to)
        characteristics = engine._effective_card_data(target)
        self.assertEqual("4", characteristics["power"])
        self.assertEqual("4", characteristics["toughness"])
        self.assertGreaterEqual(
            {keyword.casefold() for keyword in characteristics["keywords"]},
            {"flying", "lifelink"},
        )

    def test_lotus_field_composes_tapped_entry_with_controller_relative_hexproof(
        self,
    ):
        session = self.session(61401264)
        engine = session.engine
        field = self.add_card(
            engine,
            seat="B",
            name="Lotus Field",
            ref="LF1",
            register_all=True,
        )
        engine.move_card(
            field.object_id,
            "battlefield",
            controller="B",
            log=False,
        )
        self.assertTrue(field.tapped)
        field_keywords = {
            keyword.casefold()
            for keyword in engine._effective_card_data(field)["keywords"]
        }
        self.assertIn(
            "hexproof",
            field_keywords,
        )

        group = TargetGroup.from_mapping(
            {
                "zones": ["battlefield"],
                "categories": ["permanent"],
            }
        )
        source_a = next(
            card
            for card in engine.state.cards.values()
            if card.owner == "A"
        )
        row_a = next(
            row
            for row in engine._target_candidate_rows("A", group)
            if row["ref"] == field.ref
        )
        self.assertFalse(
            engine._target_row_matches(
                "A", group, row_a, source_ref=source_a.ref, as_target=True
            )
        )
        self.assertTrue(
            engine._target_row_matches(
                "A", group, row_a, source_ref=source_a.ref, as_target=False
            )
        )
        source_b = next(
            card
            for card in engine.state.cards.values()
            if card.owner == "B" and card is not field
        )
        row_b = next(
            row
            for row in engine._target_candidate_rows("B", group)
            if row["ref"] == field.ref
        )
        self.assertTrue(
            engine._target_row_matches(
                "B", group, row_b, source_ref=source_b.ref, as_target=True
            )
        )

    def test_ruins_of_oran_rief_composes_tapped_entry_with_characteristic_target(
        self,
    ):
        session = self.session(61401266)
        engine = session.engine
        ruins = self.add_card(
            engine,
            seat="A",
            name="Ruins of Oran-Rief",
            ref="ROR1",
            register_all=True,
        )
        target_ref = engine.create_token(
            "A",
            name="Colorless Entrant",
            characteristics={
                "type_line": "Token Creature — Construct",
                "colors": [],
                "power": "1",
                "toughness": "1",
                "keywords": [],
            },
        )[0]
        target = engine._resolve_object(
            "A", target_ref, zones={"battlefield"}
        )
        self.assertEqual(
            engine.state.turn_sequence,
            target.entered_battlefield_turn_sequence,
        )
        engine.move_card(
            ruins.object_id,
            "battlefield",
            controller="A",
            log=False,
        )
        self.assertTrue(ruins.tapped)

        self.stage_main(engine)
        self.issue_priority(engine)
        action_id = f"activate:{ruins.ref}:ab3"
        self.assertNotIn(
            action_id,
            {action["id"] for action in self.legal_actions(session)},
        )

        ruins.tapped = False
        self.issue_priority(engine)
        action = next(
            action
            for action in self.legal_actions(session)
            if action["id"] == action_id
        )
        self.assertIn(target.ref, action["target_schema"]["legal_refs"])
        activated = session.act(
            "pilot:A",
            {"action_id": action_id, "targets": [target.ref]},
        )
        self.assertTrue(activated.ok, activated.summary)
        self.assertTrue(ruins.tapped)
        for seat in engine.seats:
            passed = session.act(f"pilot:{seat}", {"action_id": "pass"})
            self.assertTrue(passed.ok, passed.summary)
        self.assertEqual(1, target.counters.get("+1/+1", 0))

    def test_fell_faces_compose_target_revalidation_with_tapped_entry(self):
        session = self.session(61401265)
        engine = session.engine
        land = self.add_card(
            engine,
            seat="A",
            name="Fell the Profane // Fell Mire",
            ref="F1",
            register_all=True,
        )
        spell = self.add_card(
            engine,
            seat="A",
            name="Fell the Profane // Fell Mire",
            ref="F2",
            register_all=True,
        )
        target = self.existing_creature(engine, "B")
        engine.move_card(
            target.object_id,
            "battlefield",
            controller="B",
            log=False,
        )
        engine.state.players["A"].mana_pool["B"] = 4
        self.stage_main(engine)
        self.issue_priority(engine)

        played = session.act(
            "pilot:A", {"action_id": f"play-land:{land.ref}"}
        )
        self.assertTrue(played.ok, played.summary)
        self.assertEqual("Fell Mire", land.active_face)
        self.assertTrue(land.tapped)

        cast_action = next(
            action
            for action in self.legal_actions(session)
            if action["id"] == f"cast:{spell.ref}"
        )
        self.assertIn("target_schema", cast_action, cast_action)
        self.assertIn(target.ref, cast_action["target_schema"]["legal_refs"])
        cast = session.act(
            "pilot:A",
            {
                "action_id": cast_action["id"],
                "targets": [target.ref],
                "pay": "manual",
                "payment": {"B": 4},
            },
        )
        self.assertTrue(cast.ok, cast.summary)
        self.assertEqual("stack", spell.zone)
        engine.move_card(target.object_id, "hand", log=False)
        engine.permissions.invalidate_current()
        engine.state.pending_decision = None
        engine.state.priority_player = None
        engine._prepare_stack_resolution()

        self.assertFalse(engine.state.stack)
        self.assertEqual("graveyard", spell.zone)
        self.assertEqual("hand", target.zone)

    def test_agadeem_residual_spell_stays_fail_closed_while_land_entry_executes(
        self,
    ):
        session = self.session(61401266)
        engine = session.engine
        card = self.add_card(
            engine,
            seat="A",
            name="Agadeem's Awakening // Agadeem, the Undercrypt",
            ref="A1",
            register_all=True,
        )
        engine.state.config.semantic_policy = "trusted_only"
        engine.state.players["A"].mana_pool["B"] = 3
        self.stage_main(engine)
        self.issue_priority(engine)
        actions = self.legal_actions(session)
        self.assertIn(
            f"play-land:{card.ref}", {action["id"] for action in actions}
        )
        self.assertNotIn(
            f"cast:{card.ref}", {action["id"] for action in actions}
        )

        before = authoritative_state_hash(engine.state)
        rejected = session.act(
            "pilot:A", {"action_id": f"cast:{card.ref}"}
        )
        self.assertFalse(rejected.ok)
        self.assertEqual(before, authoritative_state_hash(engine.state))
        played = session.act(
            "pilot:A", {"action_id": f"play-land:{card.ref}"}
        )
        self.assertTrue(played.ok, played.summary)
        self.assertEqual("battlefield", card.zone)
        self.assertEqual("Agadeem, the Undercrypt", card.active_face)
        self.assertTrue(card.tapped)

    def test_only_historical_v3_registry_can_use_entry_adapter(self):
        session = self.session(61401262)
        engine = session.engine
        current = self.add_card(
            engine, seat="A", name="Temple of Mystery", ref="H1"
        )
        historical = self.add_card(
            engine, seat="A", name="Temple of Mystery", ref="H2"
        )
        for program in tuple(
            engine.semantics.programs_for_oracle(
                current.oracle_id,
                active_zone="all",
                event="zone.change",
            )
        ):
            if any(
                descriptor.get("handler_id")
                == "replacement.zone.entry-state.v1"
                for descriptor in program.handlers
            ):
                engine.semantics.remove(program.key)
        engine.semantics._runtime_handler_compatibility.pop(
            (current.oracle_id, "all", "zone.change"), None
        )

        engine.move_card(
            current.object_id, "battlefield", controller="A", log=False
        )
        self.assertFalse(current.tapped)

        # Missing compatibility metadata is the historical Game Record v3
        # signal established by SemanticRegistry.load().
        engine.semantics._runtime_handler_compatibility_enabled = True
        engine.move_card(
            historical.object_id, "battlefield", controller="A", log=False
        )
        self.assertTrue(historical.tapped)

    def test_competing_land_entry_choice_is_private_and_replayable(self):
        session = self.session(6140127)
        engine = session.engine
        ambient = next(
            card
            for card in engine.state.cards.values()
            if card.owner == "B" and card.printed_name == "Spelunking"
        )
        land = next(
            card
            for card in engine.state.cards.values()
            if card.owner == "A" and card.printed_name == "Steam Vents"
        )
        engine.move_card(
            ambient.object_id,
            "battlefield",
            controller="A",
            log=False,
        )
        if land.zone != "hand":
            engine.move_card(land.object_id, "hand", log=False)
        self.stage_main(engine)
        engine._grant_priority("A")
        engine._issue_priority("A")
        session.initial_checkpoint = checkpoint_envelope(engine.state)
        session.commands.clear()
        session.decisions.clear()
        result = session.act("pilot:A", {"action_id": f"play-land:{land.ref}"})
        self.assertTrue(result.ok, result.summary)
        land = engine.state.cards[land.object_id]
        self.assertEqual("replacement.order", engine.state.pending_decision.kind)
        self.assertEqual(["A"], engine.state.pending_decision.actors)
        projector = StateProjector(self.db, engine.state)
        projected_a = projector._decision("pilot:A")
        self.assertIsNotNone(projected_a)
        self.assertIsNone(projector._decision("pilot:B"))
        self.assertNotIn("replacement_batch", json.dumps(projected_a))
        self.assertNotIn("priority_response", json.dumps(projected_a))
        self.assertEqual("hand", land.zone)
        selected = projected_a["ctx"]["options"][0]["id"]
        result = session.act(
            "pilot:A",
            {"action_id": "choose", "replacement": selected},
        )
        self.assertTrue(result.ok, result.summary)
        land = engine.state.cards[land.object_id]
        self.assertEqual("battlefield", land.zone)
        with tempfile.TemporaryDirectory() as temporary:
            record_dir = Path(temporary) / "typed-land-entry-record"
            session.save(record_dir)
            replay = replay_record(record_dir, self.db, verify=True)
        self.assertTrue(replay["ok"], replay)
        self.assertEqual(2, replay["commands"])


if __name__ == "__main__":
    unittest.main()
