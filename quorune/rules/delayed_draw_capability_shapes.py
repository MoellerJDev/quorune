from __future__ import annotations

"""Capability shape for one fixed next-turn upkeep draw payload."""

from typing import Iterable, Mapping, Sequence

from ..compiler.delayed_draw_templates import (
    FIXED_NEXT_TURN_DRAW_CAPABILITY,
    FIXED_NEXT_TURN_DRAW_MECHANIC,
    fixed_next_turn_upkeep_draw_effect,
)


def fixed_next_turn_draw_node_capabilities(
    *,
    effects: Sequence[Mapping[str, object]],
    target_schema: Mapping[str, object] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Return trust dependencies only for the canonical delayed draw shape."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if (
        FIXED_NEXT_TURN_DRAW_MECHANIC not in mechanics
        or target_schema is not None
        or tuple(effects) != (fixed_next_turn_upkeep_draw_effect(),)
    ):
        return ()
    return (
        FIXED_NEXT_TURN_DRAW_CAPABILITY,
        "trigger.placement.apnap",
        "zone.draw.library_to_hand",
    )


__all__ = ["fixed_next_turn_draw_node_capabilities"]
