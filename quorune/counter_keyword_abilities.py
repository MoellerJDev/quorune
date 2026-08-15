from __future__ import annotations

"""Typed fixed counter-producing keyword activation descriptors."""

from dataclasses import dataclass
import re
from typing import Any, Mapping

from .abilities import ActivatedAbility
from .fixed_mana_abilities import MANA_COST_KEYS
from .replacement.immutable import FrozenMap, thaw_value
from .util import mana_cost_to_vector


COUNTER_KEYWORD_ACTIVATION_HANDLER_ID = (
    "ability.activated.fixed-counter-keyword.v1"
)
FIXED_COUNTER_KEYWORD_MECHANICS = frozenset(
    {"level up", "outlast", "reinforce", "scavenge"}
)
_ABILITY_ID = re.compile(r"^ab[1-9][0-9]*$")
_ORDINARY_COST = r"(?:\{(?:0|[1-9]\d*|[WUBRGC])\})+"
_GRAMMARS = {
    "level up": re.compile(
        rf"^Level up\s+(?P<cost>{_ORDINARY_COST})\.?$",
        re.IGNORECASE,
    ),
    "outlast": re.compile(
        rf"^Outlast\s+(?P<cost>{_ORDINARY_COST})\.?$",
        re.IGNORECASE,
    ),
    "reinforce": re.compile(
        rf"^Reinforce\s+(?P<amount>[1-9]\d*)\s*[\-\u2013\u2014]\s*"
        rf"(?P<cost>{_ORDINARY_COST})\.?$",
        re.IGNORECASE,
    ),
    "scavenge": re.compile(
        rf"^Scavenge\s+(?P<cost>{_ORDINARY_COST})\.?$",
        re.IGNORECASE,
    ),
}
_CREATURE_TARGET = FrozenMap(
    {
        "zones": ["battlefield"],
        "categories": ["permanent"],
        "types_any": ["creature"],
        "count": 1,
    }
)


class CounterKeywordAbilityError(ValueError):
    """A fixed counter-keyword activation descriptor is malformed."""


def _exact_fields(
    value: Mapping[str, Any], expected: set[str], *, field: str
) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing:
        raise CounterKeywordAbilityError(
            f"{field} is missing required fields: {', '.join(missing)}"
        )
    if unknown:
        raise CounterKeywordAbilityError(
            f"{field} has unknown fields: {', '.join(unknown)}"
        )


@dataclass(frozen=True, slots=True)
class FixedCounterKeywordAbilitySpec:
    ability_id: str
    line_index: int
    oracle_line: str
    mechanic: str
    cost_text: str
    mana_cost: FrozenMap
    amount: int

    def __post_init__(self) -> None:
        if (
            type(self.ability_id) is not str
            or _ABILITY_ID.fullmatch(self.ability_id) is None
        ):
            raise CounterKeywordAbilityError("Ability ID must be abN")
        if type(self.line_index) is not int or self.line_index < 0:
            raise CounterKeywordAbilityError(
                "Ability line_index must be nonnegative"
            )
        if type(self.oracle_line) is not str or not self.oracle_line:
            raise CounterKeywordAbilityError(
                "Ability oracle_line must be nonempty"
            )
        if self.mechanic not in FIXED_COUNTER_KEYWORD_MECHANICS:
            raise CounterKeywordAbilityError(
                "Counter-keyword mechanic is unsupported"
            )
        if (
            type(self.cost_text) is not str
            or re.fullmatch(_ORDINARY_COST, self.cost_text) is None
        ):
            raise CounterKeywordAbilityError(
                "Counter-keyword cost must use fixed ordinary mana symbols"
            )
        if not isinstance(self.mana_cost, FrozenMap):
            if not isinstance(self.mana_cost, Mapping):
                raise CounterKeywordAbilityError("Mana cost must be an object")
            object.__setattr__(self, "mana_cost", FrozenMap(self.mana_cost))
        mana = thaw_value(self.mana_cost)
        if set(mana) != set(MANA_COST_KEYS) or any(
            type(value) is not int or value < 0 for value in mana.values()
        ):
            raise CounterKeywordAbilityError(
                "Mana cost must contain canonical nonnegative keys"
            )
        expected_mana, complex_symbols = mana_cost_to_vector(self.cost_text)
        if complex_symbols or mana != expected_mana:
            raise CounterKeywordAbilityError(
                "Mana cost does not match the printed cost"
            )
        if type(self.amount) is not int or self.amount <= 0:
            raise CounterKeywordAbilityError(
                "Counter amount must be a positive exact integer"
            )
        if self.mechanic in {"level up", "outlast"} and self.amount != 1:
            raise CounterKeywordAbilityError(
                f"{self.mechanic.title()} must place exactly one counter"
            )

    @property
    def counter_name(self) -> str:
        return "level" if self.mechanic == "level up" else "+1/+1"

    @property
    def targets_creature(self) -> bool:
        return self.mechanic in {"reinforce", "scavenge"}

    @property
    def active_zone(self) -> str:
        return {
            "level up": "battlefield",
            "outlast": "battlefield",
            "reinforce": "hand",
            "scavenge": "graveyard",
        }[self.mechanic]

    @property
    def has_zone_change_source_cost(self) -> bool:
        return self.mechanic in {"reinforce", "scavenge"}

    @property
    def sorcery_speed(self) -> bool:
        return self.mechanic in {"level up", "outlast", "scavenge"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "ability_id": self.ability_id,
            "line_index": self.line_index,
            "oracle_line": self.oracle_line,
            "mechanic": self.mechanic,
            "cost_text": self.cost_text,
            "mana_cost": thaw_value(self.mana_cost),
            "amount": self.amount,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "FixedCounterKeywordAbilitySpec":
        _exact_fields(
            value,
            {
                "ability_id",
                "line_index",
                "oracle_line",
                "mechanic",
                "cost_text",
                "mana_cost",
                "amount",
            },
            field="fixed counter-keyword ability",
        )
        if not all(
            type(value[field]) is str
            for field in (
                "ability_id",
                "oracle_line",
                "mechanic",
                "cost_text",
            )
        ):
            raise CounterKeywordAbilityError(
                "Counter-keyword ability text fields must be strings"
            )
        mana_cost = value["mana_cost"]
        if not isinstance(mana_cost, Mapping):
            raise CounterKeywordAbilityError("Mana cost must be an object")
        return cls(
            ability_id=value["ability_id"],
            line_index=value["line_index"],
            oracle_line=value["oracle_line"],
            mechanic=value["mechanic"],
            cost_text=value["cost_text"],
            mana_cost=FrozenMap(mana_cost),
            amount=value["amount"],
        )

    def to_activated_ability(self) -> ActivatedAbility:
        cost_tail = {
            "level up": "",
            "outlast": ", {T}",
            "reinforce": ", Discard this card",
            "scavenge": ", Exile this card from your graveyard",
        }[self.mechanic]
        return ActivatedAbility(
            ability_id=self.ability_id,
            line_index=self.line_index,
            oracle_line=self.oracle_line,
            cost_text=f"{self.cost_text}{cost_tail}",
            effect_text=(
                f"Put {self.amount} {self.counter_name} counter"
                f"{'s' if self.amount != 1 else ''} on "
                f"{'target creature' if self.targets_creature else 'this permanent'}."
            ),
            zones=(self.active_zone,),
            mana=thaw_value(self.mana_cost),
            tap_source=self.mechanic == "outlast",
            discard_source=self.mechanic == "reinforce",
            exile_source=self.mechanic == "scavenge",
            sorcery_speed=self.sorcery_speed,
            target_schema=_CREATURE_TARGET if self.targets_creature else None,
        )


def compile_fixed_counter_keyword_ability(
    *,
    material_line: str,
    oracle_line: str,
    line_index: int,
    mechanic: str,
    printed_power: str | None,
) -> FixedCounterKeywordAbilitySpec | None:
    """Compile one bounded keyword activation or return ``None``."""

    normalized_mechanic = mechanic.casefold()
    grammar = _GRAMMARS.get(normalized_mechanic)
    if grammar is None:
        return None
    match = grammar.fullmatch(material_line.strip())
    if match is None:
        return None
    if normalized_mechanic == "reinforce":
        amount = int(match.group("amount"))
    elif normalized_mechanic == "scavenge":
        normalized_power = str(printed_power or "").strip()
        if re.fullmatch(r"[1-9]\d*", normalized_power) is None:
            return None
        amount = int(normalized_power)
    else:
        amount = 1
    cost_text = match.group("cost").upper()
    mana_cost, complex_symbols = mana_cost_to_vector(cost_text)
    if complex_symbols:
        return None
    return FixedCounterKeywordAbilitySpec(
        ability_id=f"ab{line_index + 1}",
        line_index=line_index,
        oracle_line=oracle_line,
        mechanic=normalized_mechanic,
        cost_text=cost_text,
        mana_cost=FrozenMap(mana_cost),
        amount=amount,
    )


def fixed_counter_keyword_handler_descriptor(
    spec: FixedCounterKeywordAbilitySpec,
) -> dict[str, Any]:
    return {
        "handler_id": COUNTER_KEYWORD_ACTIVATION_HANDLER_ID,
        "schema_version": 1,
        "event": "activate",
        "ability": spec.to_dict(),
    }


__all__ = [
    "COUNTER_KEYWORD_ACTIVATION_HANDLER_ID",
    "FIXED_COUNTER_KEYWORD_MECHANICS",
    "CounterKeywordAbilityError",
    "FixedCounterKeywordAbilitySpec",
    "compile_fixed_counter_keyword_ability",
    "fixed_counter_keyword_handler_descriptor",
]
