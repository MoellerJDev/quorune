from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from ..compiler.surveil_templates import (
    SURVEIL_CAPABILITY_ID,
    SURVEIL_MECHANIC_ID,
)


def fixed_surveil_node_capabilities(
    *,
    effects: Sequence[Mapping[str, object]],
    target_schema: Mapping[str, object] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Recognize one mandatory fixed-count controller Surveil action."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if SURVEIL_MECHANIC_ID not in mechanics or len(effects) != 1:
        return ()
    effect = effects[0]
    if (
        target_schema is None
        and set(effect) == {"op", "player", "count"}
        and effect.get("op") == "surveil"
        and effect.get("player") == "$controller"
        and type(effect.get("count")) is int
        and int(effect["count"]) > 0
    ):
        return (SURVEIL_CAPABILITY_ID,)
    return ()


__all__ = ["fixed_surveil_node_capabilities"]
