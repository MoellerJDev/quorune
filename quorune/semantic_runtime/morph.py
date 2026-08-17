from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

from ..morph import (
    FixedManaMorphSpec,
    MORPH_CAPABILITY_ID,
    MORPH_HANDLER_ID,
    MORPH_RUNTIME_EVENT,
    MorphError,
)
from ..rules.capabilities import load_default_capability_registry
from .component_registry import RuntimeComponentRegistry, exact_fields
from .context import SemanticNodeError


@dataclass(frozen=True, slots=True)
class FixedManaMorphHandler:
    handler_id: str = MORPH_HANDLER_ID
    schema_version: int = 1
    family: str = "casting.morph.fixed_mana"
    event: str = MORPH_RUNTIME_EVENT
    rule_references: tuple[str, ...] = (
        "116.2b",
        "702.37",
        "702.37a",
        "702.37c",
        "702.37e",
        "708.2",
        "708.4",
        "708.5",
        "708.8",
        "708.9",
    )
    capability_dependencies: tuple[str, ...] = (MORPH_CAPABILITY_ID,)

    def validate(self, descriptor: Mapping[str, Any]) -> FixedManaMorphSpec:
        exact_fields(
            descriptor,
            {"handler_id", "schema_version", "event", "morph"},
            field="fixed-mana Morph handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Morph handler ID mismatch")
        if descriptor["schema_version"] != self.schema_version:
            raise SemanticNodeError("Unsupported Morph handler schema version")
        if descriptor["event"] != self.event:
            raise SemanticNodeError("Morph handler event mismatch")
        value = descriptor["morph"]
        if not isinstance(value, Mapping):
            raise SemanticNodeError("Morph descriptor must be an object")
        try:
            return FixedManaMorphSpec.from_dict(value)
        except MorphError as exc:
            raise SemanticNodeError(str(exc)) from exc

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: object,
    ) -> tuple[FixedManaMorphSpec, ...]:
        del context
        return (self.validate(descriptor),)


class FixedManaMorphRegistry(RuntimeComponentRegistry[object, FixedManaMorphSpec]):
    pass


@lru_cache(maxsize=1)
def default_fixed_mana_morph_registry() -> FixedManaMorphRegistry:
    registry = FixedManaMorphRegistry((FixedManaMorphHandler(),))
    registry.require_registered_capabilities(load_default_capability_registry())
    return registry.freeze()


__all__ = [
    "default_fixed_mana_morph_registry",
    "FixedManaMorphHandler",
    "FixedManaMorphRegistry",
]
