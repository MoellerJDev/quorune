from __future__ import annotations

"""Pure read-only queries over the authoritative current-turn journal."""

from collections.abc import Iterable

from .model import TurnHistory, TurnHistoryEvent, TurnHistoryEventKind


def current_turn_history_events(
    history: TurnHistory | None,
    *,
    turn_sequence: int,
    kind: TurnHistoryEventKind,
) -> tuple[TurnHistoryEvent, ...]:
    if (
        history is None
        or history.schema_version != 1
        or history.turn_sequence != turn_sequence
    ):
        return ()
    return tuple(event for event in history.events if event.kind == kind)


def opponent_was_dealt_damage_this_turn(
    history: TurnHistory | None,
    *,
    turn_sequence: int,
    player: str,
    active_players: Iterable[str],
) -> bool:
    """Return the immutable CR 702.54a look-back fact for ``player``."""

    opponents = frozenset(active_players) - {player}
    return any(
        event.target in opponents and event.amount > 0
        for event in current_turn_history_events(
            history,
            turn_sequence=turn_sequence,
            kind="player_damaged",
        )
    )


__all__ = [
    "current_turn_history_events",
    "opponent_was_dealt_damage_this_turn",
]
