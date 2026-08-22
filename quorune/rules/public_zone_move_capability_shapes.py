from __future__ import annotations

"""Capability closure for fixed public-origin zone-move effects."""

from typing import Any, Iterable, Mapping, Sequence

from ..public_zone_moves import (
    PublicZoneMoveError,
    PublicZoneMoveSetSpec,
    PublicZoneSeatRelation,
)
from .graveyard_card_targets import (
    GraveyardCardTargetError,
    PublicGraveyardCardTargetSpec,
)


_PLAYER_TARGETS = (
    {
        "zones": ["player"],
        "categories": ["player"],
        "count": 1,
        "player_relation": "any",
    },
    {
        "zones": ["player"],
        "categories": ["player"],
        "count": 1,
        "player_relation": "opponent",
    },
)


def public_graveyard_card_exile_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    mechanics = {str(value).casefold() for value in mechanic_ids}
    if not {
        "exile",
        "fixed-public-zone-move",
        "cr-115-targets",
    }.issubset(mechanics):
        return ()
    if len(effects) != 1 or target_schema is None:
        return ()
    try:
        PublicGraveyardCardTargetSpec.from_target_schema(target_schema)
    except (GraveyardCardTargetError, TypeError):
        return ()
    effect = effects[0]
    if (
        set(effect) != {"op", "card"}
        or effect.get("op") != "exile_public_graveyard_card"
        or effect.get("card") != "$target.0"
    ):
        return ()
    return (
        "card.exile.public_graveyard",
        "target.revalidate_resolution",
    )


def fixed_public_zone_move_set_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    mechanics = {str(value).casefold() for value in mechanic_ids}
    if not {
        "fixed-public-zone-move",
        "fixed-public-zone-move-set",
    }.issubset(mechanics) or len(effects) != 1:
        return ()
    effect = effects[0]
    if (
        set(effect) != {"op", "source", "set"}
        or effect.get("op") != "move_public_zone_set"
        or effect.get("source") != "$source"
    ):
        return ()
    try:
        spec = PublicZoneMoveSetSpec.from_dict(effect["set"])
    except (KeyError, TypeError, PublicZoneMoveError):
        return ()
    targeted = spec.seat_relation is PublicZoneSeatRelation.TARGET_PLAYER
    if targeted:
        if (
            "cr-115-targets" not in mechanics
            or dict(target_schema or {}) not in _PLAYER_TARGETS
            or spec.target_seat != "$target.0"
        ):
            return ()
        return (
            "zone.move.fixed_public_set",
            "target.revalidate_resolution",
        )
    if target_schema is not None or "cr-115-targets" in mechanics:
        return ()
    return ("zone.move.fixed_public_set",)


__all__ = [
    "fixed_public_zone_move_set_node_capabilities",
    "public_graveyard_card_exile_node_capabilities",
]
