from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..modular import (
    ModularError,
    modular_counter_count,
    modular_counter_snapshot,
)
from ..replacement.immutable import FrozenMap
from .context import SemanticChoiceContext, SemanticChoiceQuery
from .model import (
    AutoContinue,
    ScalarChoice,
    SemanticChoiceCompletion,
    SemanticChoiceContinuation,
    SemanticChoiceError,
    SemanticChoicePreparation,
    SemanticChoiceRequest,
)


_FIELDS = {
    "op",
    "player",
    "card",
    "amount",
    "counter_snapshot",
    "source",
    "rule_id",
}
_REASON_FIELD = "reason"


def _artifact_creature_target(
    query: SemanticChoiceQuery,
    card_ref: str,
) -> bool:
    card = query.object(card_ref, zones=("battlefield",))
    return bool(
        card is not None
        and not card.phased_out
        and {"artifact", "creature"}.issubset(card.types)
    )


def _validated_effect(
    effect: Mapping[str, Any],
    *,
    actor: str,
    active_seats: tuple[str, ...],
) -> tuple[str, str, int, FrozenMap, str]:
    if not isinstance(effect, Mapping) or set(effect) != _FIELDS:
        missing = sorted(_FIELDS - set(effect))
        unknown = sorted(set(effect) - _FIELDS)
        details = [
            *(f"missing {field}" for field in missing),
            *(f"unknown {field}" for field in unknown),
        ]
        raise SemanticChoiceError(
            "Modular transfer fields: " + "; ".join(details)
        )
    if effect.get("op") != "offer_modular_counter_transfer":
        raise SemanticChoiceError("Modular transfer operation changed")
    player = effect.get("player")
    card_ref = effect.get("card")
    amount = effect.get("amount")
    snapshot = effect.get("counter_snapshot")
    source_ref = effect.get("source")
    if (
        type(player) is not str
        or player != actor
        or player not in active_seats
        or type(card_ref) is not str
        or not card_ref
        or type(amount) is not int
        or amount < 0
        or not isinstance(snapshot, Mapping)
        or type(source_ref) is not str
        or not source_ref
        or effect.get("rule_id") != "702.43a"
    ):
        raise SemanticChoiceError(
            "Modular chooser, target, count, snapshot, or source is malformed"
        )
    try:
        canonical_snapshot = modular_counter_snapshot(snapshot)
        expected_amount = modular_counter_count(canonical_snapshot)
    except (ModularError, TypeError, ValueError) as exc:
        raise SemanticChoiceError(str(exc)) from exc
    if amount != expected_amount:
        raise SemanticChoiceError(
            "Modular transfer count does not match last-known information"
        )
    return player, card_ref, amount, canonical_snapshot, source_ref


@dataclass(frozen=True, slots=True)
class ModularCounterTransferHandler:
    """Resolve Modular's optional, targeted LKI-sized counter placement."""

    operation: str = "offer_modular_counter_transfer"
    handler_id: str = "choice.counter.modular-transfer.v1"
    schema_version: int = 1
    rule_references: tuple[str, ...] = (
        "CR 115.1d",
        "CR 122.1",
        "CR 122.6",
        "CR 603.3d",
        "CR 603.6c",
        "CR 603.10a",
        "CR 608.2b",
        "CR 702.43a",
    )
    capability_dependencies: tuple[str, ...] = (
        "counter.producer.modular",
    )
    continuation_fields: tuple[str, ...] = tuple(sorted(_FIELDS - {"op"}))
    private_data: tuple[str, ...] = ()
    projected_fields: tuple[str, ...] = (
        "prompt",
        "legal_actions.choice_schema.legal_values",
    )
    mutation_path: tuple[str, ...] = (
        "PlaceCountersIntent",
        "counter_placement.prepare_counter_placements",
    )
    replay_fixture: str = "fixed-modular-counter-transfer"
    test_modules: tuple[str, ...] = ("tests.test_modular_rules",)

    def prepare(
        self,
        effect: Mapping[str, Any],
        context: SemanticChoiceContext,
    ) -> SemanticChoicePreparation:
        player, card_ref, amount, snapshot, source_ref = _validated_effect(
            effect,
            actor=context.actor,
            active_seats=context.query.active_seats,
        )
        continuation = FrozenMap(
            {
                "op": self.operation,
                "player": player,
                "card": card_ref,
                "amount": amount,
                "counter_snapshot": snapshot,
                "source": source_ref,
                "rule_id": "702.43a",
            }
        )
        if amount == 0 or not _artifact_creature_target(
            context.query, card_ref
        ):
            return SemanticChoicePreparation(
                request=None,
                continuation_effect=continuation,
                auto_continue=AutoContinue(
                    "the Modular transfer has no positive legal result"
                ),
            )
        return SemanticChoicePreparation(
            request=SemanticChoiceRequest(
                prompt=(
                    f"Put {amount} +1/+1 counter"
                    f"{'s' if amount != 1 else ''} on {card_ref}?"
                ),
                choice=ScalarChoice(
                    field_name="choice",
                    legal_values=("put", "decline"),
                ),
                public_context=FrozenMap(
                    {
                        "stack": context.stack_ref,
                        "operation": self.operation,
                        "target": card_ref,
                        "amount": amount,
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
        actor = continuation.effect.get("player")
        if type(actor) is not str:
            raise SemanticChoiceError("Modular continuation chooser is malformed")
        player, card_ref, amount, _snapshot, source_ref = _validated_effect(
            continuation.effect,
            actor=actor,
            active_seats=query.active_seats,
        )
        choice = response.get("choice")
        if type(choice) is not str or choice not in {"put", "decline"}:
            raise SemanticChoiceError("Choose put or decline")
        if choice == "decline":
            return SemanticChoiceCompletion()
        if amount == 0 or not _artifact_creature_target(query, card_ref):
            raise SemanticChoiceError(
                "The Modular target or counter amount is no longer legal"
            )
        return SemanticChoiceCompletion(
            prepend_effects=(
                FrozenMap(
                    {
                        "op": "place_counters",
                        "card": card_ref,
                        "counter": "+1/+1",
                        "amount": amount,
                        "source": source_ref,
                        _REASON_FIELD: "Modular",
                    }
                ),
            )
        )


MODULAR_CHOICE_HANDLERS = (ModularCounterTransferHandler(),)


__all__ = ["MODULAR_CHOICE_HANDLERS", "ModularCounterTransferHandler"]
