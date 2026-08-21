from __future__ import annotations

import re

from ..characteristic_evaluation import type_parts
from .model import (
    AuraControllerRelation,
    AuraRuleError,
    EnchantSpec,
    SimpleEnchantSpec,
)


_REMINDER = re.compile(r"\s*\([^()]*\)\s*$")
_ENCHANT = re.compile(
    r"^enchant (?P<restriction>.+?)\.?$",
    re.IGNORECASE,
)


def is_aura_type_line(type_line: str) -> bool:
    return "aura" in type_parts(str(type_line))[1]


def is_enchant_keyword_line(line: str) -> bool:
    """Recognize one complete Enchant keyword line without trusting its predicate."""

    return _ENCHANT.fullmatch(_material_line(line)) is not None


def _material_line(value: str) -> str:
    line = value.strip()
    while True:
        reduced = _REMINDER.sub("", line).strip()
        if reduced == line:
            return reduced
        line = reduced


def enchant_restriction_text(line: str) -> str | None:
    """Return one normalized complete Enchant restriction, if present."""

    match = _ENCHANT.fullmatch(_material_line(line))
    if match is None:
        return None
    return " ".join(match.group("restriction").casefold().split())


def parse_simple_enchant_line(line: str) -> SimpleEnchantSpec | None:
    """Parse one bounded battlefield-object Enchant keyword line.

    The grammar deliberately rejects players, cards in other zones, object
    qualities, subtype alternatives, conjunctions, and multiple restrictions.
    Those families need additional legality predicates before they can be
    advertised as executable.
    """

    restriction = enchant_restriction_text(line)
    if restriction is None:
        return None
    relation = AuraControllerRelation.ANY
    for suffix, candidate in (
        (" an opponent controls", AuraControllerRelation.OPPONENT),
        (" opponent controls", AuraControllerRelation.OPPONENT),
        (" you control", AuraControllerRelation.YOU),
    ):
        if restriction.endswith(suffix):
            restriction = restriction[: -len(suffix)].strip()
            relation = candidate
            break
    try:
        return SimpleEnchantSpec(
            object_kind=restriction,
            controller_relation=relation,
        )
    except AuraRuleError:
        return None


def parse_enchant_line(line: str) -> EnchantSpec | None:
    """Parse one complete restriction through the canonical Aura grammars."""

    simple = parse_simple_enchant_line(line)
    if simple is not None:
        return simple
    from .typed_grammar import parse_typed_enchant_line

    return parse_typed_enchant_line(line)


def simple_enchant_spec_from_oracle(
    oracle_text: str,
) -> SimpleEnchantSpec | None:
    lines = [
        line.strip()
        for line in str(oracle_text).splitlines()
        if line.strip().casefold().startswith("enchant ")
    ]
    if len(lines) != 1:
        return None
    return parse_simple_enchant_line(lines[0])


def enchant_spec_from_oracle(oracle_text: str) -> EnchantSpec | None:
    lines = [
        line.strip()
        for line in str(oracle_text).splitlines()
        if line.strip().casefold().startswith("enchant ")
    ]
    if len(lines) != 1:
        return None
    return parse_enchant_line(lines[0])


__all__ = [
    "enchant_restriction_text",
    "enchant_spec_from_oracle",
    "is_enchant_keyword_line",
    "is_aura_type_line",
    "parse_enchant_line",
    "parse_simple_enchant_line",
    "simple_enchant_spec_from_oracle",
]
