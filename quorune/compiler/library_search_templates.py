from __future__ import annotations

"""Closed Oracle lowering for fixed library searches to the battlefield."""

from dataclasses import dataclass
import re
from typing import Any, Mapping

from ..object_predicate import ObjectQuerySpec
from .fixed_numbers import FIXED_COUNT_PATTERN, fixed_number


FIXED_LIBRARY_SEARCH_MECHANIC_ID = "fixed-library-search-to-battlefield"
FIXED_LIBRARY_SEARCH_CAPABILITY_ID = "library.search.fixed_to_battlefield"

_BASIC_LAND_SUBTYPES = frozenset(
    {"plains", "island", "swamp", "mountain", "forest"}
)
_LAND_SUBTYPES = _BASIC_LAND_SUBTYPES | {"cave", "desert", "gate", "town"}
_PERMANENT_TYPES = frozenset(
    {"artifact", "battle", "creature", "enchantment", "land", "planeswalker"}
)
_COLORS = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
}
_FIXED_SEARCH = re.compile(
    rf"^Search your library for (?P<up_to>up to )?"
    rf"(?P<count>an|{FIXED_COUNT_PATTERN}) "
    rf"(?P<quality>.+?) card(?P<plural>s)?, put (?P<pronoun>it|them) "
    rf"onto the battlefield(?P<tapped> tapped)?, then shuffle\.$",
    re.IGNORECASE,
)


def _or_terms(value: str) -> tuple[str, ...]:
    return tuple(
        part.strip()
        for part in re.split(r",\s*(?:or\s+)?|\s+or\s+", value)
        if part.strip()
    )


def _permanent_query() -> ObjectQuerySpec:
    return ObjectQuerySpec(types_any=tuple(sorted(_PERMANENT_TYPES)))


def _search_query(quality: str) -> ObjectQuerySpec | None:
    normalized = " ".join(quality.casefold().split())
    if normalized == "basic land":
        return ObjectQuerySpec(
            types_all=("land",),
            supertypes_all=("basic",),
        )
    if normalized == "land":
        return ObjectQuerySpec(types_all=("land",))
    if normalized == "snow land":
        return ObjectQuerySpec(
            types_all=("land",),
            supertypes_all=("snow",),
        )
    if normalized == "land with a basic land type":
        return ObjectQuerySpec(
            types_all=("land",),
            subtypes_any=tuple(sorted(_BASIC_LAND_SUBTYPES)),
        )

    basic = normalized.startswith("basic ")
    terms = _or_terms(normalized.removeprefix("basic "))
    if terms and all(term in _LAND_SUBTYPES for term in terms):
        return ObjectQuerySpec(
            types_all=("land",),
            subtypes_any=terms,
            supertypes_all=(("basic",) if basic else ()),
        )
    if basic:
        return None

    if normalized == "permanent":
        return _permanent_query()
    if normalized in _PERMANENT_TYPES:
        return ObjectQuerySpec(types_all=(normalized,))
    if normalized == "equipment":
        return ObjectQuerySpec(
            types_all=("artifact",),
            subtypes_any=("equipment",),
        )
    if normalized.startswith("legendary "):
        subject = normalized.removeprefix("legendary ")
        if subject in _PERMANENT_TYPES:
            return ObjectQuerySpec(
                types_all=(subject,),
                supertypes_all=("legendary",),
            )
        if subject.endswith(" permanent"):
            subtype = subject.removesuffix(" permanent").strip()
            if subtype and " " not in subtype:
                return ObjectQuerySpec(
                    types_any=tuple(sorted(_PERMANENT_TYPES)),
                    subtypes_any=(subtype,),
                    supertypes_all=("legendary",),
                )
        return None
    if normalized.endswith(" creature"):
        qualifier = normalized.removesuffix(" creature").strip()
        if qualifier in _COLORS:
            return ObjectQuerySpec(
                types_all=("creature",),
                colors_any=(_COLORS[qualifier],),
            )
        if qualifier and " " not in qualifier:
            return ObjectQuerySpec(
                types_all=("creature",),
                subtypes_any=(qualifier,),
            )
    if normalized.endswith(" permanent"):
        subtype = normalized.removesuffix(" permanent").strip()
        if subtype and " " not in subtype:
            return ObjectQuerySpec(
                types_any=tuple(sorted(_PERMANENT_TYPES)),
                subtypes_any=(subtype,),
            )
        return None

    type_terms = tuple(
        part.strip()
        for part in re.split(r"\s+and/or\s+|\s+or\s+", normalized)
        if part.strip()
    )
    if type_terms and all(term in _PERMANENT_TYPES for term in type_terms):
        return ObjectQuerySpec(types_any=type_terms)
    return None


def _selector(query: ObjectQuerySpec) -> dict[str, list[str]]:
    fields = {
        "types": query.types_all,
        "types_any": query.types_any,
        "subtypes_any": query.subtypes_any,
        "supertypes": query.supertypes_all,
        "colors_any": query.colors_any,
    }
    return {name: list(values) for name, values in fields.items() if values}


@dataclass(frozen=True, slots=True)
class FixedLibrarySearchTemplate:
    count: int
    optional_count: bool
    query: ObjectQuerySpec
    enters_tapped: bool

    def compiled(
        self,
    ) -> tuple[
        str,
        tuple[Mapping[str, Any], ...],
        None,
        tuple[str, ...],
    ]:
        effect: dict[str, Any] = {
            "op": "search",
            "zone": "library",
            "selector": _selector(self.query),
            "count": {
                "minimum": 0 if self.optional_count else self.count,
                "maximum": self.count,
            },
            "destination": "battlefield",
            "shuffle_after": True,
        }
        if self.enters_tapped:
            effect["enters_tapped_override"] = True
        return (
            "fixed-library-search-to-battlefield-v1",
            (effect,),
            None,
            (FIXED_LIBRARY_SEARCH_MECHANIC_ID,),
        )


def fixed_library_search_effect_template(
    text: str,
) -> FixedLibrarySearchTemplate | None:
    """Lower one fixed restrictive library search directly to the battlefield."""

    match = _FIXED_SEARCH.fullmatch(" ".join(text.strip().split()))
    if match is None:
        return None
    count = fixed_number(match.group("count"))
    if not 1 <= count <= 10:
        return None
    singular = count == 1
    if singular != (match.group("pronoun").casefold() == "it"):
        return None
    if singular == bool(match.group("plural")):
        return None
    query = _search_query(match.group("quality"))
    if query is None:
        return None
    enters_tapped = bool(match.group("tapped"))
    if count > 1 and not (
        enters_tapped
        and query.types_all == ("land",)
        and not query.types_any
    ):
        # Multiple battlefield entrants need one simultaneous transaction.
        # This closed production admits only the uniform tapped-land shape;
        # untapped and nonland groups can require independent entry choices.
        return None
    return FixedLibrarySearchTemplate(
        count=count,
        optional_count=bool(match.group("up_to")),
        query=query,
        enters_tapped=enters_tapped,
    )


__all__ = [
    "FIXED_LIBRARY_SEARCH_CAPABILITY_ID",
    "FIXED_LIBRARY_SEARCH_MECHANIC_ID",
    "FixedLibrarySearchTemplate",
    "fixed_library_search_effect_template",
]
