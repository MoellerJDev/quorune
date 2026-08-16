from __future__ import annotations

"""Closed typed descriptors for represented cumulative-upkeep costs."""

from dataclasses import dataclass
import re
from typing import Any, Mapping

from .fixed_mana_abilities import MANA_COST_KEYS
from .replacement.immutable import FrozenMap, thaw_value
from .util import mana_cost_to_vector


CUMULATIVE_UPKEEP_MECHANIC_ID = "cumulative upkeep"
_ORDINARY_COST = r"(?:\{(?:0|[1-9]\d*|[WUBRGC])\})+"
_ORDINARY_CUMULATIVE_UPKEEP = re.compile(
    rf"^Cumulative upkeep\s+(?P<cost>{_ORDINARY_COST})\.?$",
    re.IGNORECASE,
)
_FIXED_LIFE_COST = re.compile(
    r"^Pay (?P<amount>[1-9]\d*) life$",
    re.IGNORECASE,
)
_FIXED_LIFE_CUMULATIVE_UPKEEP = re.compile(
    r"^Cumulative upkeep[—–]\s*(?P<cost>Pay [1-9]\d* life)\.?$",
    re.IGNORECASE,
)


class CumulativeUpkeepError(ValueError):
    """A represented cumulative-upkeep descriptor is malformed."""


def _require_exact_fields(
    value: Mapping[str, Any], expected: set[str], *, label: str
) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing:
        raise CumulativeUpkeepError(
            f"{label} is missing required fields: {', '.join(missing)}"
        )
    if unknown:
        raise CumulativeUpkeepError(
            f"{label} has unknown fields: {', '.join(unknown)}"
        )


@dataclass(frozen=True, slots=True)
class FixedManaCumulativeUpkeepSpec:
    cost_text: str
    mana_cost: FrozenMap

    def __post_init__(self) -> None:
        if (
            not isinstance(self.cost_text, str)
            or re.fullmatch(_ORDINARY_COST, self.cost_text, re.IGNORECASE)
            is None
        ):
            raise CumulativeUpkeepError(
                "Cumulative upkeep cost must contain only fixed ordinary mana symbols"
            )
        if not isinstance(self.mana_cost, FrozenMap):
            if not isinstance(self.mana_cost, Mapping):
                raise CumulativeUpkeepError(
                    "Cumulative upkeep mana cost must be an object"
                )
            object.__setattr__(self, "mana_cost", FrozenMap(self.mana_cost))
        mana = thaw_value(self.mana_cost)
        if set(mana) != set(MANA_COST_KEYS) or any(
            type(amount) is not int or amount < 0
            for amount in mana.values()
        ):
            raise CumulativeUpkeepError(
                "Cumulative upkeep mana cost must use canonical nonnegative keys"
            )
        if not any(mana.values()):
            raise CumulativeUpkeepError(
                "Cumulative upkeep fixed mana cost must be positive"
            )
        expected, complex_symbols = mana_cost_to_vector(self.cost_text)
        if complex_symbols or mana != expected:
            raise CumulativeUpkeepError(
                "Cumulative upkeep mana cost does not match the printed cost"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cost_text": self.cost_text,
            "mana_cost": thaw_value(self.mana_cost),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "FixedManaCumulativeUpkeepSpec":
        _require_exact_fields(
            value,
            {"cost_text", "mana_cost"},
            label="fixed-mana cumulative upkeep",
        )
        cost_text = value["cost_text"]
        mana_cost = value["mana_cost"]
        if not isinstance(cost_text, str) or not isinstance(mana_cost, Mapping):
            raise CumulativeUpkeepError(
                "Cumulative upkeep descriptor fields have invalid types"
            )
        return cls(cost_text=cost_text, mana_cost=FrozenMap(mana_cost))

    def effect_descriptor(self) -> dict[str, Any]:
        return {
            "op": "cumulative_upkeep",
            "player": "$controller",
            "source": "$source",
            "cost_per_counter": thaw_value(self.mana_cost),
        }


@dataclass(frozen=True, slots=True)
class FixedLifeCumulativeUpkeepSpec:
    """One positive fixed life payment for each committed age counter."""

    cost_text: str
    life_per_counter: int

    def __post_init__(self) -> None:
        if not isinstance(self.cost_text, str):
            raise CumulativeUpkeepError(
                "Cumulative upkeep life cost must be text"
            )
        match = _FIXED_LIFE_COST.fullmatch(self.cost_text)
        if match is None:
            raise CumulativeUpkeepError(
                "Cumulative upkeep life cost must be one fixed positive amount"
            )
        if (
            type(self.life_per_counter) is not int
            or self.life_per_counter <= 0
            or int(match.group("amount")) != self.life_per_counter
        ):
            raise CumulativeUpkeepError(
                "Cumulative upkeep life amount does not match the printed cost"
            )
        object.__setattr__(
            self,
            "cost_text",
            f"Pay {self.life_per_counter} life",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cost_text": self.cost_text,
            "life_per_counter": self.life_per_counter,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "FixedLifeCumulativeUpkeepSpec":
        _require_exact_fields(
            value,
            {"cost_text", "life_per_counter"},
            label="fixed-life cumulative upkeep",
        )
        cost_text = value["cost_text"]
        life_per_counter = value["life_per_counter"]
        if (
            not isinstance(cost_text, str)
            or type(life_per_counter) is not int
        ):
            raise CumulativeUpkeepError(
                "Cumulative upkeep life descriptor fields have invalid types"
            )
        return cls(
            cost_text=cost_text,
            life_per_counter=life_per_counter,
        )

    def effect_descriptor(self) -> dict[str, Any]:
        return {
            "op": "cumulative_upkeep_life",
            "player": "$controller",
            "source": "$source",
            "life_per_counter": self.life_per_counter,
        }


def compile_fixed_mana_cumulative_upkeep(
    material_line: str,
) -> FixedManaCumulativeUpkeepSpec | None:
    """Compile exactly one ordinary fixed-mana cumulative-upkeep line."""

    match = _ORDINARY_CUMULATIVE_UPKEEP.fullmatch(material_line.strip())
    if match is None:
        return None
    cost_text = match.group("cost").upper()
    mana_cost, complex_symbols = mana_cost_to_vector(cost_text)
    if complex_symbols or not any(mana_cost.values()):
        return None
    return FixedManaCumulativeUpkeepSpec(
        cost_text=cost_text,
        mana_cost=FrozenMap(mana_cost),
    )


def compile_fixed_life_cumulative_upkeep(
    material_line: str,
) -> FixedLifeCumulativeUpkeepSpec | None:
    """Compile exactly one fixed positive life cumulative-upkeep line."""

    match = _FIXED_LIFE_CUMULATIVE_UPKEEP.fullmatch(material_line.strip())
    if match is None:
        return None
    cost_text = match.group("cost")
    cost_match = _FIXED_LIFE_COST.fullmatch(cost_text)
    if cost_match is None:
        return None
    amount = int(cost_match.group("amount"))
    return FixedLifeCumulativeUpkeepSpec(
        cost_text=f"Pay {amount} life",
        life_per_counter=amount,
    )


__all__ = [
    "CUMULATIVE_UPKEEP_MECHANIC_ID",
    "CumulativeUpkeepError",
    "FixedLifeCumulativeUpkeepSpec",
    "FixedManaCumulativeUpkeepSpec",
    "compile_fixed_life_cumulative_upkeep",
    "compile_fixed_mana_cumulative_upkeep",
]
