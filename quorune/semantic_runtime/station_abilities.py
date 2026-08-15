from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

from ..rules.capabilities import load_default_capability_registry
from ..station import (
    OrdinaryStationAbilitySpec,
    STATION_CAPABILITY_ID,
    STATION_HANDLER_ID,
    StationAbilityError,
)
from .component_registry import RuntimeComponentRegistry, exact_fields
from .context import SemanticNodeError


@dataclass(frozen=True, slots=True)
class OrdinaryStationAbilityHandler:
    handler_id: str = STATION_HANDLER_ID
    schema_version: int = 1
    family: str = "ability.activated.station"
    event: str = "activate"
    rule_references: tuple[str, ...] = (
        "107.1b",
        "602.1",
        "602.2",
        "702.184",
        "702.184a",
    )
    capability_dependencies: tuple[str, ...] = (STATION_CAPABILITY_ID,)

    def validate(
        self, descriptor: Mapping[str, Any]
    ) -> OrdinaryStationAbilitySpec:
        exact_fields(
            descriptor,
            {"handler_id", "schema_version", "event", "ability"},
            field="ordinary Station handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Station handler ID mismatch")
        if descriptor["schema_version"] != self.schema_version:
            raise SemanticNodeError(
                "Unsupported ordinary Station handler schema version"
            )
        if descriptor["event"] != self.event:
            raise SemanticNodeError(
                "Ordinary Station handler must use the activate event"
            )
        ability = descriptor["ability"]
        if not isinstance(ability, Mapping):
            raise SemanticNodeError("Station ability must be an object")
        try:
            return OrdinaryStationAbilitySpec.from_dict(ability)
        except StationAbilityError as exc:
            raise SemanticNodeError(str(exc)) from exc

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: object,
    ) -> tuple[OrdinaryStationAbilitySpec, ...]:
        del context
        return (self.validate(descriptor),)


class OrdinaryStationAbilityRegistry(
    RuntimeComponentRegistry[object, OrdinaryStationAbilitySpec]
):
    pass


@lru_cache(maxsize=1)
def default_ordinary_station_ability_registry(
) -> OrdinaryStationAbilityRegistry:
    registry = OrdinaryStationAbilityRegistry(
        (OrdinaryStationAbilityHandler(),)
    )
    registry.require_registered_capabilities(
        load_default_capability_registry()
    )
    return registry.freeze()


def ordinary_station_specs_from_descriptors(
    descriptors: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]],
) -> tuple[OrdinaryStationAbilitySpec, ...]:
    registry = default_ordinary_station_ability_registry()
    result: list[OrdinaryStationAbilitySpec] = []
    for descriptor in descriptors:
        if registry.describe(str(descriptor.get("handler_id") or "")) is None:
            continue
        result.extend(registry.lower(descriptor, None))
    return tuple(result)


__all__ = [
    "OrdinaryStationAbilityHandler",
    "OrdinaryStationAbilityRegistry",
    "default_ordinary_station_ability_registry",
    "ordinary_station_specs_from_descriptors",
]
