from __future__ import annotations

"""Closed Oracle grammar for casting and activation runtime metadata."""

import re
from typing import Any, Mapping

from ..creature_subtypes import canonical_creature_subtype
from ..semantic_runtime.casting_activation_metadata import (
    LOYALTY_COST_MODIFIER_EVENT,
    LOYALTY_COST_MODIFIER_HANDLER_ID,
    SELF_ZONE_CAST_PERMISSION_EVENT,
    SELF_ZONE_CAST_PERMISSION_HANDLER_ID,
)


CastingActivationMetadataTemplate = tuple[str, Mapping[str, Any], str]


_SELF_GRAVEYARD_CONTROLLED_SUBTYPE = re.compile(
    r"^You may cast this card from your graveyard as long as you control "
    r"(?:a|an) (?P<subtype>[A-Za-z][A-Za-z' -]*)\.?$",
    re.IGNORECASE,
)
_OPPONENT_PLANESWALKER_LOYALTY_MANA_INCREASE = re.compile(
    r"^Loyalty abilities of planeswalkers your opponents control cost "
    r"\{(?P<amount>[1-9][0-9]*)\} more to activate\.?$",
    re.IGNORECASE,
)
_CONTROLLER_LOYALTY_INCREASE = re.compile(
    r"^Planeswalkers' loyalty abilities you activate cost an additional "
    r"\[\+(?P<amount>[1-9][0-9]*)\] to activate\.?$",
    re.IGNORECASE,
)


def static_self_zone_cast_permission_handler(
    text: str,
) -> CastingActivationMetadataTemplate | None:
    """Lower one self-graveyard permission with a pinned subtype condition."""

    match = _SELF_GRAVEYARD_CONTROLLED_SUBTYPE.fullmatch(text.strip())
    if match is None:
        return None
    subtype = canonical_creature_subtype(match.group("subtype"))
    if subtype is None:
        return None
    return (
        "self-graveyard-cast-controlled-subtype-v1",
        {
            "handler_id": SELF_ZONE_CAST_PERMISSION_HANDLER_ID,
            "schema_version": 1,
            "event": SELF_ZONE_CAST_PERMISSION_EVENT,
            "source_zone": "graveyard",
            "controlled_subtypes_any": [subtype],
        },
        "casting.zone.self_graveyard.controlled_subtype",
    )


def static_loyalty_cost_modifier_handler(
    text: str,
) -> CastingActivationMetadataTemplate | None:
    """Lower the two represented public loyalty-cost modifier sentences."""

    normalized = text.strip()
    match = _OPPONENT_PLANESWALKER_LOYALTY_MANA_INCREASE.fullmatch(normalized)
    if match is not None:
        affected_controller = "opponent"
        adjustment_kind = "generic_mana_increase"
    else:
        match = _CONTROLLER_LOYALTY_INCREASE.fullmatch(normalized)
        if match is None:
            return None
        affected_controller = "source_controller"
        adjustment_kind = "loyalty_increase"
    return (
        "loyalty-cost-modifier-marker-v1",
        {
            "handler_id": LOYALTY_COST_MODIFIER_HANDLER_ID,
            "schema_version": 1,
            "event": LOYALTY_COST_MODIFIER_EVENT,
            "affected_controller": affected_controller,
            "adjustment_kind": adjustment_kind,
            "amount": int(match.group("amount")),
        },
        "activation.loyalty_cost.modifier_detection",
    )


__all__ = [
    "CastingActivationMetadataTemplate",
    "static_loyalty_cost_modifier_handler",
    "static_self_zone_cast_permission_handler",
]
