from __future__ import annotations

"""Strict CardProgram capability shape for ordinary printed Crew."""

from typing import Any, Iterable, Mapping, Sequence

from ..crew import CREW_CAPABILITY_ID, CREW_MECHANIC_ID


_COST_FIELDS = frozenset(
    {
        "text",
        "mana",
        "complex_symbols",
        "tap_source",
        "untap_source",
        "discard_source",
        "sacrifice_source",
        "exile_source",
        "life_payment",
        "energy_payment",
        "loyalty_delta",
        "choices",
        "uncompiled_costs",
        "crew",
    }
)
_MANA_KEYS = frozenset({"GENERIC", "W", "U", "B", "R", "G", "C"})


def ordinary_crew_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
    cost_schema: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    mechanics = {str(value).casefold() for value in mechanic_ids}
    if mechanics != {CREW_MECHANIC_ID}:
        return ()
    if target_schema is not None or len(effects) != 1:
        return ()
    if dict(effects[0]) != {
        "op": "add_types_until_end_of_turn",
        "card": "$source.zone_object",
        "types": ["Artifact", "Creature"],
    }:
        return ()
    if not isinstance(cost_schema, Mapping) or frozenset(cost_schema) != _COST_FIELDS:
        return ()
    threshold = cost_schema.get("crew")
    if type(threshold) is not int or threshold < 0:
        return ()
    if cost_schema.get("text") != f"Crew {threshold}":
        return ()
    mana = cost_schema.get("mana")
    if (
        not isinstance(mana, Mapping)
        or frozenset(mana) != _MANA_KEYS
        or any(type(value) is not int or value != 0 for value in mana.values())
    ):
        return ()
    if cost_schema.get("complex_symbols") != []:
        return ()
    if any(
        cost_schema.get(field)
        for field in (
            "tap_source",
            "untap_source",
            "discard_source",
            "sacrifice_source",
            "exile_source",
            "life_payment",
            "energy_payment",
            "choices",
            "uncompiled_costs",
        )
    ):
        return ()
    if cost_schema.get("loyalty_delta") is not None:
        return ()
    return (CREW_CAPABILITY_ID,)


__all__ = ["ordinary_crew_node_capabilities"]
