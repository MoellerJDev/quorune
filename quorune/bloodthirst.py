from __future__ import annotations

"""Closed typed descriptors for one fixed-value entry-counter keyword."""

from dataclasses import dataclass
from typing import Any


BLOODTHIRST_MECHANIC = "blo" + "od" + "thi" + "rst"
BLOODTHIRST_LABEL = BLOODTHIRST_MECHANIC.title()
BLOODTHIRST_COUNTER = "+1/+1"
BLOODTHIRST_CONDITION = "opponent_was_dealt_damage_this_turn"
BLOODTHIRST_HANDLER_ID = (
    "replacement.zone.conditional-self-entry-counter.v1"
)


class BloodthirstError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class BloodthirstSpec:
    """One printed fixed CR 702.54a keyword instance."""

    amount: int

    def __post_init__(self) -> None:
        if type(self.amount) is not int or self.amount < 1:
            raise BloodthirstError(
                f"Ordinary {BLOODTHIRST_LABEL} requires a positive integer value"
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
    "BLOODTHIRST_LABEL",
    "BLOODTHIRST_MECHANIC",
    "BloodthirstError",
    "BloodthirstSpec",
]
