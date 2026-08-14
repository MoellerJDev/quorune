from __future__ import annotations

import re
from typing import Sequence


_BLOODTHIRST_MECHANIC = "bloodthirst"
_RENOWN_MECHANIC = "renown"
_MODULAR_MECHANIC = "modular"

_KEYWORD_WITH_VALUE = re.compile(
    rf"^(?P<name>{re.escape(_BLOODTHIRST_MECHANIC)}|{re.escape(_RENOWN_MECHANIC)}|{re.escape(_MODULAR_MECHANIC)}|ward|equip|enchant|bushido|cycling|crew|dredge|kicker|toxic|"
    r"cumulative upkeep|echo|evolve|fabricate|persist|undying|riot|sunburst|unleash|prowess|convoke|affinity|morph|bestow|evoke|unearth)"
    r"(?:\s+(?P<value>.+))?$",
    re.IGNORECASE,
)
_KNOWN_BARE_KEYWORDS = frozenset(
    "deathtouch|defender|double strike|first strike|flash|flying|haste|"
    "flanking|hexproof|indestructible|infect|lifelink|menace|reach|shadow|shroud|"
    "trample|vigilance|wither".split("|")
)


def keyword_mechanics(
    text: str,
    card_keywords: Sequence[str],
) -> tuple[str, ...] | None:
    """Recognize a complete Oracle line made only of printed keywords."""

    parts = [part.strip() for part in text.rstrip(".").split(",")]
    if not parts:
        return None
    known = {keyword.casefold() for keyword in card_keywords}
    mechanics: list[str] = []
    for part in parts:
        lower = part.casefold()
        if lower == "proliferate":
            # Proliferate is a keyword action whose imperative instruction
            # executes during resolution, not a keyword ability carried by
            # the source. Let the closed resolution grammar own it.
            return None
        if re.fullmatch(r"support\s+.+", lower):
            # Support is a keyword action whose target set depends on whether
            # the instruction's source is a permanent or an instant/sorcery.
            # Let the source-context-aware resolution grammar own it.
            return None
        if re.fullmatch(r"bolster\s+.+", lower):
            # Bolster is a resolution-time keyword action whose eligible
            # creature set depends on current effective toughness.
            return None
        if re.fullmatch(r"amass\s+.+", lower):
            # Amass is a staged resolution-time keyword action. The closed
            # effect grammar owns its subtype and amount.
            return None
        if lower in _KNOWN_BARE_KEYWORDS or lower in known:
            mechanics.append(lower)
            continue
        match = _KEYWORD_WITH_VALUE.fullmatch(part)
        if match and match.group("name").casefold() in known:
            mechanics.append(match.group("name").casefold())
            continue
        if lower.startswith("protection from ") and "protection" in known:
            mechanics.append("protection")
            continue
        return None
    return tuple(mechanics)
