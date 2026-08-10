from __future__ import annotations

"""Closed Oracle grammar for reusable spell additional costs."""

from dataclasses import dataclass
import re
from typing import Any, Mapping

from ..additional_cost_vocabulary import (
    DISCARD_ONE_COST,
    EXILE_ONE_FROM_BATTLEFIELD_COST,
    EXILE_ONE_FROM_GRAVEYARD_COST,
    FIXED_ZONE_CHANGE_COST_CONTRACTS,
    RETURN_ONE_TO_OWNER_HAND_COST,
    SACRIFICE_COST_KIND,
    SACRIFICE_ONE_COST,
    ZONE_CHANGE_COST_KIND,
)
from ..object_predicate import ObjectQuerySpec
from .creature_subtypes import canonical_creature_subtype
from .fixed_numbers import FIXED_COUNT_PATTERN, fixed_number


_COUNTER_NAME = (
    r"[+-]\d+/[+-]\d+|"
    r"[A-Za-z][A-Za-z'-]*(?: [A-Za-z][A-Za-z'-]*){0,2}"
)
_FIXED_COUNTER_COST = re.compile(
    rf"As an additional cost to cast this spell, put "
    rf"(?P<count>{FIXED_COUNT_PATTERN}) (?P<counter>{_COUNTER_NAME}) "
    r"(?P<plural>counter|counters) on a creature you control\.?",
    re.IGNORECASE,
)
_PERMANENT_TYPE_PATTERN = (
    r"artifact|battle|creature|enchantment|land|planeswalker"
)
_FIXED_SACRIFICE_COST = re.compile(
    rf"As an additional cost to cast this spell, sacrifice "
    rf"(?P<article>a|an) "
    rf"(?P<first>{_PERMANENT_TYPE_PATTERN}|permanent)"
    rf"(?: or (?P<second>{_PERMANENT_TYPE_PATTERN}))?\.?",
    re.IGNORECASE,
)
_QUALIFIED_SACRIFICE_COST = re.compile(
    r"As an additional cost to cast this spell, sacrifice "
    r"(?P<article>a|an) (?P<quality>[A-Za-z][A-Za-z -]*)\.?",
    re.IGNORECASE,
)
_FIXED_DISCARD_COST = re.compile(
    r"As an additional cost to cast this spell, discard "
    r"(?P<article>a|an) (?:(?P<quality>[A-Za-z]+(?: or [A-Za-z]+)?) )?card\.?",
    re.IGNORECASE,
)
_FIXED_GRAVEYARD_EXILE_COST = re.compile(
    r"As an additional cost to cast this spell, exile "
    r"(?P<article>a|an) (?P<quality>[A-Za-z]+(?: or [A-Za-z]+)?) card "
    r"from your graveyard\.?",
    re.IGNORECASE,
)
_FIXED_BATTLEFIELD_EXILE_COST = re.compile(
    r"As an additional cost to cast this spell, exile "
    r"(?P<article>a|an) (?P<quality>[A-Za-z ]+) you control\.?",
    re.IGNORECASE,
)
_FIXED_RETURN_COST = re.compile(
    r"As an additional cost to cast this spell, return "
    r"(?P<article>a|an) (?P<quality>[A-Za-z ]+) you control "
    r"to its owner's hand\.?",
    re.IGNORECASE,
)
_COLOR_WORDS = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
    "colorless": "C",
}


def _creature_you_control_query() -> ObjectQuerySpec:
    return ObjectQuerySpec(
        zones=("battlefield",),
        controller="$actor",
        types_all=("creature",),
        known_to_actor=True,
    )


def _permanent_you_control_query(
    types_any: tuple[str, ...],
) -> ObjectQuerySpec:
    return ObjectQuerySpec(
        zones=("battlefield",),
        controller="$actor",
        types_any=types_any,
        known_to_actor=True,
    )


@dataclass(frozen=True, slots=True)
class FixedCounterAdditionalCostTemplate:
    """One mandatory fixed counter placement paid while casting a spell."""

    amount: int
    counter_name: str

    def __post_init__(self) -> None:
        normalized = " ".join(self.counter_name.casefold().split())
        if type(self.amount) is not int or self.amount <= 0:
            raise ValueError("Counter additional-cost amount must be positive")
        if not normalized or re.fullmatch(_COUNTER_NAME, normalized) is None:
            raise ValueError("Counter additional-cost name is unsupported")
        object.__setattr__(self, "counter_name", normalized)

    @property
    def template_id(self) -> str:
        return "spell-additional-cost-fixed-counter-creature-you-control-v1"

    @property
    def descriptor(self) -> Mapping[str, Any]:
        return {
            "schema_version": 1,
            "kind": "counter_placement",
            "counter": self.counter_name,
            "amount": self.amount,
            "choice_field": "counter_cost_card",
            "predicate": _creature_you_control_query().to_dict(),
        }

    @property
    def cost_schema(self) -> Mapping[str, Any]:
        return {"additional_costs": [dict(self.descriptor)]}


@dataclass(frozen=True, slots=True)
class FixedSacrificeAdditionalCostTemplate:
    """One mandatory sacrifice of a controlled permanent while casting."""

    permanent_types: tuple[str, ...]

    def __post_init__(self) -> None:
        normalized = tuple(
            sorted(str(value).casefold() for value in self.permanent_types)
        )
        allowed = {
            "artifact",
            "battle",
            "creature",
            "enchantment",
            "land",
            "planeswalker",
        }
        if (
            len(normalized) > 2
            or len(normalized) != len(set(normalized))
            or not set(normalized).issubset(allowed)
        ):
            raise ValueError(
                "Sacrifice additional-cost types are outside the closed family"
            )
        object.__setattr__(self, "permanent_types", normalized)

    @property
    def template_id(self) -> str:
        suffix = "permanent" if not self.permanent_types else "-or-".join(
            self.permanent_types
        )
        return f"spell-additional-cost-fixed-sacrifice-{suffix}-v1"

    @property
    def descriptor(self) -> Mapping[str, Any]:
        return {
            "schema_version": 1,
            "kind": SACRIFICE_COST_KIND,
            "count": 1,
            "choice_field": "sacrifice_cards",
            "predicate": _permanent_you_control_query(
                self.permanent_types
            ).to_dict(),
        }

    @property
    def cost_schema(self) -> Mapping[str, Any]:
        return {"additional_costs": [dict(self.descriptor)]}


@dataclass(frozen=True, slots=True)
class FixedZoneChangeAdditionalCostTemplate:
    """One mandatory single-object zone change paid while casting."""

    operation: str
    predicate: ObjectQuerySpec

    def __post_init__(self) -> None:
        if self.operation not in FIXED_ZONE_CHANGE_COST_CONTRACTS:
            raise ValueError("Zone-change additional-cost operation is unsupported")
        origin, _, _ = FIXED_ZONE_CHANGE_COST_CONTRACTS[self.operation]
        if self.predicate.zones != (origin,):
            raise ValueError("Zone-change additional-cost origin is noncanonical")

    @property
    def template_id(self) -> str:
        terms: list[str] = [self.operation.replace("_one", "")]
        for field_name in (
            "types_all",
            "types_any",
            "excluded_types",
            "subtypes_all",
            "supertypes_all",
            "colors_all",
            "colors_any",
        ):
            values = getattr(self.predicate, field_name)
            if values:
                terms.append(field_name.replace("_", "-"))
                terms.extend(str(value).casefold() for value in values)
        if len(terms) == 1:
            terms.append("card")
        return "spell-additional-cost-fixed-" + "-".join(terms) + "-v1"

    @property
    def descriptor(self) -> Mapping[str, Any]:
        _, _, choice_field = FIXED_ZONE_CHANGE_COST_CONTRACTS[self.operation]
        return {
            "schema_version": 1,
            "kind": ZONE_CHANGE_COST_KIND,
            "operation": self.operation,
            "count": 1,
            "choice_field": choice_field,
            "predicate": self.predicate.to_dict(),
        }

    @property
    def cost_schema(self) -> Mapping[str, Any]:
        return {"additional_costs": [dict(self.descriptor)]}


def _article_matches(article: str, noun: str) -> bool:
    expected = "an" if noun[0].casefold() in "aeiou" else "a"
    return article.casefold() == expected


def _owned_zone_query(
    zone: str,
    *,
    types_all: tuple[str, ...] = (),
    types_any: tuple[str, ...] = (),
    colors_any: tuple[str, ...] = (),
) -> ObjectQuerySpec:
    return ObjectQuerySpec(
        zones=(zone,),
        owner="$actor",
        types_all=types_all,
        types_any=types_any,
        colors_any=colors_any,
        known_to_actor=True,
    )


def _controlled_permanent_query(
    *,
    types_all: tuple[str, ...] = (),
    types_any: tuple[str, ...] = (),
    excluded_types: tuple[str, ...] = (),
    subtypes_all: tuple[str, ...] = (),
    supertypes_all: tuple[str, ...] = (),
    colors_all: tuple[str, ...] = (),
) -> ObjectQuerySpec:
    return ObjectQuerySpec(
        zones=("battlefield",),
        controller="$actor",
        types_all=types_all,
        types_any=types_any,
        excluded_types=excluded_types,
        subtypes_all=subtypes_all,
        supertypes_all=supertypes_all,
        colors_all=colors_all,
        known_to_actor=True,
    )


def _qualified_sacrifice_query(quality: str) -> ObjectQuerySpec | None:
    normalized = " ".join(quality.casefold().split())
    if normalized == "nonland permanent":
        return _controlled_permanent_query(excluded_types=("land",))
    if normalized == "legendary creature":
        return _controlled_permanent_query(
            types_all=("creature",), supertypes_all=("legendary",)
        )
    words = normalized.split()
    if len(words) == 2 and words[0] in _COLOR_WORDS and words[1] in {
        "creature",
        "permanent",
    }:
        return _controlled_permanent_query(
            types_all=(() if words[1] == "permanent" else (words[1],)),
            colors_all=(_COLOR_WORDS[words[0]],),
        )
    subtype = canonical_creature_subtype(normalized)
    if subtype is not None:
        return _controlled_permanent_query(subtypes_all=(subtype,))
    return None


def fixed_zone_change_additional_cost_template(
    text: str,
) -> FixedZoneChangeAdditionalCostTemplate | None:
    """Parse the closed fixed single-object zone-change cost family."""

    stripped = text.strip()
    match = _FIXED_DISCARD_COST.fullmatch(stripped)
    if match is not None:
        raw_quality = match.group("quality")
        quality = raw_quality.casefold() if raw_quality else ""
        if not _article_matches(match.group("article"), quality or "card"):
            return None
        if not quality:
            predicate = _owned_zone_query("hand")
        elif quality in {"land", "creature"}:
            predicate = _owned_zone_query("hand", types_all=(quality,))
        else:
            colors = tuple(
                _COLOR_WORDS.get(value)
                for value in quality.split(" or ")
            )
            if any(value is None for value in colors):
                return None
            predicate = _owned_zone_query(
                "hand", colors_any=tuple(str(value) for value in colors)
            )
        return FixedZoneChangeAdditionalCostTemplate(
            DISCARD_ONE_COST, predicate
        )

    match = _FIXED_GRAVEYARD_EXILE_COST.fullmatch(stripped)
    if match is not None:
        quality = match.group("quality").casefold()
        if not _article_matches(match.group("article"), quality):
            return None
        card_types = tuple(quality.split(" or "))
        if not set(card_types).issubset({"creature", "instant", "sorcery"}):
            return None
        predicate = _owned_zone_query(
            "graveyard",
            types_all=card_types if len(card_types) == 1 else (),
            types_any=card_types if len(card_types) > 1 else (),
        )
        return FixedZoneChangeAdditionalCostTemplate(
            EXILE_ONE_FROM_GRAVEYARD_COST, predicate
        )

    match = _FIXED_BATTLEFIELD_EXILE_COST.fullmatch(stripped)
    if match is not None:
        quality = " ".join(match.group("quality").casefold().split())
        if not _article_matches(match.group("article"), quality):
            return None
        if quality not in {"artifact", "creature", "permanent"}:
            return None
        predicate = _controlled_permanent_query(
            types_all=(() if quality == "permanent" else (quality,))
        )
        return FixedZoneChangeAdditionalCostTemplate(
            EXILE_ONE_FROM_BATTLEFIELD_COST, predicate
        )

    match = _FIXED_RETURN_COST.fullmatch(stripped)
    if match is not None:
        quality = " ".join(match.group("quality").casefold().split())
        if not _article_matches(match.group("article"), quality):
            return None
        if quality not in {"land", "creature", "permanent"}:
            return None
        predicate = _controlled_permanent_query(
            types_all=(() if quality == "permanent" else (quality,))
        )
        return FixedZoneChangeAdditionalCostTemplate(
            RETURN_ONE_TO_OWNER_HAND_COST, predicate
        )

    match = _QUALIFIED_SACRIFICE_COST.fullmatch(stripped)
    if match is None:
        return None
    quality = " ".join(match.group("quality").casefold().split())
    if not _article_matches(match.group("article"), quality):
        return None
    predicate = _qualified_sacrifice_query(quality)
    if predicate is None:
        return None
    return FixedZoneChangeAdditionalCostTemplate(
        SACRIFICE_ONE_COST, predicate
    )


def fixed_counter_additional_cost_template(
    text: str,
) -> FixedCounterAdditionalCostTemplate | None:
    """Parse one exact mandatory creature-counter casting cost."""

    match = _FIXED_COUNTER_COST.fullmatch(text.strip())
    if match is None:
        return None
    amount = fixed_number(match.group("count"))
    if amount <= 0 or (match.group("plural").casefold() == "counter") != (
        amount == 1
    ):
        return None
    return FixedCounterAdditionalCostTemplate(
        amount=amount,
        counter_name=match.group("counter"),
    )


def fixed_sacrifice_additional_cost_template(
    text: str,
) -> FixedSacrificeAdditionalCostTemplate | None:
    """Parse one exact fixed sacrifice casting cost with closed type nouns."""

    match = _FIXED_SACRIFICE_COST.fullmatch(text.strip())
    if match is None:
        return None
    first = match.group("first").casefold()
    article = match.group("article").casefold()
    expected_article = "an" if first[0] in "aeiou" else "a"
    if article != expected_article:
        return None
    second = match.group("second")
    if first == "permanent":
        if second is not None:
            return None
        types: tuple[str, ...] = ()
    else:
        types = (first,) if second is None else (first, second.casefold())
    return FixedSacrificeAdditionalCostTemplate(types)


__all__ = [
    "FixedCounterAdditionalCostTemplate",
    "FixedSacrificeAdditionalCostTemplate",
    "FixedZoneChangeAdditionalCostTemplate",
    "fixed_counter_additional_cost_template",
    "fixed_sacrifice_additional_cost_template",
    "fixed_zone_change_additional_cost_template",
]
