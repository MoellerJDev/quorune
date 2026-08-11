from __future__ import annotations

from dataclasses import dataclass

from .creature_subtypes import canonical_creature_subtype


AMASS_MECHANIC_ID = "keyword_action.amass.fixed"
AMASS_COUNTER_NAME = "+1/+1"

_PLURAL_ES_FINALS = frozenset("sxz")


class AmassError(ValueError):
    """Raised when a typed Amass descriptor is outside the closed family."""


def canonical_amass_subtype(value: str) -> str | None:
    """Resolve a pinned subtype from its singular or closed plural surface."""

    if type(value) is not str:
        return None
    normalized = " ".join(value.casefold().split())
    candidates = [normalized]
    if normalized.endswith("ies"):
        candidates.append(f"{normalized[:-3]}y")
    if normalized.endswith("ves"):
        candidates.extend((f"{normalized[:-3]}f", f"{normalized[:-3]}fe"))
    if normalized.endswith("s"):
        candidates.append(normalized[:-1])
    matches = {
        subtype
        for candidate in candidates
        if (subtype := canonical_creature_subtype(candidate)) is not None
    }
    if len(matches) != 1:
        return None
    return next(iter(matches))


def plural_amass_subtype(value: str) -> str:
    """Return the ordinary plural label used by Amass rules text."""

    subtype = canonical_amass_subtype(value)
    if subtype is None:
        raise AmassError("Amass requires one pinned creature subtype")
    if subtype.endswith("y") and len(subtype) > 1 and subtype[-2] not in "aeiou":
        return f"{subtype[:-1].title()}ies"
    if subtype.endswith("fe"):
        return f"{subtype[:-2].title()}ves"
    if subtype.endswith("f"):
        return f"{subtype[:-1].title()}ves"
    if subtype[-1] in _PLURAL_ES_FINALS or subtype.endswith(("ch", "sh")):
        return f"{subtype.title()}es"
    return f"{subtype.title()}s"


@dataclass(frozen=True, slots=True)
class FixedAmassSpec:
    """One fixed positive CR 701.47 Amass instruction."""

    subtype: str
    amount: int

    def __post_init__(self) -> None:
        subtype = canonical_amass_subtype(self.subtype)
        if subtype is None:
            raise AmassError("Amass requires one pinned creature subtype")
        if type(self.amount) is not int or self.amount <= 0:
            raise AmassError(
                "Amass amount must be an exact positive integer"
            )
        object.__setattr__(self, "subtype", subtype.title())


__all__ = [
    "AMASS_COUNTER_NAME",
    "AMASS_MECHANIC_ID",
    "AmassError",
    "FixedAmassSpec",
    "canonical_amass_subtype",
    "plural_amass_subtype",
]
