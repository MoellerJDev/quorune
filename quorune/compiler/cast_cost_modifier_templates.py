from __future__ import annotations

"""Closed Oracle grammar for fixed controller spell-cost reductions."""

import re
from typing import Any, Mapping

from ..creature_subtypes import canonical_creature_subtype
from ..object_predicate import ObjectQueryError, ObjectQuerySpec
from ..semantic_runtime.cast_costs import (
    FIXED_SPELL_COST_REDUCTION_CAPABILITY_ID,
    FIXED_SPELL_COST_REDUCTION_EVENT,
    FIXED_SPELL_COST_REDUCTION_HANDLER_ID,
)


CastCostModifierTemplate = tuple[
    str,
    Mapping[str, Any],
    str,
]


_FIXED_GENERIC_SPELL_REDUCTION = re.compile(
    r"^(?P<subject>.+?) cost(?:s)? "
    r"\{(?P<amount>[1-9][0-9]*)\} less to cast\.?$",
    re.IGNORECASE,
)
_CARD_TYPES = frozenset(
    {
        "artifact",
        "battle",
        "creature",
        "enchantment",
        "instant",
        "land",
        "planeswalker",
        "sorcery",
    }
)
_COLORS = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
}
_SUPERTYPES = frozenset({"legendary", "snow"})
_NONCREATURE_SUBTYPES = frozenset(
    {"arcane", "aura", "equipment", "lesson", "saga", "vehicle"}
)


def _single_spell_quality(
    text: str,
) -> tuple[str, dict[str, Any]] | None:
    words = text.casefold().split()
    if len(words) == 1:
        word = words[0]
        if word in _CARD_TYPES:
            return "type", {"types_all": (word,)}
        if word in _COLORS:
            return "color", {"colors_all": (_COLORS[word],)}
        if word == "colorless":
            return "colorless", {"colorless": True}
        if word in _SUPERTYPES:
            return "supertype", {"supertypes_all": (word,)}
        if word == "noncreature":
            return "excluded_type", {"excluded_types": ("creature",)}
        subtype = (
            word
            if word in _NONCREATURE_SUBTYPES
            else canonical_creature_subtype(word)
        )
        if subtype is not None:
            return "subtype", {"subtypes_all": (subtype,)}
        return None
    if len(words) != 2:
        return None
    qualifier, subject = words
    if subject in _CARD_TYPES:
        if qualifier in _COLORS:
            return "conjunction", {
                "types_all": (subject,),
                "colors_all": (_COLORS[qualifier],),
            }
        if qualifier == "colorless":
            return "conjunction", {
                "types_all": (subject,),
                "colorless": True,
            }
        if qualifier in _SUPERTYPES:
            return "conjunction", {
                "types_all": (subject,),
                "supertypes_all": (qualifier,),
            }
        return None
    subtype = canonical_creature_subtype(subject)
    if subtype is None or qualifier not in {*_COLORS, "colorless"}:
        return None
    fields: dict[str, Any] = {"subtypes_all": (subtype,)}
    if qualifier == "colorless":
        fields["colorless"] = True
    else:
        fields["colors_all"] = (_COLORS[qualifier],)
    return "conjunction", fields


def _fixed_spell_predicate(subject: str) -> ObjectQuerySpec | None:
    normalized = subject.strip()
    if normalized.casefold() == "spells you cast":
        return ObjectQuerySpec()
    suffix = " spells you cast"
    if not normalized.casefold().endswith(suffix):
        return None
    qualities = normalized[: -len(suffix)].strip()
    # Oracle repeats "spells" in lists such as "White spells and black
    # spells". It is only a grammatical carrier inside this closed subject.
    qualities = re.sub(r"\bspells\b", "", qualities, flags=re.IGNORECASE)
    parts = tuple(
        part.strip()
        for part in re.split(
            r"\s*(?:,|\band\b)\s*",
            qualities,
            flags=re.IGNORECASE,
        )
        if part.strip()
    )
    parsed = tuple(_single_spell_quality(part) for part in parts)
    if not parsed or any(value is None for value in parsed):
        return None
    typed = tuple(value for value in parsed if value is not None)
    if len(typed) == 1:
        return ObjectQuerySpec(**typed[0][1])
    kinds = {kind for kind, _fields in typed}
    if len(kinds) != 1:
        return None
    kind = next(iter(kinds))
    values = tuple(
        next(iter(fields.values()))[0]
        for _kind, fields in typed
    )
    if kind == "type":
        return ObjectQuerySpec(types_any=values)
    if kind == "color":
        return ObjectQuerySpec(colors_any=values)
    if kind == "subtype":
        return ObjectQuerySpec(subtypes_any=values)
    return None


def static_fixed_spell_cost_reduction_handler(
    text: str,
) -> CastCostModifierTemplate | None:
    """Lower one unconditional generic reduction over a fixed spell set."""

    match = _FIXED_GENERIC_SPELL_REDUCTION.fullmatch(text.strip())
    if match is None:
        return None
    try:
        predicate = _fixed_spell_predicate(match.group("subject"))
    except ObjectQueryError:
        return None
    if predicate is None:
        return None
    return (
        "fixed-query-spell-cost-reduction-v1",
        {
            "handler_id": FIXED_SPELL_COST_REDUCTION_HANDLER_ID,
            "schema_version": 1,
            "event": FIXED_SPELL_COST_REDUCTION_EVENT,
            "affected_controller": "source_controller",
            "predicate": predicate.to_dict(),
            "generic_reduction": int(match.group("amount")),
        },
        FIXED_SPELL_COST_REDUCTION_CAPABILITY_ID,
    )


__all__ = [
    "CastCostModifierTemplate",
    "static_fixed_spell_cost_reduction_handler",
]
