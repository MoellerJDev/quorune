from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Any, Mapping

from .card_programs.admission import REQUIRES_COMPLETE_CARD_PROGRAM_FIELD
from .replacement.immutable import FrozenMap, thaw_value
from .util import mana_cost_to_vector, stable_json


BESTOW_MECHANIC_ID = "bestow"
BESTOW_CAPABILITY_ID = "casting.bestow.fixed_mana"
BESTOW_HANDLER_ID = "casting.bestow.fixed-mana.v1"
BESTOW_RUNTIME_EVENT = "cast.cost"
BESTOW_CAST_OPTION_ID = "bestow"
_ABILITY_ID = re.compile(r"^ab[1-9][0-9]*$")
_ORDINARY_COST = r"(?:\{(?:0|[1-9]\d*|[WUBRGC])\})+"
_BESTOW = re.compile(
    rf"^Bestow (?P<cost>{_ORDINARY_COST})(?:\s+\(.*\))?\.?$",
    re.IGNORECASE,
)
_MANA_FIELDS = ("GENERIC", "W", "U", "B", "R", "G", "C")


class BestowError(ValueError):
    """A fixed-mana Bestow descriptor is malformed."""


@dataclass(frozen=True, slots=True)
class FixedManaBestowSpec:
    ability_id: str
    line_index: int
    oracle_line: str
    cost_text: str
    mana_cost: FrozenMap
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise BestowError("Unsupported fixed-mana Bestow schema version")
        if (
            type(self.ability_id) is not str
            or _ABILITY_ID.fullmatch(self.ability_id) is None
        ):
            raise BestowError("Bestow ability ID must be abN")
        if type(self.line_index) is not int or self.line_index < 0:
            raise BestowError("Bestow line index must be nonnegative")
        if self.ability_id != f"ab{self.line_index + 1}":
            raise BestowError("Bestow ability ID does not match its source line")
        if type(self.oracle_line) is not str or not self.oracle_line:
            raise BestowError("Bestow Oracle line is required")
        oracle_match = _BESTOW.fullmatch(self.oracle_line.strip())
        if oracle_match is None:
            raise BestowError("Bestow Oracle line is outside the closed grammar")
        if (
            type(self.cost_text) is not str
            or re.fullmatch(_ORDINARY_COST, self.cost_text) is None
        ):
            raise BestowError("Bestow cost must use fixed ordinary mana")
        if oracle_match.group("cost").upper() != self.cost_text:
            raise BestowError("Bestow cost does not match its Oracle line")
        if not isinstance(self.mana_cost, FrozenMap):
            if not isinstance(self.mana_cost, Mapping):
                raise BestowError("Bestow mana cost must be an object")
            object.__setattr__(self, "mana_cost", FrozenMap(self.mana_cost))
        mana = thaw_value(self.mana_cost)
        expected, complex_symbols = mana_cost_to_vector(self.cost_text)
        if (
            set(mana) != set(_MANA_FIELDS)
            or any(type(value) is not int or value < 0 for value in mana.values())
            or complex_symbols
            or mana != expected
        ):
            raise BestowError("Bestow mana vector does not match its cost")

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(stable_json(self.to_dict()).encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ability_id": self.ability_id,
            "line_index": self.line_index,
            "oracle_line": self.oracle_line,
            "cost_text": self.cost_text,
            "mana_cost": thaw_value(self.mana_cost),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "FixedManaBestowSpec":
        expected = {
            "schema_version", "ability_id", "line_index", "oracle_line",
            "cost_text", "mana_cost",
        }
        if not isinstance(value, Mapping) or set(value) != expected:
            raise BestowError("Fixed-mana Bestow descriptors have a closed schema")
        mana_cost = value["mana_cost"]
        if not isinstance(mana_cost, Mapping):
            raise BestowError("Bestow mana cost must be an object")
        return cls(
            ability_id=value["ability_id"],
            line_index=value["line_index"],
            oracle_line=value["oracle_line"],
            cost_text=value["cost_text"],
            mana_cost=FrozenMap(mana_cost),
            schema_version=value["schema_version"],
        )

    def cast_cost_option(self) -> dict[str, Any]:
        return {
            "id": BESTOW_CAST_OPTION_ID,
            "kind": "alternate",
            "label": f"Bestow {self.cost_text}",
            "requirements": thaw_value(self.mana_cost),
            "bestow_fingerprint": self.fingerprint,
            "cast_type_line": "Enchantment — Aura",
            "target_schema": {
                "zones": ["battlefield"],
                "categories": ["permanent"],
                "creature": True,
                "count": 1,
            },
            "effects": [
                {"op": "bestow_prepare", "aura": "$card", "card": "$target.0"}
            ],
        }


def compile_fixed_mana_bestow(
    *, material_line: str, oracle_line: str, line_index: int,
) -> FixedManaBestowSpec | None:
    match = _BESTOW.fullmatch(material_line.strip())
    if match is None:
        return None
    cost = match.group("cost").upper()
    mana, complex_symbols = mana_cost_to_vector(cost)
    if complex_symbols:
        return None
    return FixedManaBestowSpec(
        ability_id=f"ab{line_index + 1}", line_index=line_index,
        oracle_line=oracle_line, cost_text=cost, mana_cost=FrozenMap(mana),
    )


def bestow_handler_descriptor(spec: FixedManaBestowSpec) -> dict[str, Any]:
    return {
        "handler_id": BESTOW_HANDLER_ID,
        "schema_version": 1,
        "event": BESTOW_RUNTIME_EVENT,
        REQUIRES_COMPLETE_CARD_PROGRAM_FIELD: True,
        "bestow": spec.to_dict(),
    }


__all__ = ["BESTOW_CAPABILITY_ID", "BESTOW_CAST_OPTION_ID", "BESTOW_HANDLER_ID", "BESTOW_MECHANIC_ID", "BESTOW_RUNTIME_EVENT", "BestowError", "FixedManaBestowSpec", "bestow_handler_descriptor", "compile_fixed_mana_bestow"]
