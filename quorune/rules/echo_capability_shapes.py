from __future__ import annotations

"""Closed CardProgram capability shape for ordinary fixed-mana Echo."""

from typing import Any, Iterable, Mapping, Sequence

from ..echo import ECHO_CONTROL_CONDITION_FIELD
from ..fixed_mana_abilities import MANA_COST_KEYS


def fixed_mana_echo_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    event_condition: Mapping[str, Any] | None,
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Return ownership only for one ordinary fixed-mana Echo trigger."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if "echo" not in mechanics or len(effects) != 1:
        return ()
    effect = effects[0]
    cost = effect.get("cost")
    if (
        target_schema is not None
        or set(effect) != {"op", "player", "source", "cost"}
        or effect.get("op") != "echo_upkeep"
        or effect.get("player") != "$controller"
        or effect.get("source") != "$source"
        or not isinstance(cost, Mapping)
        or set(cost) != set(MANA_COST_KEYS)
        or any(type(amount) is not int or amount < 0 for amount in cost.values())
    ):
        return ()
    if dict(event_condition or {}) != {
        "all": [
            {"field": "step", "op": "eq", "value": "upkeep"},
            {"field": ECHO_CONTROL_CONDITION_FIELD, "op": "truthy"},
        ]
    }:
        return ()
    return ("trigger.keyword.echo.fixed_mana",)


__all__ = ["fixed_mana_echo_node_capabilities"]
