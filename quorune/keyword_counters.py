from __future__ import annotations

"""Typed CR 122.1b keyword-counter characteristic projection."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any


class KeywordCounterError(ValueError):
    """A represented keyword-counter quantity is malformed."""


# CR 122.1b's closed ordinary keyword-counter vocabulary. Variants of these
# keywords require their own typed grammar and deliberately do not normalize
# through this table.
KEYWORD_COUNTER_MECHANICS: Mapping[str, str] = MappingProxyType(
    {
        "flying": "flying",
        "first strike": "first-strike",
        "double strike": "double-strike",
        "deathtouch": "deathtouch",
        "decayed": "decayed",
        "exalted": "exalted",
        "haste": "haste",
        "hexproof": "hexproof",
        "indestructible": "indestructible",
        "lifelink": "lifelink",
        "menace": "menace",
        "reach": "reach",
        "shadow": "shadow",
        "trample": "trample",
        "vigilance": "vigilance",
    }
)


def keyword_counter_mechanic(counter_name: object) -> str | None:
    """Return the exact mechanic dependency for one ordinary counter name."""

    if not isinstance(counter_name, str):
        return None
    normalized = " ".join(counter_name.casefold().split())
    return KEYWORD_COUNTER_MECHANICS.get(normalized)


def keyword_counter_abilities(counters: Mapping[str, Any]) -> tuple[str, ...]:
    """Return abilities granted by positive represented keyword counters."""

    if not isinstance(counters, Mapping):
        raise KeywordCounterError("Counters must be a mapping")
    abilities: list[str] = []
    for counter_name, mechanic_id in KEYWORD_COUNTER_MECHANICS.items():
        if counter_name not in counters:
            continue
        amount = counters[counter_name]
        if type(amount) is not int or amount < 0:
            raise KeywordCounterError(
                f"{counter_name} counter quantity must be a nonnegative integer"
            )
        if amount > 0:
            abilities.append(mechanic_id.replace("-", " ").title())
    return tuple(abilities)


__all__ = [
    "KEYWORD_COUNTER_MECHANICS",
    "KeywordCounterError",
    "keyword_counter_abilities",
    "keyword_counter_mechanic",
]
