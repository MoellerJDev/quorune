from __future__ import annotations

import unittest

from quorune.ability_fragments import ability_fragment_from_dict
from quorune.compiler.ability_keyword_fragments import (
    lower_ability_keyword_fragments,
)
from quorune.compiler.trigger_participation_templates import (
    static_trigger_multiplier_handler,
)
from quorune.trigger_batches import (
    PendingTriggerItem,
    TriggerBatchError,
    TriggerOccurrence,
)
from quorune.trigger_participation import (
    StaticTriggerParticipation,
    TriggerMultiplierPredicate,
    TriggerMultiplierSpec,
    TriggerParticipationError,
    WardSpec,
)


class StaticTriggerParticipationTests(unittest.TestCase):
    def test_multiplier_snapshot_is_typed_canonical_and_source_pinned(self):
        spec = TriggerMultiplierSpec(
            predicate=(
                TriggerMultiplierPredicate.ANOTHER_CREATURE_OF_CHOSEN_TYPE
            ),
            exclude_self=True,
        )
        participation = StaticTriggerParticipation(
            source_object_id="card-physical",
            source_logical_object_id="card-logical-7",
            source_controller="A",
            active_zone="battlefield",
            spec=spec,
            chosen_creature_type="  Goblin  ",
        )

        self.assertEqual("goblin", participation.chosen_creature_type)
        self.assertEqual(
            "trigger.multiplier.another_creature_of_chosen_type",
            participation.capability_id,
        )
        self.assertEqual(participation.fingerprint, participation.fingerprint)
        self.assertEqual(
            participation.fingerprint,
            StaticTriggerParticipation(
                source_object_id="card-physical",
                source_logical_object_id="card-logical-7",
                source_controller="A",
                active_zone="battlefield",
                spec=TriggerMultiplierSpec.from_dict(spec.to_dict()),
                chosen_creature_type="goblin",
            ).fingerprint,
        )

    def test_multiplier_snapshot_rejects_missing_choice_and_wrong_self_rule(self):
        with self.assertRaises(TriggerParticipationError):
            TriggerMultiplierSpec(
                predicate=(
                    TriggerMultiplierPredicate.ANOTHER_CREATURE_OF_CHOSEN_TYPE
                ),
                exclude_self=False,
            )
        with self.assertRaises(TriggerParticipationError):
            StaticTriggerParticipation(
                source_object_id="card-physical",
                source_logical_object_id="card-logical-7",
                source_controller="A",
                active_zone="battlefield",
                spec=TriggerMultiplierSpec(
                    predicate=(
                        TriggerMultiplierPredicate.ANOTHER_CREATURE_OF_CHOSEN_TYPE
                    ),
                    exclude_self=True,
                ),
            )

    def test_multiplier_and_ward_fragments_have_closed_schemas(self):
        multiplier = TriggerMultiplierSpec(
            predicate=(
                TriggerMultiplierPredicate.ARTIFACT_OR_CREATURE_ENTERS
            ),
        )
        ward = WardSpec(generic_cost=2)

        self.assertEqual(
            multiplier,
            ability_fragment_from_dict(
                {
                    "kind": "trigger_multiplier",
                    "value": multiplier.to_dict(),
                }
            ),
        )
        self.assertEqual(
            ward,
            ability_fragment_from_dict(
                {"kind": "ward", "value": ward.to_dict()}
            ),
        )
        with self.assertRaises(TriggerParticipationError):
            TriggerMultiplierSpec.from_dict(
                {**multiplier.to_dict(), "oracle_text": "live authority"}
            )
        with self.assertRaises(TriggerParticipationError):
            WardSpec.from_dict({**ward.to_dict(), "arbitrary": True})


class TriggerParticipationCompilerTests(unittest.TestCase):
    def test_artifact_creature_enter_multiplier_compiles_to_typed_fragment(self):
        result = static_trigger_multiplier_handler(
            "If an artifact or creature entering causes a triggered ability "
            "of a permanent you control to trigger, that ability triggers "
            "an additional time."
        )

        self.assertIsNotNone(result)
        assert result is not None
        template_id, descriptor, capability_id = result
        self.assertEqual(
            "static-trigger-multiplier-artifact-creature-enters-v1",
            template_id,
        )
        self.assertEqual(
            "trigger.multiplier.artifact_or_creature_enters",
            capability_id,
        )
        fragment = ability_fragment_from_dict(descriptor["fragment"])
        self.assertIsInstance(fragment, TriggerMultiplierSpec)

    def test_chosen_type_multiplier_compiles_and_near_misses_stay_unsupported(self):
        result = static_trigger_multiplier_handler(
            "If a triggered ability of another creature you control of the "
            "chosen type triggers, it triggers an additional time."
        )
        self.assertIsNotNone(result)
        assert result is not None
        fragment = ability_fragment_from_dict(result[1]["fragment"])
        self.assertEqual(
            TriggerMultiplierPredicate.ANOTHER_CREATURE_OF_CHOSEN_TYPE,
            fragment.predicate,
        )
        self.assertTrue(fragment.exclude_self)
        self.assertIsNone(
            static_trigger_multiplier_handler(
                "If an ability of a creature you control triggers, it "
                "triggers two additional times."
            )
        )

    def test_fixed_generic_ward_compiles_and_other_costs_remain_residual(self):
        fixed = lower_ability_keyword_fragments("Ward {2}", ("ward",))
        life = lower_ability_keyword_fragments("Ward—Pay 3 life.", ("ward",))

        self.assertIsNone(fixed.residual_kind)
        self.assertEqual(1, len(fixed.handlers))
        ward = ability_fragment_from_dict(fixed.handlers[0]["fragment"])
        self.assertEqual(WardSpec(generic_cost=2), ward)
        self.assertEqual("unsupported_ward_cost", life.residual_kind)
        self.assertFalse(life.handlers)


class TriggerOccurrenceTests(unittest.TestCase):
    @staticmethod
    def payload() -> dict:
        return {
            "stack_id": "stack-1",
            "ref": "S1",
            "kind": "triggered_ability",
            "controller": "A",
            "label": "Typed trigger",
            "source_object_id": "physical-1",
            "semantic_key": "oracle:ability:ab1",
            "visibility": ["A", "B"],
            "context": {
                "event": "permanent.enter",
                "source_logical_object_id": "logical-2",
                "source_zone": "battlefield",
                "intervening_condition": {"field": "enabled"},
                "trigger_target_selection_pending": True,
                "additional_trigger_source": {
                    "source_object_id": "multiplier-1"
                },
                "one_or_more_aggregation_id": "aggregation-1",
            },
        }

    def test_occurrence_is_immutable_canonical_and_game_record_compatible(self):
        payload = self.payload()
        occurrence = TriggerOccurrence.from_dict(payload)
        payload["context"]["event"] = "tampered"

        self.assertIs(PendingTriggerItem, TriggerOccurrence)
        self.assertEqual("permanent.enter", occurrence.normalized_event_id)
        self.assertEqual("logical-2", occurrence.source_logical_object_id)
        self.assertTrue(occurrence.target_selection_required)
        self.assertEqual(
            occurrence.fingerprint,
            TriggerOccurrence.from_dict(occurrence.to_dict()).fingerprint,
        )
        self.assertEqual(occurrence.to_dict(), PendingTriggerItem.from_dict(
            occurrence.to_dict()
        ).to_dict())

    def test_occurrence_rejects_malformed_typed_context(self):
        malformed_values = (
            {"event": ""},
            {"source_logical_object_id": 4},
            {"trigger_target_selection_pending": 1},
            {"intervening_condition": []},
            {"additional_trigger_source": "oracle text"},
        )
        for update in malformed_values:
            with self.subTest(update=update):
                payload = self.payload()
                payload["context"].update(update)
                with self.assertRaises(TriggerBatchError):
                    TriggerOccurrence.from_dict(payload)


if __name__ == "__main__":
    unittest.main()
