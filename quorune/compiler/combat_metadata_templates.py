from __future__ import annotations

"""Closed Oracle grammar for bounded combat runtime metadata."""

import re
from typing import Any, Mapping

from ..semantic_runtime.combat_metadata import (
    GOAD_PROHIBITION_EVENT,
    GOAD_PROHIBITION_HANDLER_ID,
)


CombatMetadataTemplate = tuple[str, Mapping[str, Any], str]


_CONTROLLER_CREATURE_GOAD_PROHIBITION = re.compile(
    r"^Creatures you control can't be goaded\.?$",
    re.IGNORECASE,
)


def static_goad_prohibition_handler(
    text: str,
) -> CombatMetadataTemplate | None:
    """Lower the exact controller-creature goad prohibition."""

    if _CONTROLLER_CREATURE_GOAD_PROHIBITION.fullmatch(text.strip()) is None:
        return None
    return (
        "controller-creature-goad-prohibition-v1",
        {
            "handler_id": GOAD_PROHIBITION_HANDLER_ID,
            "schema_version": 1,
            "event": GOAD_PROHIBITION_EVENT,
            "affected_controller": "source_controller",
            "affected_card_type": "creature",
        },
        "combat.goad.prohibition.controller_creatures",
    )


__all__ = [
    "CombatMetadataTemplate",
    "static_goad_prohibition_handler",
]
