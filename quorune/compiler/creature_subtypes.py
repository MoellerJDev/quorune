"""Compatibility import for the shared pinned creature-subtype registry."""

from ..creature_subtypes import (
    CREATURE_SUBTYPES,
    CREATURE_SUBTYPE_RULE_REFERENCE,
    CREATURE_SUBTYPE_SNAPSHOT,
    canonical_creature_subtype,
)

__all__ = [
    "CREATURE_SUBTYPES",
    "CREATURE_SUBTYPE_RULE_REFERENCE",
    "CREATURE_SUBTYPE_SNAPSHOT",
    "canonical_creature_subtype",
]
