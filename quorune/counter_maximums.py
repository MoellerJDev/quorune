from __future__ import annotations

"""Typed fixed self-restrictions for CR 704.5r counter maximums."""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .counter_names import CounterStateError, normalized_counter_name


class CounterMaximumError(ValueError):
    """A maximum-counter ability is malformed or outside the closed grammar."""


@dataclass(frozen=True, slots=True)
class CounterMaximumSpec:
    """One immutable fixed maximum for a named counter kind on this object."""

    counter_name: str
    maximum: int
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise CounterMaximumError(
                "Unsupported counter-maximum schema version"
            )
        if type(self.counter_name) is not str:
            raise CounterMaximumError(
                "Counter maximums require a string counter name"
            )
        try:
            counter_name = normalized_counter_name(self.counter_name)
        except CounterStateError as exc:
            raise CounterMaximumError(str(exc)) from exc
        if type(self.maximum) is not int or self.maximum < 0:
            raise CounterMaximumError(
                "Counter maximums require a nonnegative integer"
            )
        object.__setattr__(self, "counter_name", counter_name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "counter_name": self.counter_name,
            "maximum": self.maximum,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CounterMaximumSpec":
        expected = {"schema_version", "counter_name", "maximum"}
        if not isinstance(value, Mapping) or set(value) != expected:
            raise CounterMaximumError(
                "Counter-maximum fragments have a closed schema"
            )
        return cls(**dict(value))


def effective_counter_maximums(
    fragments: Iterable[object],
) -> dict[str, int]:
    """Return the strictest current maximum for each represented counter."""

    maximums: dict[str, int] = {}
    for fragment in fragments:
        if not isinstance(fragment, CounterMaximumSpec):
            continue
        maximums[fragment.counter_name] = min(
            maximums.get(fragment.counter_name, fragment.maximum),
            fragment.maximum,
        )
    return dict(sorted(maximums.items()))


def validated_counter_maximums(
    values: Mapping[object, object],
) -> tuple[tuple[str, int], ...]:
    """Validate and canonicalize one immutable SBA maximum snapshot."""

    maximums: list[tuple[str, int]] = []
    for raw_kind, raw_maximum in values.items():
        if type(raw_kind) is not str:
            raise CounterMaximumError(
                "Counter maximums require a string counter kind"
            )
        try:
            kind = normalized_counter_name(raw_kind)
        except CounterStateError as exc:
            raise CounterMaximumError(str(exc)) from exc
        if type(raw_maximum) is not int:
            raise CounterMaximumError(
                "Counter maximums require an integer value"
            )
        if raw_maximum < 0:
            raise CounterMaximumError(
                "Counter maximums require a nonnegative value"
            )
        maximums.append((kind, raw_maximum))
    return tuple(sorted(maximums))


__all__ = [
    "CounterMaximumError",
    "CounterMaximumSpec",
    "effective_counter_maximums",
    "validated_counter_maximums",
]
