from __future__ import annotations

"""Capability closure for fixed life and ordered controller effects."""

from typing import Any, Iterable, Mapping, Sequence

from .node_capability_shapes import (
    fixed_counter_placement_node_capabilities,
    fixed_draw_node_capabilities,
    fixed_scry_node_capabilities,
)


_FIXED_CONTROLLER_SEQUENCE_MECHANIC = "fixed-controller-effect-sequence"
_FIXED_COUNTER_CONTROLLER_SEQUENCE_MECHANIC = (
    "fixed-counter-controller-effect-sequence"
)
_LIFE_OPERATION = "life"


def _positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def fixed_life_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Return life ownership only for the closed fixed-value grammar."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if (
        "cr-119-life" not in mechanics
        or target_schema is not None
        or len(effects) != 1
    ):
        return ()
    effect = effects[0]
    operation = effect.get("op")
    if operation == _LIFE_OPERATION:
        valid = (
            set(effect) == {"op", "player", "delta"}
            and effect.get("player") == "$controller"
            and _positive_int(effect.get("delta"))
        )
    elif operation == "lose_life":
        valid = (
            set(effect) == {"op", "player", "amount"}
            and effect.get("player") == "$controller"
            and _positive_int(effect.get("amount"))
        )
    elif operation == "lose_life_each_opponent":
        valid = (
            set(effect) == {"op", "amount"}
            and _positive_int(effect.get("amount"))
            and "cr-101-the-magic-golden-rules" in mechanics
        )
    else:
        valid = False
    return ("life.change.effect",) if valid else ()


def fixed_controller_effect_sequence_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Own exactly two ordered controller effects containing one draw."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if (
        _FIXED_CONTROLLER_SEQUENCE_MECHANIC not in mechanics
        or target_schema is not None
        or len(effects) != 2
    ):
        return ()
    dependencies: set[str] = {"resolution.effect_sequence.fixed_controller"}
    draw_count = 0
    for effect in effects:
        operation = effect.get("op")
        if operation == "draw":
            required = fixed_draw_node_capabilities(
                effects=(effect,),
                target_schema=None,
                mechanic_ids=("cr-121-drawing-a-card",),
            )
            draw_count += 1
        elif operation in {_LIFE_OPERATION, "lose_life"}:
            required = fixed_life_node_capabilities(
                effects=(effect,),
                target_schema=None,
                mechanic_ids=("cr-119-life",),
            )
        elif operation == "scry":
            required = fixed_scry_node_capabilities(
                effects=(effect,),
                target_schema=None,
                mechanic_ids=("scry",),
            )
        else:
            return ()
        if not required:
            return ()
        dependencies.update(required)
    if draw_count != 1:
        return ()
    return tuple(sorted(dependencies))


def fixed_counter_controller_effect_sequence_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Own one fixed counter placement and one fixed controller effect."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if (
        _FIXED_COUNTER_CONTROLLER_SEQUENCE_MECHANIC not in mechanics
        or len(effects) != 2
    ):
        return ()
    counter_effects = tuple(
        effect for effect in effects if effect.get("op") == "place_counters"
    )
    controller_effects = tuple(
        effect for effect in effects if effect.get("op") != "place_counters"
    )
    if len(counter_effects) != 1 or len(controller_effects) != 1:
        return ()
    counter_effect = counter_effects[0]
    if counter_effect.get("card") == "$source.zone_object":
        if target_schema is not None:
            return ()
        normalized_counter = {**counter_effect, "card": "$source"}
    elif counter_effect.get("card") == "$target.0":
        normalized_counter = counter_effect
    else:
        return ()
    counter_dependencies = fixed_counter_placement_node_capabilities(
        effects=(normalized_counter,),
        target_schema=target_schema,
        mechanic_ids=mechanics,
    )
    if not counter_dependencies:
        return ()
    controller_effect = controller_effects[0]
    operation = controller_effect.get("op")
    if operation == "draw":
        controller_dependencies = fixed_draw_node_capabilities(
            effects=(controller_effect,),
            target_schema=None,
            mechanic_ids=("cr-121-drawing-a-card",),
        )
    elif operation in {_LIFE_OPERATION, "lose_life"}:
        controller_dependencies = fixed_life_node_capabilities(
            effects=(controller_effect,),
            target_schema=None,
            mechanic_ids=("cr-119-life",),
        )
    elif operation == "scry":
        controller_dependencies = fixed_scry_node_capabilities(
            effects=(controller_effect,),
            target_schema=None,
            mechanic_ids=("scry",),
        )
    else:
        return ()
    if not controller_dependencies:
        return ()
    return tuple(
        sorted(
            {
                "resolution.effect_sequence.fixed_counter_controller",
                *counter_dependencies,
                *controller_dependencies,
            }
        )
    )


__all__ = [
    "fixed_counter_controller_effect_sequence_node_capabilities",
    "fixed_controller_effect_sequence_node_capabilities",
    "fixed_life_node_capabilities",
]
