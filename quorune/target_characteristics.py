from __future__ import annotations

"""Immutable current characteristics used by direct-target legality."""

from dataclasses import dataclass
from typing import Any, Mapping

from .characteristic_evaluation import type_parts
from .targets import TargetGroup


@dataclass(frozen=True, slots=True)
class TargetCharacteristicSnapshot:
    types: frozenset[str] = frozenset()
    subtypes: frozenset[str] = frozenset()
    supertypes: frozenset[str] = frozenset()
    keywords: frozenset[str] = frozenset()
    colors: frozenset[str] = frozenset()
    mana_value: float = 0.0

    @classmethod
    def from_effective_data(
        cls,
        data: Mapping[str, Any],
    ) -> "TargetCharacteristicSnapshot":
        types, subtypes, supertypes = type_parts(
            str(data.get("type_line") or "")
        )
        return cls(
            types=frozenset(types),
            subtypes=frozenset(subtypes),
            supertypes=frozenset(supertypes),
            keywords=frozenset(
                str(value).casefold()
                for value in data.get("keywords", ())
            ),
            colors=frozenset(
                str(value).upper() for value in data.get("colors", ())
            ),
            mana_value=float(
                data.get("mana_value", data.get("cmc", 0)) or 0
            ),
        )

    @classmethod
    def from_row(
        cls,
        row: Mapping[str, Any],
    ) -> "TargetCharacteristicSnapshot":
        return cls(
            types=frozenset(
                str(value).casefold() for value in row.get("types", ())
            ),
            subtypes=frozenset(
                str(value).casefold() for value in row.get("subtypes", ())
            ),
            supertypes=frozenset(
                str(value).casefold() for value in row.get("supertypes", ())
            ),
            keywords=frozenset(
                str(value).casefold() for value in row.get("keywords", ())
            ),
            colors=frozenset(
                str(value).upper() for value in row.get("colors", ())
            ),
            mana_value=float(row.get("mana_value", 0) or 0),
        )

    def row_values(self) -> dict[str, Any]:
        return {
            "types": set(self.types),
            "subtypes": set(self.subtypes),
            "supertypes": set(self.supertypes),
            "keywords": set(self.keywords),
            "colors": set(self.colors),
            "mana_value": self.mana_value,
        }

    def matches(self, group: TargetGroup) -> bool:
        return group.matches_type_characteristics(
            types=self.types,
            subtypes=self.subtypes,
            supertypes=self.supertypes,
        ) and group.matches_keyword_characteristics(keywords=self.keywords)


__all__ = ["TargetCharacteristicSnapshot"]
