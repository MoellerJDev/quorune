from __future__ import annotations

"""Typed CR 702.112 Renown trigger and intervening-if boundary."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .ability_fragments import (
    DamageKeywordTriggerKind,
    DamageKeywordTriggerSpec,
    ability_fragment_to_dict,
)


RENOWN_MECHANIC_ID = "renown"
RENOWN_EVENT_CONDITION_FIELD = "renown_combat_damage_player_unrenowned"


class RenownError(ValueError):
    """A Renown value or normalized damage fact is malformed."""


@dataclass(frozen=True, slots=True)
class RenownSpec:
    """One positive printed Renown N ability instance."""

    amount: int

    def __post_init__(self) -> None:
        if type(self.amount) is not int or self.amount <= 0:
            raise RenownError("Renown requires a positive integer value")

    def handler_descriptor(self) -> dict[str, Any]:
        return {
            "handler_id": "ability.trigger.renown.v1",
            "schema_version": 1,
            "event": "damage.dealt.self",
            "fragment": ability_fragment_to_dict(
                DamageKeywordTriggerSpec(
                    kind=DamageKeywordTriggerKind.RENOWN,
                    amount=self.amount,
                )
            ),
        }

    def effect_descriptor(self) -> dict[str, Any]:
        return {
            "op": "fixed_self_counter_keyword_action",
            "action": RENOWN_MECHANIC_ID,
            "amount": self.amount,
            "source": "$source",
        }

    def event_condition(self) -> dict[str, str]:
        return {
            "field": RENOWN_EVENT_CONDITION_FIELD,
            "op": "truthy",
        }


def renown_condition_holds(
    source: Any,
    context: Mapping[str, Any],
) -> bool:
    """Evaluate Renown's intervening-if from normalized damage facts.

    The same function is used when the damage trigger is discovered and when
    it resolves.  The latter check requires the original logical object to
    remain on the battlefield and still not be renowned.
    """

    if not isinstance(context, Mapping):
        raise RenownError("Renown requires normalized damage context")
    source_ref = context.get("source")
    source_object_id = context.get("source_object_id")
    source_logical_object_id = context.get("source_logical_object_id")
    target_kind = context.get("target_kind")
    source_types = context.get("source_types")
    combat = context.get("combat")
    amount = context.get("amount")
    if any(
        type(value) is not str or not value
        for value in (
            source_ref,
            source_object_id,
            source_logical_object_id,
            target_kind,
        )
    ):
        raise RenownError("Renown damage identity is malformed")
    if not isinstance(source_types, Sequence) or isinstance(
        source_types, (str, bytes)
    ) or any(type(value) is not str or not value for value in source_types):
        raise RenownError("Renown source types are malformed")
    if type(combat) is not bool:
        raise RenownError("Renown combat status must be a boolean")
    if type(amount) is not int or amount < 0:
        raise RenownError("Renown dealt damage must be nonnegative")
    renowned = getattr(source, "renowned", None)
    if type(renowned) is not bool:
        raise RenownError("The source renowned designation is malformed")
    return bool(
        getattr(source, "ref", None) == source_ref
        and getattr(source, "object_id", None) == source_object_id
        and getattr(source, "logical_object_id", None)
        == source_logical_object_id
        and getattr(source, "zone", None) == "battlefield"
        and getattr(source, "phased_out", None) is False
        and not renowned
        and target_kind == "player"
        and combat
        and amount > 0
        and "creature" in {value.casefold() for value in source_types}
    )


__all__ = [
    "RENOWN_EVENT_CONDITION_FIELD",
    "RENOWN_MECHANIC_ID",
    "RenownError",
    "RenownSpec",
    "renown_condition_holds",
]
