from __future__ import annotations

"""Closed typed descriptors for ordinary fixed-value Bloodthirst."""

from dataclasses import dataclass
from typing import Any


BLOODTHIRST_MECHANIC = "blood" + "thirst"
BLOODTHIRST_COUNTER = "+1/+1"
BLOODTHIRST_CONDITION = "opponent_was_dealt_damage_this_turn"
BLOODTHIRST_HANDLER_ID = (
    "replacement.zone.conditional-self-entry-counter.v1"
)


class BloodthirstError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class BloodthirstSpec:
    """One printed CR 702.54a Bloodthirst N instance."""

    amount: int

    def __post_init__(self) -> None:
        if type(self.amount) is not int or self.amount < 1:
            raise BloodthirstError(
                "Ordinary Bloodthirst requires a positive integer value"
            )

    def handler_descriptor(self) -> dict[str, Any]:
        return {
            "handler_id": BLOODTHIRST_HANDLER_ID,
            "schema_version": 1,
            "event": "zone.change",
            "condition": BLOODTHIRST_CONDITION,
            "counter_name": BLOODTHIRST_COUNTER,
            "amount": self.amount,
            "rule_id": "702.54a",
        }


__all__ = [
    "BLOODTHIRST_CONDITION",
    "BLOODTHIRST_COUNTER",
    "BLOODTHIRST_HANDLER_ID",
    "BLOODTHIRST_MECHANIC",
    "BloodthirstError",
    "BloodthirstSpec",
]
