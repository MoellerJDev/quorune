from __future__ import annotations

"""Typed ownership for control-acquisition and upkeep history."""

from typing import Any

from .model import CONTROL_HISTORY_VERSION


class ControlHistoryError(ValueError):
    """A serialized or proposed control-history value is malformed."""


def record_control_acquisition(
    permanent: Any,
    *,
    controller_turns_begun: int,
    timestamp: int,
    history_version: int | None,
) -> None:
    """Record when the current controller acquired one permanent.

    The turn count remains the canonical CR 302.6 input.  The independent
    timestamp supports rules such as Echo whose look-back boundary is an
    upkeep rather than the beginning of the current turn.
    """

    if type(controller_turns_begun) is not int or controller_turns_begun < 0:
        raise ControlHistoryError(
            "Controller turns-begun count must be a nonnegative integer"
        )
    if type(timestamp) is not int or timestamp < 0:
        raise ControlHistoryError(
            "Control-acquisition timestamp must be a nonnegative integer"
        )
    if history_version not in {None, CONTROL_HISTORY_VERSION}:
        raise ControlHistoryError("Unsupported control-history version")
    permanent.acquired_control_turn_count = controller_turns_begun
    if history_version is not None:
        permanent.acquired_control_timestamp = timestamp


def begin_upkeep_control_epoch(
    player: Any,
    *,
    timestamp: int,
    history_version: int | None,
) -> int:
    """Advance one player's public upkeep boundary and return its predecessor."""

    if type(timestamp) is not int or timestamp < 0:
        raise ControlHistoryError(
            "Upkeep timestamp must be a nonnegative integer"
        )
    if history_version not in {None, CONTROL_HISTORY_VERSION}:
        raise ControlHistoryError("Unsupported control-history version")
    if history_version is None:
        # Historical Game Record v3 journals predate upkeep-relative control
        # history. Replaying them must not introduce a new hashed state field.
        return 0
    previous = getattr(player, "last_upkeep_timestamp", None)
    if type(previous) is not int or previous < 0:
        raise ControlHistoryError(
            "Previous upkeep timestamp must be a nonnegative integer"
        )
    if previous > timestamp:
        raise ControlHistoryError(
            "Upkeep timestamp cannot move backwards"
        )
    player.last_upkeep_timestamp = timestamp
    return previous


__all__ = [
    "CONTROL_HISTORY_VERSION",
    "ControlHistoryError",
    "begin_upkeep_control_epoch",
    "record_control_acquisition",
]
