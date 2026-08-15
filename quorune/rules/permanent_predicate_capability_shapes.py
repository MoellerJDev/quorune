from __future__ import annotations

"""Closed capability shapes for shared permanent predicates."""

from typing import Any, Mapping

from ..compiler.direct_target import DirectPermanentTargetSpec
from ..object_predicate import ObjectQueryError, PermanentStatePredicateSpec


PUBLIC_PERMANENT_STATE_CAPABILITY = (
    "state_query.permanent.public_state_predicate"
)


def fixed_counter_target_schema_is_closed(
    target_schema: Mapping[str, Any] | None,
    *,
    allow_commander: bool = False,
) -> bool:
    """Return whether one direct permanent target schema is closed."""

    try:
        DirectPermanentTargetSpec.from_target_schema(
            target_schema,  # type: ignore[arg-type]
            allow_commander=allow_commander,
        )
    except (TypeError, ValueError):
        return False
    return True


def direct_target_predicate_capabilities(
    target_schema: Mapping[str, Any],
) -> tuple[str, ...]:
    """Return the characteristic and public-state owners for one target."""

    target_spec = DirectPermanentTargetSpec.from_target_schema(target_schema)
    return (
        *(
            ("target.permanent.characteristic_predicate",)
            if target_spec.uses_compound_characteristics
            else ()
        ),
        *(
            (PUBLIC_PERMANENT_STATE_CAPABILITY,)
            if target_spec.uses_public_state
            else ()
        ),
    )


def public_state_query_capabilities(
    state_predicate: PermanentStatePredicateSpec | None,
) -> tuple[str, ...]:
    """Return the shared owner for a typed affected-set state predicate."""

    return (
        (PUBLIC_PERMANENT_STATE_CAPABILITY,)
        if state_predicate is not None
        else ()
    )


def fixed_counter_target_set_state_capabilities(
    schema: Mapping[str, Any],
    *,
    types_any: tuple[str, ...],
) -> tuple[str, ...] | None:
    """Validate the closed tapped-creature target-set state descriptor."""

    raw_state = schema.get("state_predicate")
    try:
        state_predicate = (
            PermanentStatePredicateSpec.from_dict(raw_state)
            if raw_state is not None
            else None
        )
    except ObjectQueryError:
        return None
    if state_predicate is None:
        return ()
    if (
        state_predicate.tapped is not True
        or state_predicate.entered_this_turn
        or state_predicate.counter_name is not None
        or types_any != ("creature",)
    ):
        return None
    return (PUBLIC_PERMANENT_STATE_CAPABILITY,)


__all__ = [
    "direct_target_predicate_capabilities",
    "fixed_counter_target_schema_is_closed",
    "fixed_counter_target_set_state_capabilities",
    "public_state_query_capabilities",
]
