from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence


class EntryCounterError(ValueError):
    """An as-enters counter instruction is not representable."""


def _normalized_nonempty(value: Any, *, field: str) -> str:
    if type(value) is not str:
        raise EntryCounterError(f"{field} must be a string")
    normalized = " ".join(value.casefold().split())
    if not normalized:
        raise EntryCounterError(f"{field} must be nonempty")
    return normalized


@dataclass(frozen=True, slots=True)
class IntrinsicEntryCounter:
    counter_name: str
    amount: int
    required_type: str
    rule_id: str

    def __post_init__(self) -> None:
        counter_name = " ".join(self.counter_name.casefold().split())
        required_type = " ".join(self.required_type.casefold().split())
        rule_id = str(self.rule_id or "")
        if not counter_name or not required_type or not rule_id:
            raise EntryCounterError(
                "Intrinsic entry counters require a counter, type, and rule"
            )
        if type(self.amount) is not int or self.amount < 0:
            raise EntryCounterError(
                "Intrinsic entry counter amounts must be nonnegative integers"
            )
        object.__setattr__(self, "counter_name", counter_name)
        object.__setattr__(self, "required_type", required_type)
        object.__setattr__(self, "rule_id", rule_id)


@dataclass(frozen=True, slots=True)
class EffectEntryCounter:
    """One effect-generated counter attached to a proposed battlefield entry."""

    counter_name: str
    amount: int
    placing_player: str
    source_ref: str
    rule_id: str

    def __post_init__(self) -> None:
        counter_name = _normalized_nonempty(
            self.counter_name,
            field="Effect entry counter name",
        )
        if type(self.amount) is not int or self.amount < 1:
            raise EntryCounterError(
                "Effect entry counter amounts must be positive integers"
            )
        for field_name in ("placing_player", "source_ref", "rule_id"):
            value = getattr(self, field_name)
            if type(value) is not str or not value or value != value.strip():
                raise EntryCounterError(
                    f"Effect entry counter {field_name} must be a canonical "
                    "nonempty string"
                )
        object.__setattr__(self, "counter_name", counter_name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "counter_name": self.counter_name,
            "amount": self.amount,
            "placing_player": self.placing_player,
            "source_ref": self.source_ref,
            "rule_id": self.rule_id,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "EffectEntryCounter":
        if not isinstance(value, Mapping):
            raise EntryCounterError(
                "Effect entry counter serialization must be an object"
            )
        expected = {
            "counter_name",
            "amount",
            "placing_player",
            "source_ref",
            "rule_id",
        }
        missing = sorted(expected - set(value))
        unknown = sorted(set(value) - expected)
        if missing or unknown:
            details = [
                *(f"missing {field}" for field in missing),
                *(f"unknown {field}" for field in unknown),
            ]
            raise EntryCounterError(
                "Effect entry counter fields: " + "; ".join(details)
            )
        return cls(
            counter_name=value["counter_name"],
            amount=value["amount"],
            placing_player=value["placing_player"],
            source_ref=value["source_ref"],
            rule_id=value["rule_id"],
        )


def _printed_nonnegative_integer(
    value: Any,
    *,
    characteristic: str,
) -> int:
    if type(value) is int:
        amount = value
    elif type(value) is str and re.fullmatch(r"-?\d+", value.strip()):
        amount = int(value.strip())
    else:
        raise EntryCounterError(
            f"{characteristic} must be a represented nonnegative integer"
        )
    if amount < 0:
        raise EntryCounterError(f"{characteristic} cannot be negative")
    return amount


def intrinsic_entry_counters(
    characteristics: Mapping[str, Any],
    *,
    card_types: Sequence[str],
) -> tuple[IntrinsicEntryCounter, ...]:
    """Return the closed CR 306.5b/310.4b entry-counter instructions."""

    if not isinstance(characteristics, Mapping):
        raise EntryCounterError(
            "Entry counter characteristics must be a mapping"
        )
    types = {" ".join(str(value).casefold().split()) for value in card_types}
    counters: list[IntrinsicEntryCounter] = []
    if "planeswalker" in types:
        counters.append(
            IntrinsicEntryCounter(
                counter_name="loyalty",
                amount=_printed_nonnegative_integer(
                    characteristics.get("loyalty"),
                    characteristic="Starting loyalty",
                ),
                required_type="planeswalker",
                rule_id="306.5b",
            )
        )
    if "battle" in types:
        counters.append(
            IntrinsicEntryCounter(
                counter_name="defense",
                amount=_printed_nonnegative_integer(
                    characteristics.get("defense"),
                    characteristic="Battle defense",
                ),
                required_type="battle",
                rule_id="310.4b",
            )
        )
    return tuple(counters)


__all__ = [
    "EntryCounterError",
    "EffectEntryCounter",
    "IntrinsicEntryCounter",
    "intrinsic_entry_counters",
]
