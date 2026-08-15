from __future__ import annotations

"""Capability shape for optional fixed counter event-trigger wrappers."""

from typing import Any, Iterable, Mapping, Sequence

from .node_capability_shapes import (
    fixed_counter_placement_batch_node_capabilities,
    fixed_counter_placement_node_capabilities,
    fixed_counter_placement_set_node_capabilities,
    fixed_counter_placement_target_set_node_capabilities,
    fixed_player_counter_placement_node_capabilities,
)


def optional_fixed_counter_event_trigger_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Recognize one optional wrapper around one closed counter effect."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if (
        "optional-fixed-counter-event-trigger" not in mechanics
        or len(effects) != 1
    ):
        return ()
    wrapper = effects[0]
    if (
        set(wrapper) != {"op", "player", "effect"}
        or wrapper.get("op") != "offer_optional_counter_placement"
        or wrapper.get("player") != "$controller"
        or not isinstance(wrapper.get("effect"), Mapping)
    ):
        return ()
    nested_effects = (wrapper["effect"],)
    nested_dependencies: set[str] = set()
    for resolver in (
        fixed_counter_placement_batch_node_capabilities,
        fixed_counter_placement_node_capabilities,
        fixed_counter_placement_set_node_capabilities,
        fixed_counter_placement_target_set_node_capabilities,
        fixed_player_counter_placement_node_capabilities,
    ):
        nested_dependencies.update(
            resolver(
                effects=nested_effects,
                target_schema=target_schema,
                mechanic_ids=mechanics,
            )
        )
    if not any(
        dependency.startswith("counter.producer.")
        for dependency in nested_dependencies
    ):
        return ()
    return (
        "counter.producer.optional_fixed_event_trigger",
        *sorted(nested_dependencies),
    )


__all__ = ["optional_fixed_counter_event_trigger_node_capabilities"]
