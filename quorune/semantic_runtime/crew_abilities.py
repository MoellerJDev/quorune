from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

from ..crew import (
    CREW_CAPABILITY_ID,
    CREW_HANDLER_ID,
    CrewAbilityError,
    OrdinaryCrewAbilitySpec,
)
from ..rules.capabilities import load_default_capability_registry
from .component_registry import RuntimeComponentRegistry, exact_fields
from .context import SemanticNodeError


@dataclass(frozen=True, slots=True)
class OrdinaryCrewAbilityHandler:
    handler_id: str = CREW_HANDLER_ID
    schema_version: int = 1
    family: str = "ability.activated.crew"
    event: str = "activate"
    rule_references: tuple[str, ...] = (
        "205.1a",
        "205.1b",
        "302.6",
        "602.1",
        "602.2",
        "702.122",
        "702.122a",
        "702.122b",
        "702.122c",
    )
    capability_dependencies: tuple[str, ...] = (CREW_CAPABILITY_ID,)

    def validate(
        self, descriptor: Mapping[str, Any]
    ) -> OrdinaryCrewAbilitySpec:
        exact_fields(
            descriptor,
            {"handler_id", "schema_version", "event", "ability"},
            field="ordinary Crew handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Crew handler ID mismatch")
        if descriptor["schema_version"] != self.schema_version:
            raise SemanticNodeError(
                "Unsupported ordinary Crew handler schema version"
            )
        if descriptor["event"] != self.event:
            raise SemanticNodeError(
                "Ordinary Crew handler must use the activate event"
            )
        ability = descriptor["ability"]
        if not isinstance(ability, Mapping):
            raise SemanticNodeError("Crew ability must be an object")
        try:
            return OrdinaryCrewAbilitySpec.from_dict(ability)
        except CrewAbilityError as exc:
            raise SemanticNodeError(str(exc)) from exc

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: object,
    ) -> tuple[OrdinaryCrewAbilitySpec, ...]:
        del context
        return (self.validate(descriptor),)


class OrdinaryCrewAbilityRegistry(
    RuntimeComponentRegistry[object, OrdinaryCrewAbilitySpec]
):
    pass


@lru_cache(maxsize=1)
def default_ordinary_crew_ability_registry() -> OrdinaryCrewAbilityRegistry:
    registry = OrdinaryCrewAbilityRegistry((OrdinaryCrewAbilityHandler(),))
    registry.require_registered_capabilities(
        load_default_capability_registry()
    )
    return registry.freeze()


def ordinary_crew_specs_from_descriptors(
    descriptors: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]],
) -> tuple[OrdinaryCrewAbilitySpec, ...]:
    registry = default_ordinary_crew_ability_registry()
    result: list[OrdinaryCrewAbilitySpec] = []
    for descriptor in descriptors:
        if registry.describe(str(descriptor.get("handler_id") or "")) is None:
            continue
        result.extend(registry.lower(descriptor, None))
    return tuple(result)


__all__ = [
    "OrdinaryCrewAbilityHandler",
    "OrdinaryCrewAbilityRegistry",
    "default_ordinary_crew_ability_registry",
    "ordinary_crew_specs_from_descriptors",
]
