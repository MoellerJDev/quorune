from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
import unittest

from quorune.abilities import (
    ActivatedAbility,
    ActivationConditionKind,
    parse_activated_abilities,
)
from quorune.carddb import CardRecord
from quorune.compiler.activated_ability_catalog import (
    compile_activated_ability_catalog,
    with_activated_ability_catalog,
)
from quorune.continuous_effect_model import (
    ContinuousEffect,
    ContinuousOperation,
    Layer,
)
from quorune.continuous_effects import (
    CharacteristicState,
    evaluate_continuous_effects,
)
from quorune.rules.activation.conditions import activation_condition_status
from quorune.semantic_runtime.activated_abilities import (
    ACTIVATED_ABILITY_CATALOG_HANDLER_ID,
    activated_abilities_from_descriptors,
)
from quorune.semantics import SemanticProgram
from quorune.standard_token_abilities import standard_token_characteristics


def record(name: str, oracle_text: str, *, type_line: str = "Artifact") -> CardRecord:
    return CardRecord(
        oracle_id=f"fixture:{name.casefold().replace(' ', '-')}",
        name=name,
        mana_cost="{0}",
        mana_value=0.0,
        type_line=type_line,
        oracle_text=oracle_text,
        power=None,
        toughness=None,
        loyalty=None,
        defense=None,
        colors=(),
        color_identity=("W", "U", "B", "R", "G"),
        keywords=(),
        produced_mana=(),
        layout="normal",
        released_at="2026-01-01",
        legalities={"commander": "legal"},
        faces=(),
        raw={},
    )


class TypedActivatedAbilityCatalogTests(unittest.TestCase):
    def test_closed_descriptor_round_trip_and_input_isolation(self):
        mana = {"GENERIC": 2}
        ability = parse_activated_abilities(
            card_name="Fixture",
            oracle_text=(
                "{2}, {T}: Add one mana of any color. "
                "Activate only if you control an artifact."
            ),
        )[0]
        mana.update(ability.mana)
        serialized = ability.to_dict()
        reconstructed = ActivatedAbility.from_dict(serialized)
        serialized["mana"]["GENERIC"] = 99

        self.assertEqual(ability, reconstructed)
        self.assertEqual(2, reconstructed.mana["GENERIC"])
        self.assertEqual(
            ActivationConditionKind.CONTROLS_TYPE,
            reconstructed.activation_conditions[0].kind,
        )
        with self.assertRaisesRegex(ValueError, "closed schema"):
            ActivatedAbility.from_dict({**ability.to_dict(), "unknown": True})

    def test_catalog_specializes_color_set_and_dynamic_outputs(self):
        mox = compile_activated_ability_catalog(
            record(
                "Mox Amber",
                "{T}: Add one mana of any color among legendary creatures "
                "and planeswalkers you control.",
                type_line="Legendary Artifact",
            )
        )["front"][0]
        fellwar = compile_activated_ability_catalog(
            record(
                "Fellwar Stone",
                "{T}: Add one mana of any color that a land an opponent "
                "controls could produce.",
            )
        )["front"][0]

        self.assertIsNotNone(mox.color_set_mana_output)
        self.assertEqual("opponent_land_colors", fellwar.dynamic_mana_output)

    def test_program_catalog_is_additive_and_strictly_lowered(self):
        card = record("Fixture Stone", "{T}: Add {C}.")
        program = SemanticProgram(
            key=f"{card.oracle_id}:ability:ab1",
            label="Fixture mana ability",
            oracle_id=card.oracle_id,
            ability_id="ability:ab1",
            active_zone="battlefield",
            event="activate",
            trust_level="provisional",
        )
        augmented = with_activated_ability_catalog(card, (program,))[0]
        descriptors = [
            handler
            for handler in augmented.handlers
            if handler["handler_id"] == ACTIVATED_ABILITY_CATALOG_HANDLER_ID
        ]

        self.assertEqual(1, len(descriptors))
        lowered = activated_abilities_from_descriptors(descriptors)
        self.assertEqual("ab1", lowered[0].ability_id)
        self.assertEqual({"C": 1}, {
            key: amount
            for key, amount in lowered[0].fixed_mana_outputs[0].bundle.items()
            if amount
        })
        malformed = {**descriptors[0], "unknown": True}
        with self.assertRaisesRegex(ValueError, "unknown fields"):
            activated_abilities_from_descriptors([malformed])

    def test_conditions_ignore_runtime_prose_and_use_effective_types(self):
        ability = parse_activated_abilities(
            card_name="Fixture",
            oracle_text=(
                "{T}: Add {C}. Activate only if you control three or more "
                "artifacts."
            ),
        )[0]
        ability = replace(ability, effect_text="Display text changed.")
        cards = {
            value: SimpleNamespace(
                object_id=value,
                controller="A",
                phased_out=False,
            )
            for value in ("one", "two", "three")
        }

        class Host:
            state = SimpleNamespace(
                active_player="A",
                turn_sequence=1,
                cards=cards,
                players={
                    "A": SimpleNamespace(
                        stats={}, zones={"battlefield": list(cards), "graveyard": []}
                    )
                },
            )

            @staticmethod
            def _effective_card_data(card):
                return {
                    "type_line": (
                        "Artifact"
                        if card.object_id != "three"
                        else "Creature"
                    )
                }

            @staticmethod
            def _type_parts(type_line):
                return ({type_line.casefold()}, set(), set())

        self.assertEqual(
            ("unavailable", "requires_3_artifacts"),
            activation_condition_status(Host(), "A", ability),
        )
        Host._effective_card_data = staticmethod(lambda card: {"type_line": "Artifact"})
        self.assertEqual(
            ("payable", None),
            activation_condition_status(Host(), "A", ability),
        )

    def test_standard_tokens_receive_typed_executable_abilities(self):
        treasure = standard_token_characteristics(
            {
                "type_line": "Token Artifact — Treasure",
                "activated_ability_profile": "tap_sac_any_color_mana_v1",
            }
        )
        food = standard_token_characteristics(
            {
                "type_line": "Token Artifact — Food",
                "activated_ability_profile": (
                    "two_tap_sac_gain_three_life_v1"
                ),
            }
        )
        mana = ActivatedAbility.from_dict(treasure["activated_abilities"][0])
        life = ActivatedAbility.from_dict(food["activated_abilities"][0])

        self.assertTrue(mana.mana_ability)
        self.assertTrue(mana.sacrifice_source)
        self.assertEqual(5, len(mana.fixed_mana_outputs))
        self.assertEqual("builtin:gain-life:3", life.builtin_semantic_key)
        self.assertNotIn("activated_ability_profile", treasure)
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            standard_token_characteristics(
                {"activated_ability_profile": "unknown-v1"}
            )

    def test_material_catalog_change_changes_pinned_handler(self):
        program = SemanticProgram(
            key="fixture:catalog:ability:ab1",
            label="Fixture mana ability",
            oracle_id="fixture:fixture-stone",
            ability_id="ability:ab1",
            active_zone="battlefield",
            event="activate",
            trust_level="provisional",
        )
        colorless = with_activated_ability_catalog(
            record("Fixture Stone", "{T}: Add {C}."),
            (program,),
        )[0]
        blue = with_activated_ability_catalog(
            record("Fixture Stone", "{T}: Add {U}."),
            (program,),
        )[0]

        self.assertNotEqual(colorless.handlers, blue.handlers)

    def test_copy_and_remove_all_abilities_use_the_typed_catalog(self):
        ability = compile_activated_ability_catalog(
            record("Fixture Stone", "{T}: Add {C}.")
        )["front"][0]
        copied = evaluate_continuous_effects(
            CharacteristicState(name="Copy target"),
            (
                ContinuousEffect(
                    effect_id="copy-ability",
                    source_id="copy-source",
                    layer=Layer.COPY,
                    sublayer="1a",
                    timestamp=1,
                    operations=(
                        ContinuousOperation(
                            "copy_values",
                            {"activated_abilities": [ability.to_dict()]},
                        ),
                    ),
                ),
            ),
        )
        self.assertEqual(
            ability.to_dict(), copied.characteristics["activated_abilities"][0]
        )

        removed = evaluate_continuous_effects(
            CharacteristicState(
                name="Copy target", activated_abilities=[ability]
            ),
            (
                ContinuousEffect(
                    effect_id="remove-abilities",
                    source_id="removal-source",
                    layer=Layer.ABILITY,
                    sublayer="6",
                    timestamp=2,
                    operations=(ContinuousOperation("remove_all_abilities"),),
                ),
            ),
        )
        self.assertEqual([], removed.characteristics["activated_abilities"])


if __name__ == "__main__":
    unittest.main()
