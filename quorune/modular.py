from __future__ import annotations

"""Typed CR 702.43 fixed-value Modular lifecycle."""

from dataclasses import dataclass
from typing import Any, Mapping

from .counter_snapshot import (
    CounterSnapshotError,
    permanent_counter_snapshot,
)
from .replacement.immutable import FrozenMap


MODULAR_MECHANIC_ID = "modular"
MODULAR_COUNTER_SNAPSHOT_FIELD = "modular_counter_snapshot"
MODULAR_COUNTER_COUNT_FIELD = "modular_counter_count"


class ModularError(ValueError):
    """A fixed Modular value or departure counter snapshot is malformed."""


@dataclass(frozen=True, slots=True)
class ModularSpec:
    """One positive printed ``Modular N`` ability instance."""

    amount: int

    def __post_init__(self) -> None:
        if type(self.amount) is not int or self.amount <= 0:
            raise ModularError("Modular requires a positive integer value")

    def entry_handler_descriptor(self) -> dict[str, Any]:
        return {
            "handler_id": "replacement.zone.self-entry-counter.v1",
            "schema_version": 1,
            "event": "zone.change",
            "counter_name": "+1/+1",
            "amount": self.amount,
            "optional": False,
            "rule_id": "702.43a",
        }

    def departure_effect_descriptor(self) -> dict[str, Any]:
        return {
            "op": "offer_modular_counter_transfer",
            "player": "$controller",
            "card": "$target.0",
            "amount": f"$context.{MODULAR_COUNTER_COUNT_FIELD}",
            "counter_snapshot": f"$context.{MODULAR_COUNTER_SNAPSHOT_FIELD}",
            "source": "$stack",
            "rule_id": "702.43a",
        }

    @staticmethod
    def target_schema() -> dict[str, Any]:
        return {
            "zones": ["battlefield"],
            "categories": ["permanent"],
            "types_all": ["artifact", "creature"],
            "count": 1,
        }


def modular_counter_snapshot(counters: Mapping[str, Any]) -> FrozenMap:
    """Capture the public LKI counter map used by one Modular trigger."""

    try:
        return permanent_counter_snapshot(counters)
    except CounterSnapshotError as exc:
        raise ModularError(
            f"Modular last-known counters are malformed: {exc}"
        ) from exc


def modular_counter_count(counters: Mapping[str, Any]) -> int:
    """Return the CR 702.43a +1/+1 counter count from an immutable snapshot."""

    return int(modular_counter_snapshot(counters).get("+1/+1", 0))


__all__ = [
    "MODULAR_COUNTER_COUNT_FIELD",
    "MODULAR_COUNTER_SNAPSHOT_FIELD",
    "MODULAR_MECHANIC_ID",
    "ModularError",
    "ModularSpec",
    "modular_counter_count",
    "modular_counter_snapshot",
]
