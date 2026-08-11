from __future__ import annotations

"""Capability shapes for closed direct permanent-counter removal nodes."""

from typing import Any, Iterable, Mapping, Sequence

from .node_capability_shapes import (
    direct_target_predicate_capabilities,
    fixed_counter_target_schema_is_closed,
)


def fixed_counter_removal_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Return capabilities only for one closed fixed counter removal."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if (
        not {"cr-122-counters", "cr-115-targets"}.issubset(mechanics)
        or len(effects) != 1
    ):
        return ()
    effect = effects[0]
    if (
        set(effect) != {"op", "card", "counter", "amount", "source"}
        or effect.get("op") != "remove_counters"
        or effect.get("card") != "$target.0"
        or type(effect.get("counter")) is not str
        or not effect.get("counter")
        or type(effect.get("amount")) is not int
        or effect.get("amount", 0) <= 0
        or effect.get("source") != "$source"
        or not fixed_counter_target_schema_is_closed(target_schema)
    ):
        return ()
    assert target_schema is not None
    return (
        "counter.removal.fixed_effect",
        *direct_target_predicate_capabilities(target_schema),
        "target.revalidate_resolution",
    )


def all_counter_removal_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Return capabilities only for one direct all-counter removal."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if (
        not {"cr-122-counters", "cr-115-targets"}.issubset(mechanics)
        or len(effects) != 1
    ):
        return ()
    effect = effects[0]
    if (
        set(effect) != {"op", "card", "source"}
        or effect.get("op") != "remove_all_counters"
        or effect.get("card") != "$target.0"
        or effect.get("source") != "$source"
        or not fixed_counter_target_schema_is_closed(target_schema)
    ):
        return ()
    assert target_schema is not None
    return (
        "counter.removal.all_effect",
        *direct_target_predicate_capabilities(target_schema),
        "target.revalidate_resolution",
    )


__all__ = [
    "all_counter_removal_node_capabilities",
    "fixed_counter_removal_node_capabilities",
]
