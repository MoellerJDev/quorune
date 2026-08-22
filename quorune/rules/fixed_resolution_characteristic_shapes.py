from __future__ import annotations

"""Capability closure for fixed resolution-locked characteristic sets."""

from typing import Any, Iterable, Mapping, Sequence

from ..compiler.creature_subtypes import canonical_creature_subtype
from ..object_predicate import ObjectQueryError, ObjectQuerySpec


FIXED_RESOLUTION_CHARACTERISTICS_CAPABILITY = (
    "continuous.resolution.fixed_characteristics_until_end_of_turn"
)


def _controlled_creature_query_is_closed(query: ObjectQuerySpec) -> bool:
    if (
        query.zones != ("battlefield",)
        or query.owner is not None
        or query.controller != "$controller"
        or query.types_any
        or query.excluded_types
        or query.subtypes_any
        or query.excluded_subtypes
        or query.colors_any
        or query.colorless is not None
        or query.keywords_all
        or query.token is not None
        or query.tapped is not None
        or query.include_phased_out
        or query.known_to_actor is not None
        or query.state_predicate is not None
        or query.exclude_ref not in {None, "$source"}
    ):
        return False
    qualifiers = sum(
        bool(value)
        for value in (
            query.subtypes_all,
            query.supertypes_all,
            query.colors_all,
        )
    )
    if query.types_all == ("artifact", "creature"):
        return qualifiers == 0
    if query.types_all != ("creature",) or qualifiers > 1:
        return False
    if query.subtypes_all:
        return (
            len(query.subtypes_all) == 1
            and canonical_creature_subtype(query.subtypes_all[0])
            == query.subtypes_all[0]
        )
    if query.supertypes_all:
        return query.supertypes_all == ("legendary",)
    if query.colors_all:
        return len(query.colors_all) == 1 and query.colors_all[0] in "WUBRG"
    return True


def fixed_controlled_characteristic_set_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Own one fixed, resolution-locked controlled-creature modifier."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if (
        "cr-611-continuous-effects" not in mechanics
        or target_schema is not None
        or len(effects) != 1
    ):
        return ()
    effect = effects[0]
    if (
        set(effect) != {"op", "predicate", "power", "toughness"}
        or effect.get("op")
        != "modify_all_matching_permanents_until_end_of_turn"
        or type(effect.get("power")) is not int
        or type(effect.get("toughness")) is not int
        or not isinstance(effect.get("predicate"), Mapping)
    ):
        return ()
    try:
        query = ObjectQuerySpec.from_dict(effect["predicate"])
    except (ObjectQueryError, TypeError):
        return ()
    if (
        dict(effect["predicate"]) != query.to_dict()
        or not _controlled_creature_query_is_closed(query)
    ):
        return ()
    return (FIXED_RESOLUTION_CHARACTERISTICS_CAPABILITY,)


__all__ = [
    "FIXED_RESOLUTION_CHARACTERISTICS_CAPABILITY",
    "fixed_controlled_characteristic_set_node_capabilities",
]
