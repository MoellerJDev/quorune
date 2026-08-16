from __future__ import annotations

"""Strict internal shape extraction for fixed ``Choose one`` programs."""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from ..compiler.modal_templates import FIXED_CHOOSE_ONE_MODAL_MECHANIC
from ..targets import target_plan


@dataclass(frozen=True, slots=True)
class FixedModalBranch:
    effects: tuple[Mapping[str, Any], ...]
    target_schema: Mapping[str, Any] | None
    mechanics: tuple[str, ...]


def fixed_choose_one_modal_branches(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[FixedModalBranch, ...] | None:
    """Return exact branches, or ``None`` for every malformed modal shape."""

    mechanics = tuple(str(value).casefold() for value in mechanic_ids)
    if (
        effects
        or len(mechanics) != len(set(mechanics))
        or FIXED_CHOOSE_ONE_MODAL_MECHANIC not in mechanics
        or not isinstance(target_schema, Mapping)
        or set(target_schema) != {"mode_count", "modes"}
        or type(target_schema.get("mode_count")) is not int
        or target_schema.get("mode_count") != 1
    ):
        return None
    definitions = target_schema.get("modes")
    if not isinstance(definitions, Mapping) or len(definitions) not in {2, 3}:
        return None
    expected_ids = tuple(
        f"mode_{index}" for index in range(1, len(definitions) + 1)
    )
    if tuple(definitions) != expected_ids:
        return None

    branches: list[FixedModalBranch] = []
    represented = {FIXED_CHOOSE_ONE_MODAL_MECHANIC}
    for definition in definitions.values():
        if not isinstance(definition, Mapping):
            return None
        raw_effects = definition.get("effects")
        raw_mechanics = definition.get("mechanics")
        if (
            not isinstance(raw_effects, (list, tuple))
            or not raw_effects
            or any(not isinstance(effect, Mapping) for effect in raw_effects)
            or not isinstance(raw_mechanics, (list, tuple))
            or not raw_mechanics
            or any(
                not isinstance(mechanic, str)
                or not mechanic
                or mechanic != mechanic.casefold()
                for mechanic in raw_mechanics
            )
            or len(raw_mechanics) != len(set(raw_mechanics))
            or FIXED_CHOOSE_ONE_MODAL_MECHANIC in raw_mechanics
        ):
            return None
        child_schema = {
            key: value
            for key, value in definition.items()
            if key not in {"effects", "mechanics"}
        }
        if child_schema == {"groups": []}:
            target = None
        else:
            if "groups" in child_schema or "modes" in child_schema:
                return None
            try:
                plan = target_plan(child_schema)
            except (TypeError, ValueError):
                return None
            if len(plan.groups) != 1:
                return None
            target = child_schema
        branch_mechanics = tuple(raw_mechanics)
        represented.update(branch_mechanics)
        branches.append(
            FixedModalBranch(
                effects=tuple(dict(effect) for effect in raw_effects),
                target_schema=target,
                mechanics=branch_mechanics,
            )
        )
    if set(mechanics) != represented:
        return None
    return tuple(branches)


__all__ = ["FixedModalBranch", "fixed_choose_one_modal_branches"]
