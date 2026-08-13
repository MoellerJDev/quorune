from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest import mock

from common import keep_all, load_assets, make_session
from quorune.abilities import parse_activated_abilities
from quorune.carddb import CardRecord
from quorune.model import CardInstance, StackItem
from quorune.oracle_ir import generated_programs
from quorune.rules.capabilities import load_default_capability_registry
from quorune.semantic_runtime.casting_activation_metadata import (
    LOYALTY_COST_MODIFIER_EVENT,
)


class _NoRulingsDatabase:
    @staticmethod
    def rulings(record):
        del record
        return ()


class LoyaltyAbilityRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db, cls.mishra, cls.zimone = load_assets()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def make_engine(self, seed: int):
        session = make_session(
            self.db,
            self.mishra,
            self.zimone,
            players=2,
            seed=seed,
        )
        keep_all(session)
        session.engine.permissions.invalidate_current()
        session.engine.state.pending_decision = None
        session.engine.state.priority_player = "A"
        return session.engine

    @staticmethod
    def card(engine, owner: str, name: str):
        return next(
            card
            for card in engine.state.cards.values()
            if card.owner == owner
            and card.is_card_object
            and card.printed_name == name
        )

    @staticmethod
    def prepare_main(engine, seat: str = "A") -> None:
        engine.state.active_player = seat
        engine.state.phase = "precombat_main"
        engine.state.step = "main"
        engine.state.stack.clear()
        engine.state.priority_player = seat
        engine.state.priority_passes = []
        engine.state.pending_decision = None

    @staticmethod
    def add_test_permanent(
        engine,
        *,
        ref: str,
        name: str,
        oracle_text: str,
        type_line: str,
        controller: str = "A",
        loyalty: int = 0,
    ) -> CardInstance:
        card = CardInstance(
            object_id=f"test-loyalty-{ref}",
            ref=ref,
            oracle_id=f"custom-token:test-loyalty-oracle-{ref}",
            printed_name=name,
            owner=controller,
            controller=controller,
            zone="battlefield",
            is_token=True,
            known_to=list(engine.seats),
            revealed_to=list(engine.seats),
            counters={"loyalty": loyalty},
            annotations={
                "loyalty_initialized": True,
                "token_characteristics": {
                    "name": name,
                    "type_line": type_line,
                    "oracle_text": oracle_text,
                    "activated_abilities": [
                        ability.to_dict()
                        for ability in parse_activated_abilities(
                            card_name=name,
                            oracle_text=oracle_text,
                        )
                    ],
                },
            },
        )
        engine.state.cards[card.object_id] = card
        engine.state.players[controller].zones["battlefield"].append(
            card.object_id
        )
        return card

    def test_contract_traces_every_cr_606_rule(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads(
            (
                root
                / "mechanics"
                / "contracts"
                / "loyalty-abilities.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(
            {
                "606",
                "606.1",
                "606.2",
                "606.3",
                "606.4",
                "606.5",
                "606.6",
            },
            {
                rule_id
                for rule_id in contract["rule_references"]
                if str(rule_id).startswith("606")
            },
        )

    def test_loyalty_symbol_defines_ability_on_any_permanent(self):
        engine = self.make_engine(60601)
        relic = self.add_test_permanent(
            engine,
            ref="A-loyalty-relic",
            name="Loyalty Relic",
            type_line="Artifact",
            oracle_text="+1: Scry 1.",
        )
        self.prepare_main(engine)

        ability = engine._activated_abilities(relic)[0]
        self.assertEqual(1, ability.loyalty_delta)
        self.assertEqual(
            ("payable", None),
            engine._ability_availability("A", relic, ability),
        )

        ordinary = parse_activated_abilities(
            card_name="Ordinary Relic",
            oracle_text="{T}: Add {C}.",
        )[0]
        self.assertIsNone(ordinary.loyalty_delta)

    def test_loyalty_timing_control_and_once_per_permanent(self):
        engine = self.make_engine(60602)
        daretti = self.card(engine, "A", "Daretti, Scrap Savant")
        engine.move_card(
            daretti.object_id,
            "battlefield",
            controller="A",
            log=False,
        )
        plus, minus, _ = engine._activated_abilities(daretti)

        self.prepare_main(engine, "A")
        self.assertEqual(
            ("payable", None),
            engine._ability_availability("A", daretti, plus),
        )
        self.assertFalse(
            any(
                hint.get("s") == daretti.ref
                for hint in engine._priority_action_hints("B")["abilities"]
            )
        )

        engine.state.phase = "beginning"
        engine.state.step = "upkeep"
        self.assertEqual(
            ("unavailable", "loyalty_timing"),
            engine._ability_availability("A", daretti, plus),
        )

        self.prepare_main(engine, "A")
        engine.state.stack.append(
            StackItem(
                stack_id="S-loyalty-window",
                ref="S-loyalty-window",
                kind="spell",
                controller="B",
                label="Stack is not empty",
            )
        )
        self.assertEqual(
            ("unavailable", "loyalty_timing"),
            engine._ability_availability("A", daretti, plus),
        )

        self.prepare_main(engine, "A")
        before = daretti.counters["loyalty"]
        engine._activate(
            "A",
            {"source": daretti.ref, "ability": plus.ability_id},
        )
        self.assertEqual(before + 2, daretti.counters["loyalty"])

        engine.state.stack.clear()
        self.assertEqual(
            ("unavailable", "loyalty_already_activated"),
            engine._ability_availability("A", daretti, minus),
        )

    def test_negative_loyalty_cost_requires_enough_counters(self):
        engine = self.make_engine(60603)
        daretti = self.card(engine, "A", "Daretti, Scrap Savant")
        engine.move_card(
            daretti.object_id,
            "battlefield",
            controller="A",
            log=False,
        )
        minus = engine._activated_abilities(daretti)[1]
        self.prepare_main(engine)

        daretti.counters["loyalty"] = 1
        self.assertEqual(
            ("unpayable", "insufficient_loyalty"),
            engine._ability_availability("A", daretti, minus),
        )
        daretti.counters["loyalty"] = 2
        self.assertEqual(
            ("payable", None),
            engine._ability_availability("A", daretti, minus),
        )

    def test_raw_loyalty_cost_words_without_typed_metadata_remain_payable(self):
        engine = self.make_engine(60604)
        daretti = self.card(engine, "A", "Daretti, Scrap Savant")
        engine.move_card(
            daretti.object_id,
            "battlefield",
            controller="A",
            log=False,
        )
        self.add_test_permanent(
            engine,
            ref="A-loyalty-modifier",
            name="Loyalty Cost Modifier",
            type_line="Enchantment",
            oracle_text=(
                "Loyalty abilities you activate cost an additional "
                "+1 to activate."
            ),
        )
        self.prepare_main(engine)

        ability = engine._activated_abilities(daretti)[0]
        self.assertEqual(
            ("payable", None),
            engine._ability_availability("A", daretti, ability),
        )

    def test_visible_typed_loyalty_cost_modifier_fails_closed(self):
        engine = self.make_engine(60605)
        daretti = self.card(engine, "A", "Daretti, Scrap Savant")
        engine.move_card(
            daretti.object_id,
            "battlefield",
            controller="A",
            log=False,
        )
        record = CardRecord(
            oracle_id="00000000-0000-4000-8000-000000606005",
            name="Typed Loyalty Cost Modifier",
            mana_cost="{2}{B}{G}",
            mana_value=4.0,
            type_line="Legendary Creature — Human Warrior",
            oracle_text=(
                "Planeswalkers' loyalty abilities you activate cost an "
                "additional [+1] to activate."
            ),
            power="3",
            toughness="3",
            loyalty=None,
            defense=None,
            colors=("B", "G"),
            color_identity=("B", "G"),
            keywords=(),
            produced_mana=(),
            layout="normal",
            released_at="2026-01-01",
            legalities={"commander": "legal"},
            faces=(),
            raw={},
        )
        source = CardInstance(
            object_id="typed-loyalty-modifier",
            ref="A-typed-loyalty-modifier",
            oracle_id=record.oracle_id,
            printed_name=record.name,
            owner="A",
            controller="A",
            zone="battlefield",
            known_to=list(engine.seats),
            revealed_to=list(engine.seats),
        )
        engine.state.cards[source.object_id] = source
        engine.state.players["A"].zones["battlefield"].append(source.object_id)
        capabilities = load_default_capability_registry()
        program = next(
            program
            for program in generated_programs(
                _NoRulingsDatabase(),
                record,
                trust_level="trusted",
                capability_registry=capabilities,
                capability_profile=engine.state.config.review_profile,
            )
            if program.event == LOYALTY_COST_MODIFIER_EVENT
        )
        engine.semantics.put(program)
        original_card_record = engine.card_record
        original_trust = engine.semantic_program_is_current_trusted

        def card_record(value):
            card = (
                value
                if isinstance(value, CardInstance)
                else engine.state.cards[value]
            )
            if card.oracle_id == record.oracle_id:
                return record
            return original_card_record(value)

        def current_trusted(candidate):
            if candidate.oracle_id == record.oracle_id:
                return True
            return original_trust(candidate)

        self.prepare_main(engine)
        ability = engine._activated_abilities(daretti)[0]
        with mock.patch.object(engine, "card_record", side_effect=card_record), mock.patch.object(
            engine,
            "semantic_program_is_current_trusted",
            side_effect=current_trusted,
        ):
            self.assertEqual(
                ("unresolved", "unresolved_loyalty_cost_modification"),
                engine._ability_availability("A", daretti, ability),
            )
            source.phased_out = True
            self.assertEqual(
                ("payable", None),
                engine._ability_availability("A", daretti, ability),
            )
            source.phased_out = False
            self.assertEqual(
                ("unresolved", "unresolved_loyalty_cost_modification"),
                engine._ability_availability("A", daretti, ability),
            )
            hints = engine._priority_action_hints("A")
            self.assertFalse(
                any(
                    hint.get("s") == daretti.ref
                    for hint in hints["abilities"]
                )
            )
            self.assertTrue(
                any(
                    hint.get("s") == daretti.ref
                    and hint.get("reason")
                    == "unresolved_loyalty_cost_modification"
                    for hint in hints["diagnostic"][
                        "unresolved_cost_semantics"
                    ]
                )
            )

    def test_multiple_loyalty_costs_fail_closed_until_combined(self):
        ability = parse_activated_abilities(
            card_name="Combined Loyalty Relic",
            oracle_text="+1, −2: Draw a card.",
        )[0]

        self.assertIsNone(ability.loyalty_delta)
        self.assertFalse(ability.compiled_cost)
        self.assertIn(
            "multiple loyalty-symbol costs require combined-cost semantics",
            ability.uncompiled_costs,
        )


if __name__ == "__main__":
    unittest.main()
