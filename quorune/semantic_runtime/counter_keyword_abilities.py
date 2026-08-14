from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

from ..counter_keyword_abilities import (
    COUNTER_KEYWORD_ACTIVATION_HANDLER_ID,
    CounterKeywordAbilityError,
    FixedCounterKeywordAbilitySpec,
)
from ..rules.capabilities import load_default_capability_registry
from .component_registry import RuntimeComponentRegistry, exact_fields
from .context import SemanticNodeError


@dataclass(frozen=True, slots=True)
class FixedCounterKeywordAbilityHandler:
    handler_id: str = COUNTER_KEYWORD_ACTIVATION_HANDLER_ID
    schema_version: int = 1
    family: str = "ability.activated.fixed-counter-keyword"
    event: str = "activate"
    rule_references: tuple[str, ...] = (
        "602.1",
        "602.2",
        "702.77a",
        "702.87a",
        "702.97a",
        "702.107a",
    )
    capability_dependencies: tuple[str, ...] = (
        "activation.counter_keyword.fixed",
    )

    def validate(
        self, descriptor: Mapping[str, Any]
    ) -> FixedCounterKeywordAbilitySpec:
        exact_fields(
            descriptor,
            {"handler_id", "schema_version", "event", "ability"},
            field="fixed counter-keyword activation handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError(
                "Counter-keyword activation handler ID mismatch"
            )
        if descriptor["schema_version"] != self.schema_version:
            raise SemanticNodeError(
                "Unsupported counter-keyword activation handler schema version"
            )
        if descriptor["event"] != self.event:
            raise SemanticNodeError(
                "Counter-keyword activation handler must use activate"
            )
        ability = descriptor["ability"]
        if not isinstance(ability, Mapping):
            raise SemanticNodeError(
                "Counter-keyword activation ability must be an object"
            )
        try:
            return FixedCounterKeywordAbilitySpec.from_dict(ability)
        except CounterKeywordAbilityError as exc:
            raise SemanticNodeError(str(exc)) from exc

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: object,
    ) -> tuple[FixedCounterKeywordAbilitySpec, ...]:
        del context
        return (self.validate(descriptor),)


class FixedCounterKeywordAbilityRegistry(
    RuntimeComponentRegistry[object, FixedCounterKeywordAbilitySpec]
):
    pass


@lru_cache(maxsize=1)
def default_fixed_counter_keyword_ability_registry(
) -> FixedCounterKeywordAbilityRegistry:
    registry = FixedCounterKeywordAbilityRegistry(
        (FixedCounterKeywordAbilityHandler(),)
    )
    registry.require_registered_capabilities(
        load_default_capability_registry()
    )
    return registry.freeze()


def fixed_counter_keyword_specs_from_descriptors(
    descriptors: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]],
) -> tuple[FixedCounterKeywordAbilitySpec, ...]:
    registry = default_fixed_counter_keyword_ability_registry()
    result: list[FixedCounterKeywordAbilitySpec] = []
    for descriptor in descriptors:
        if registry.describe(str(descriptor.get("handler_id") or "")) is None:
            continue
        result.extend(registry.lower(descriptor, None))
    return tuple(result)


__all__ = [
    "FixedCounterKeywordAbilityHandler",
    "FixedCounterKeywordAbilityRegistry",
    "default_fixed_counter_keyword_ability_registry",
    "fixed_counter_keyword_specs_from_descriptors",
]
