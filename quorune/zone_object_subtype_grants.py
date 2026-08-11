from __future__ import annotations

"""Resolution-created subtype additions pinned to one battlefield incarnation."""

from typing import Any, Protocol

from .continuous_effect_model import (
    ContinuousEffect,
    ContinuousEffectDuration,
    ContinuousOperation,
    Layer,
)
from .continuous_effect_state import (
    ContinuousEffectStateError,
    ResolutionEffectSource,
    create_resolution_continuous_effect,
)
from .creature_subtypes import canonical_creature_subtype


class ZoneObjectSubtypeGrantError(ValueError):
    """A zone-object subtype addition was malformed or stale."""


class ZoneObjectSubtypeGrantHost(Protocol):
    state: Any

    def _next_ref(self, prefix: str) -> str: ...

    def _next_zone_timestamp(self) -> int: ...


def commit_zone_object_subtype_addition(
    host: ZoneObjectSubtypeGrantHost,
    *,
    card: Any,
    source: ResolutionEffectSource,
    subtype: str,
) -> ContinuousEffect:
    """Add one pinned creature subtype for this battlefield logical object."""

    if getattr(card, "zone", None) != "battlefield" or bool(
        getattr(card, "phased_out", False)
    ):
        raise ZoneObjectSubtypeGrantError(
            "Zone-object subtype additions require a phased-in battlefield permanent"
        )
    if type(getattr(card, "object_id", None)) is not str or not card.object_id:
        raise ZoneObjectSubtypeGrantError(
            "Zone-object subtype additions require physical object identity"
        )
    if (
        type(getattr(card, "logical_object_id", None)) is not str
        or not card.logical_object_id
    ):
        raise ZoneObjectSubtypeGrantError(
            "Zone-object subtype additions require logical object identity"
        )
    if not isinstance(source, ResolutionEffectSource):
        raise ZoneObjectSubtypeGrantError(
            "Zone-object subtype additions require typed resolution source identity"
        )
    normalized = canonical_creature_subtype(subtype)
    if normalized is None:
        raise ZoneObjectSubtypeGrantError(
            "Zone-object subtype additions require a pinned creature subtype"
        )
    try:
        effect = create_resolution_continuous_effect(
            host,
            source=source,
            targets=(card,),
            layer=Layer.TYPE,
            sublayer="4",
            operations=(
                ContinuousOperation(
                    "add_types",
                    (normalized.title(),),
                    field="subtypes",
                ),
            ),
            duration=ContinuousEffectDuration.ZONE_OBJECT,
        )
    except ContinuousEffectStateError as exc:
        raise ZoneObjectSubtypeGrantError(str(exc)) from exc
    if effect is None:
        raise ZoneObjectSubtypeGrantError(
            "Zone-object subtype additions require continuous-effect state"
        )
    return effect


__all__ = [
    "ZoneObjectSubtypeGrantError",
    "commit_zone_object_subtype_addition",
]
