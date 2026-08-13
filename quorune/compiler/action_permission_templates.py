from __future__ import annotations

"""Closed Oracle grammar for controller-wide static action permissions."""

import re
from typing import Any, Mapping

from ..semantic_runtime.action_permissions import (
    ACTION_PERMISSION_EVENT,
    ACTIVATE_CONTROLLED_CREATURE_AS_HASTE_HANDLER_ID,
    LAND_PLAY_FROM_OWN_GRAVEYARD_HANDLER_ID,
    ActionPermissionKind,
)


ActionPermissionHandlerTemplate = tuple[str, Mapping[str, Any], str]


_PLAY_LANDS_FROM_GRAVEYARD = re.compile(
    r"^You may play lands from your graveyard\.?$",
    re.IGNORECASE,
)
_ACTIVATE_CREATURES_AS_HASTE = re.compile(
    r"^You may activate abilities of creatures you control as though those "
    r"creatures had haste\.?$",
    re.IGNORECASE,
)


def _descriptor(
    *,
    handler_id: str,
    permission: ActionPermissionKind,
) -> dict[str, Any]:
    return {
        "handler_id": handler_id,
        "schema_version": 1,
        "event": ACTION_PERMISSION_EVENT,
        "permission": permission.value,
    }


def static_action_permission_handler(
    text: str,
) -> ActionPermissionHandlerTemplate | None:
    """Lower only the two closed controller-wide permission sentences."""

    normalized = text.strip()
    if _PLAY_LANDS_FROM_GRAVEYARD.fullmatch(normalized) is not None:
        return (
            "land-play-from-own-graveyard-permission-v1",
            _descriptor(
                handler_id=LAND_PLAY_FROM_OWN_GRAVEYARD_HANDLER_ID,
                permission=ActionPermissionKind.LAND_PLAY_FROM_OWN_GRAVEYARD,
            ),
            "land.play.from_own_graveyard",
        )
    if _ACTIVATE_CREATURES_AS_HASTE.fullmatch(normalized) is not None:
        return (
            "activate-controlled-creature-as-haste-permission-v1",
            _descriptor(
                handler_id=ACTIVATE_CONTROLLED_CREATURE_AS_HASTE_HANDLER_ID,
                permission=(
                    ActionPermissionKind.ACTIVATE_CONTROLLED_CREATURE_AS_HASTE
                ),
            ),
            "activation.permission.controlled_creature_as_haste",
        )
    return None


__all__ = [
    "ActionPermissionHandlerTemplate",
    "static_action_permission_handler",
]
