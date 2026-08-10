from __future__ import annotations

"""Resolution-time coordination for ordinary fixed Bolster."""

from dataclasses import dataclass
from typing import Any, Mapping

from ..object_query import ObjectQueryResult
from ..replacement.immutable import FrozenMap
from ..semantic_runtime import PlaceCountersIntent, RecordChoiceIntent
from .context import SemanticChoiceContext, SemanticChoiceQuery
from .model import (
    AutoContinue,
    ObjectChoice,
    SemanticChoiceCompletion,
    SemanticChoiceContinuation,
    SemanticChoiceError,
    SemanticChoicePreparation,
    SemanticChoiceRequest,
)


_EFFECT_FIELDS = {"op", "player", "amount"}
_CONTINUATION_FIELDS = {
    *_EFFECT_FIELDS,
    "_actor",
    "_controlled_creatures",
    "_legal_refs",
    "_source_ref",
    "_stack_label",
}
_COUNTER_NAME = "+1/+1"


def _validated_effect(effect: Mapping[str, Any]) -> tuple[str, int]:
    if set(effect) != _EFFECT_FIELDS:
        raise SemanticChoiceError("Bolster effect fields are malformed")
    player = effect.get("player")
    amount = effect.get("amount")
    if (
        effect.get("op") != "fixed_bolster"
        or type(player) is not str
        or not player
        or type(amount) is not int
        or amount <= 0
    ):
        raise SemanticChoiceError("Bolster effect values are malformed")
    return player, amount


def _controlled_creatures(
    query: SemanticChoiceQuery,
    player: str,
) -> tuple[ObjectQueryResult, ...]:
    creatures = tuple(
        sorted(
            (
                row
                for row in query.objects(
                    zones=("battlefield",),
                    controller=player,
                )
                if "creature" in row.types
            ),
            key=lambda row: row.ref,
        )
    )
    for row in creatures:
        if type(row.effective_toughness) is not int:
            raise SemanticChoiceError(
                "Bolster requires an exact effective toughness for every "
                "controlled creature"
            )
    return creatures


def _creature_snapshot(
    creatures: tuple[ObjectQueryResult, ...],
) -> tuple[FrozenMap, ...]:
    return tuple(
        FrozenMap(
            {
                "ref": row.ref,
                "object_id": row.object_id,
                "logical_object_id": row.logical_object_id,
                "toughness": row.effective_toughness,
            }
        )
        for row in creatures
    )


def _least_toughness_creatures(
    creatures: tuple[ObjectQueryResult, ...],
) -> tuple[ObjectQueryResult, ...]:
    if not creatures:
        return ()
    minimum = min(int(row.effective_toughness) for row in creatures)
    return tuple(
        row for row in creatures if row.effective_toughness == minimum
    )


@dataclass(frozen=True, slots=True)
class FixedBolsterChoiceHandler:
    operation: str = "fixed_bolster"
    handler_id: str = "choice.keyword-action.bolster-fixed.v1"
    schema_version: int = 1
    rule_references: tuple[str, ...] = (
        "CR 122.1a",
        "CR 608.2c",
        "CR 614.16",
        "CR 616.1",
        "CR 701.39a",
    )
    capability_dependencies: tuple[str, ...] = (
        "counter.placement.quantity_replacement",
    )
    continuation_fields: tuple[str, ...] = (
        "player",
        "amount",
        "_actor",
        "_controlled_creatures",
        "_legal_refs",
        "_source_ref",
        "_stack_label",
    )
    private_data: tuple[str, ...] = ()
    projected_fields: tuple[str, ...] = (
        "prompt",
        "objects",
        "legal_actions.choice_schema.legal_refs",
    )
    mutation_path: tuple[str, ...] = (
        "PlaceCountersIntent",
        "counter_placement.place_counters",
    )
    replay_fixture: str = "fixed-bolster-choice"
    test_modules: tuple[str, ...] = ("tests.test_bolster_rules",)

    def prepare(
        self,
        effect: Mapping[str, Any],
        context: SemanticChoiceContext,
    ) -> SemanticChoicePreparation:
        player, amount = _validated_effect(effect)
        if player != context.actor:
            raise SemanticChoiceError(
                "Bolster must be performed by the resolving controller"
            )
        creatures = _controlled_creatures(context.query, player)
        continuation = FrozenMap(
            {
                "op": self.operation,
                "player": player,
                "amount": amount,
                "_actor": context.actor,
                "_controlled_creatures": _creature_snapshot(creatures),
                "_legal_refs": tuple(
                    row.ref for row in _least_toughness_creatures(creatures)
                ),
                "_source_ref": context.source_ref,
                "_stack_label": context.stack_label,
            }
        )
        if not creatures:
            return SemanticChoicePreparation(
                request=None,
                continuation_effect=continuation,
                auto_continue=AutoContinue(
                    reason="the Bolster player controls no creatures"
                ),
            )
        legal = _least_toughness_creatures(creatures)
        return SemanticChoicePreparation(
            request=SemanticChoiceRequest(
                prompt=(
                    "Choose a creature you control tied for least toughness "
                    f"to bolster {amount}."
                ),
                choice=ObjectChoice(
                    field_name="objects",
                    legal_refs=tuple(row.ref for row in legal),
                    zones=("battlefield",),
                ),
                public_context=FrozenMap(
                    {
                        "stack": context.stack_ref,
                        "operation": self.operation,
                        "objects": tuple(
                            {
                                "id": row.ref,
                                "name": row.printed_name,
                                "toughness": row.effective_toughness,
                            }
                            for row in legal
                        ),
                    }
                ),
            ),
            continuation_effect=continuation,
        )

    def complete(
        self,
        continuation: SemanticChoiceContinuation,
        response: Mapping[str, Any],
        query: SemanticChoiceQuery,
    ) -> SemanticChoiceCompletion:
        effect = continuation.effect
        if set(effect) != _CONTINUATION_FIELDS:
            raise SemanticChoiceError("Bolster continuation fields are malformed")
        player, amount = _validated_effect(
            {
                "op": effect.get("op"),
                "player": effect.get("player"),
                "amount": effect.get("amount"),
            }
        )
        if player != effect.get("_actor"):
            raise SemanticChoiceError("Bolster continuation actor changed")
        raw_selected = response.get("objects", response.get("cards"))
        if not isinstance(raw_selected, (list, tuple)):
            raise SemanticChoiceError("Bolster requires one object choice")
        selected = tuple(str(value) for value in raw_selected)
        legal_refs = tuple(str(value) for value in effect.get("_legal_refs", ()))
        if (
            len(selected) != 1
            or selected[0] not in legal_refs
            or len(legal_refs) != len(set(legal_refs))
        ):
            raise SemanticChoiceError(
                "Bolster choice is not tied for least toughness"
            )
        current = _controlled_creatures(query, player)
        if _creature_snapshot(current) != tuple(
            effect.get("_controlled_creatures", ())
        ):
            raise SemanticChoiceError(
                "Bolster creature identity or effective toughness changed"
            )
        current_legal = tuple(
            row.ref for row in _least_toughness_creatures(current)
        )
        if current_legal != legal_refs:
            raise SemanticChoiceError("Bolster legal creature set changed")
        source_ref = effect.get("_source_ref")
        if source_ref is not None and (
            type(source_ref) is not str or not source_ref
        ):
            raise SemanticChoiceError("Bolster source identity is malformed")
        label = effect.get("_stack_label")
        if type(label) is not str or not label:
            raise SemanticChoiceError("Bolster stack label is malformed")
        return SemanticChoiceCompletion(
            intents=(
                PlaceCountersIntent(
                    actor=player,
                    object_refs=selected,
                    counter_name=_COUNTER_NAME,
                    amount=amount,
                    reason=label,
                    source_ref=source_ref,
                ),
                RecordChoiceIntent(
                    actor=player,
                    event_code="keyword_action.bolster.chosen",
                    message=f"{player} chose {selected[0]} for Bolster.",
                    details=FrozenMap(
                        {
                            "stack": continuation.stack_ref,
                            "object": selected[0],
                            "amount": amount,
                        }
                    ),
                ),
            )
        )


BOLSTER_CHOICE_HANDLERS = (FixedBolsterChoiceHandler(),)


__all__ = ["BOLSTER_CHOICE_HANDLERS", "FixedBolsterChoiceHandler"]
