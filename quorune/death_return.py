from __future__ import annotations

"""Closed typed values shared by printed Persist and Undying."""

from dataclasses import dataclass
from typing import Any, Mapping

from .counter_snapshot import (
    CounterSnapshotError,
    permanent_counter_snapshot,
)
from .replacement.immutable import FrozenMap


DEATH_RETURN_EVENT_CONDITION_FIELD = "death_return_departed_without_counter"
PERSIST_KEYWORD = "persist"
UNDYING_KEYWORD = "undying"


class DeathReturnError(ValueError):
    """A death-return keyword or its last-known counter facts are malformed."""


@dataclass(frozen=True, slots=True)
class DeathReturnSpec:
    keyword: str
    prohibited_counter: str
    entry_counter: str
    rule_id: str
    capability_id: str

    def __post_init__(self) -> None:
        expected = _DEATH_RETURN_SPECS.get(str(self.keyword).casefold())
        actual = (
            str(self.prohibited_counter).casefold(),
            str(self.entry_counter).casefold(),
            str(self.rule_id),
            str(self.capability_id),
        )
        if expected is None or actual != expected:
            raise DeathReturnError(
                "Death-return specifications must be canonical Persist or Undying"
            )
        object.__setattr__(self, "keyword", self.keyword.casefold())
        object.__setattr__(
            self, "prohibited_counter", self.prohibited_counter.casefold()
        )
        object.__setattr__(self, "entry_counter", self.entry_counter.casefold())

    @classmethod
    def for_keyword(cls, keyword: str) -> "DeathReturnSpec":
        normalized = str(keyword).casefold()
        values = _DEATH_RETURN_SPECS.get(normalized)
        if values is None:
            raise DeathReturnError(
                f"Unsupported death-return keyword {keyword!r}"
            )
        prohibited, entry, rule_id, capability_id = values
        return cls(
            keyword=normalized,
            prohibited_counter=prohibited,
            entry_counter=entry,
            rule_id=rule_id,
            capability_id=capability_id,
        )

    def event_condition(self) -> dict[str, Any]:
        return {
            "field": DEATH_RETURN_EVENT_CONDITION_FIELD,
            "counter": self.prohibited_counter,
            "op": "truthy",
        }

    def effect_descriptor(self) -> dict[str, Any]:
        return {
            "op": "death_return_with_counter",
            "player": "$controller",
            "card": "$source",
            "expected_zone_change_counter": (
                "$context.card_zone_change_counter"
            ),
            "departure_counters": "$context.death_return_counter_snapshot",
            "prohibited_counter": self.prohibited_counter,
            "entry_counter": self.entry_counter,
            "source": "$stack",
            "rule_id": self.rule_id,
        }


_DEATH_RETURN_SPECS: dict[str, tuple[str, str, str, str]] = {
    PERSIST_KEYWORD: (
        "-1/-1",
        "-1/-1",
        "702.79a",
        "counter.producer.persist",
    ),
    UNDYING_KEYWORD: (
        "+1/+1",
        "+1/+1",
        "702.93a",
        "counter.producer.undying",
    ),
}


def death_return_counter_snapshot(
    counters: Mapping[str, Any],
) -> FrozenMap:
    """Deep-freeze the public LKI counter map used by the intervening-if."""

    try:
        return permanent_counter_snapshot(counters)
    except CounterSnapshotError as exc:
        raise DeathReturnError(
            f"Death-return last-known counters are malformed: {exc}"
        ) from exc


def death_return_condition_holds(
    counters: Mapping[str, Any],
    prohibited_counter: str,
) -> bool:
    """Evaluate the fixed last-known counter predicate for one keyword."""

    snapshot = death_return_counter_snapshot(counters)
    name = " ".join(str(prohibited_counter).casefold().split())
    if name not in {"-1/-1", "+1/+1"}:
        raise DeathReturnError(
            "Death-return conditions require a canonical prohibiting counter"
        )
    return int(snapshot.get(name, 0)) == 0


__all__ = [
    "DEATH_RETURN_EVENT_CONDITION_FIELD",
    "DeathReturnError",
    "DeathReturnSpec",
    "PERSIST_KEYWORD",
    "UNDYING_KEYWORD",
    "death_return_condition_holds",
    "death_return_counter_snapshot",
]
