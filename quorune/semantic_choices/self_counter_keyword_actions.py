from __future__ import annotations

"""Resolution-time conditions for fixed self-counter keyword actions."""

from dataclasses import dataclass
from typing import Mapping

from ..object_query import ObjectQueryResult
from ..replacement.immutable import FrozenMap
from ..semantic_runtime import (
    BecomeMonstrousIntent,
    BecomeRenownedIntent,
    PlaceCountersIntent,
)
from .context import SemanticChoiceContext, SemanticChoiceQuery
from .model import (
    AutoContinue,
    SemanticChoiceCompletion,
    SemanticChoiceContinuation,
    SemanticChoiceError,
    SemanticChoicePreparation,
)


_EFFECT_FIELDS = {"op", "action", "amount", "source"}
_ACTIONS = {"adapt", "monstrosity", "renown"}
_COUNTER_NAME = "+1/+1"


def _validated_effect(
    effect: Mapping[str, object],
) -> tuple[str, int, str]:
    if set(effect) != _EFFECT_FIELDS:
        raise SemanticChoiceError(
            "Self-counter keyword action fields are malformed"
        )
    if effect.get("op") != "fixed_self_counter_keyword_action":
        raise SemanticChoiceError(
            "Self-counter keyword action operation changed"
        )
    action = effect.get("action")
    amount = effect.get("amount")
    source_ref = effect.get("source")
    if (
        type(action) is not str
        or action not in _ACTIONS
        or type(amount) is not int
        or amount <= 0
        or type(source_ref) is not str
        or not source_ref
    ):
        raise SemanticChoiceError(
            "Self-counter keyword action values are malformed"
        )
    return action, amount, source_ref


def _counter_amount(source: ObjectQueryResult) -> int:
    raw = source.counters.get(_COUNTER_NAME, 0)
    if type(raw) is not int or raw < 0:
        raise SemanticChoiceError(
            "The source permanent's +1/+1 counter state is malformed"
        )
    return raw


@dataclass(frozen=True, slots=True)
class FixedSelfCounterKeywordActionHandler:
    operation: str = "fixed_self_counter_keyword_action"
    handler_id: str = "choice.keyword-action.self-counter-fixed.v1"
    schema_version: int = 1
    rule_references: tuple[str, ...] = (
        "CR 400.7",
        "CR 608.2c",
        "CR 614.16",
        "CR 701.37a",
        "CR 701.37b",
        "CR 701.37c",
        "CR 701.46a",
        "CR 702.112a",
        "CR 702.112b",
        "CR 702.112c",
    )
    capability_dependencies: tuple[str, ...] = (
        "counter.placement.quantity_replacement",
    )
    continuation_fields: tuple[str, ...] = (
        "action",
        "amount",
        "source",
    )
    private_data: tuple[str, ...] = ()
    projected_fields: tuple[str, ...] = ()
    mutation_path: tuple[str, ...] = (
        "PlaceCountersIntent",
        "counter_placement.place_counters",
        "BecomeMonstrousIntent",
        "permanent_designations.become_monstrous",
        "BecomeRenownedIntent",
        "permanent_designations.become_renowned",
    )
    replay_fixture: str = "fixed-self-counter-keyword-actions"
    test_modules: tuple[str, ...] = (
        "tests.test_self_counter_keyword_actions",
        "tests.test_renown_rules",
    )

    def prepare(
        self,
        effect: Mapping[str, object],
        context: SemanticChoiceContext,
    ) -> SemanticChoicePreparation:
        action, amount, source_ref = _validated_effect(effect)
        if source_ref != context.source_ref:
            raise SemanticChoiceError(
                "Self-counter keyword action source changed"
            )
        source = context.query.object(source_ref)
        source_logical_object_id = context.source_logical_object_id
        current = bool(
            source is not None
            and source.zone == "battlefield"
            and not source.phased_out
            and type(source_logical_object_id) is str
            and source_logical_object_id
            and source.logical_object_id == source_logical_object_id
        )
        continuation_effect = FrozenMap(
            {
                "op": self.operation,
                "action": action,
                "amount": amount,
                "source": source_ref,
            }
        )
        if not current:
            return SemanticChoicePreparation(
                request=None,
                continuation_effect=continuation_effect,
                preparation_intents=(),
                auto_continue=AutoContinue(
                    reason="the source is no longer the resolving permanent"
                ),
            )
        assert source is not None
        current_counter_amount = _counter_amount(source)
        if action == "adapt" and current_counter_amount:
            return SemanticChoicePreparation(
                request=None,
                continuation_effect=continuation_effect,
                preparation_intents=(),
                auto_continue=AutoContinue(
                    reason="the permanent already has a +1/+1 counter"
                ),
            )
        if action == "monstrosity":
            monstrous_value = source.monstrous_value
            if monstrous_value is not None and (
                type(monstrous_value) is not int or monstrous_value < 0
            ):
                raise SemanticChoiceError(
                    "The source permanent's monstrous designation is malformed"
                )
            if monstrous_value is not None:
                return SemanticChoicePreparation(
                    request=None,
                    continuation_effect=continuation_effect,
                    preparation_intents=(),
                    auto_continue=AutoContinue(
                        reason="the permanent is already monstrous"
                    ),
                )
        if action == "renown":
            if type(source.renowned) is not bool:
                raise SemanticChoiceError(
                    "The source permanent's renowned designation is malformed"
                )
            if source.renowned:
                return SemanticChoicePreparation(
                    request=None,
                    continuation_effect=continuation_effect,
                    preparation_intents=(),
                    auto_continue=AutoContinue(
                        reason="the permanent is already renowned"
                    ),
                )

        intents = [
            PlaceCountersIntent(
                actor=context.actor,
                object_refs=(source.ref,),
                counter_name=_COUNTER_NAME,
                amount=amount,
                reason=context.stack_label,
                source_ref=source.ref,
            )
        ]
        if action == "monstrosity":
            intents.append(
                BecomeMonstrousIntent(
                    actor=context.actor,
                    object_id=source.object_id,
                    object_ref=source.ref,
                    logical_object_id=source.logical_object_id,
                    value=amount,
                    reason=context.stack_label,
                )
            )
        if action == "renown":
            intents.append(
                BecomeRenownedIntent(
                    actor=context.actor,
                    object_id=source.object_id,
                    object_ref=source.ref,
                    logical_object_id=source.logical_object_id,
                    reason=context.stack_label,
                )
            )
        return SemanticChoicePreparation(
            request=None,
            continuation_effect=continuation_effect,
            preparation_intents=tuple(intents),
            auto_continue=AutoContinue(
                reason=f"resolved fixed {action} action"
            ),
        )

    def complete(
        self,
        continuation: SemanticChoiceContinuation,
        response: Mapping[str, object],
        query: SemanticChoiceQuery,
    ) -> SemanticChoiceCompletion:
        raise SemanticChoiceError(
            "Fixed self-counter keyword actions never issue a player choice"
        )


SELF_COUNTER_KEYWORD_ACTION_HANDLERS = (
    FixedSelfCounterKeywordActionHandler(),
)


__all__ = [
    "FixedSelfCounterKeywordActionHandler",
    "SELF_COUNTER_KEYWORD_ACTION_HANDLERS",
]
