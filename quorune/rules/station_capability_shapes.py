from __future__ import annotations

"""Strict CardProgram capability shape for ordinary printed Station."""

from typing import Any, Iterable, Mapping, Sequence

from ..station import STATION_CAPABILITY_ID, STATION_MECHANIC_ID


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
    }
)
_MANA_KEYS = frozenset({"GENERIC", "W", "U", "B", "R", "G", "C"})


def ordinary_station_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
    cost_schema: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    mechanics = {str(value).casefold() for value in mechanic_ids}
    if mechanics != {STATION_MECHANIC_ID}:
        return ()
    if target_schema is not None or len(effects) != 1:
        return ()
    if dict(effects[0]) != {
        "op": "station",
        "card": "$source.zone_object",
        "amount": "$station.power",
        "source": "$source",
    }:
        return ()
    if not isinstance(cost_schema, Mapping) or frozenset(cost_schema) != _COST_FIELDS:
        return ()
    if cost_schema.get("text") != "Tap another untapped creature you control":
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
            "uncompiled_costs",
        )
    ):
        return ()
    if cost_schema.get("loyalty_delta") is not None:
        return ()
    if cost_schema.get("choices") != [
        {
            "k": "station",
            "n": 1,
            "z": "battlefield",
            "t": "creature",
            "other": 1,
        }
    ]:
        return ()
    return (STATION_CAPABILITY_ID,)


__all__ = ["ordinary_station_node_capabilities"]
