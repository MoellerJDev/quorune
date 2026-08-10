from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

from ..convoke import ConvokeError, ConvokeSpec
from ..rules.capabilities import load_default_capability_registry
from .component_registry import RuntimeComponentRegistry, exact_fields
from .context import SemanticNodeError


CONVOKE_ACTIVE_ZONE = "stack"
CONVOKE_COST_EVENT = "cast.cost"
CONVOKE_HANDLER_ID = "casting.payment.convoke.v1"


@dataclass(frozen=True, slots=True)
class ConvokeCostHandler:
    handler_id: str = CONVOKE_HANDLER_ID
    schema_version: int = 1
    family: str = "casting.payment.convoke"
    event: str = CONVOKE_COST_EVENT
    rule_references: tuple[str, ...] = (
        "601.2f",
        "601.2g",
        "601.2h",
        "601.2i",
        "702.51",
        "702.51a",
        "702.51b",
        "702.51c",
        "702.51d",
    )
    capability_dependencies: tuple[str, ...] = ("casting.payment.convoke",)

    def validate(self, descriptor: Mapping[str, Any]) -> ConvokeSpec:
        exact_fields(
            descriptor,
            {"handler_id", "schema_version", "event", "payment"},
            field="Convoke cost handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Convoke cost handler ID mismatch")
        if (
            type(descriptor["schema_version"]) is not int
            or descriptor["schema_version"] != self.schema_version
        ):
            raise SemanticNodeError("Unsupported Convoke cost handler version")
        if descriptor["event"] != self.event:
            raise SemanticNodeError(
                f"Convoke cost handler must use {self.event}"
            )
        payment = descriptor["payment"]
        if not isinstance(payment, Mapping):
            raise SemanticNodeError("Convoke payment descriptor must be an object")
        try:
            return ConvokeSpec.from_dict(payment)
        except ConvokeError as exc:
            raise SemanticNodeError(str(exc)) from exc

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: object,
    ) -> tuple[ConvokeSpec, ...]:
        del context
        return (self.validate(descriptor),)


class CastCostComponentRegistry(RuntimeComponentRegistry[object, ConvokeSpec]):
    pass


@lru_cache(maxsize=1)
def default_cast_cost_component_registry() -> CastCostComponentRegistry:
    registry = CastCostComponentRegistry((ConvokeCostHandler(),))
    registry.require_registered_capabilities(load_default_capability_registry())
    return registry.freeze()


def convoke_handler_descriptor() -> dict[str, Any]:
    return {
        "handler_id": CONVOKE_HANDLER_ID,
        "schema_version": 1,
        "event": CONVOKE_COST_EVENT,
        "payment": ConvokeSpec().to_dict(),
    }


__all__ = [
    "CONVOKE_ACTIVE_ZONE",
    "CONVOKE_COST_EVENT",
    "CONVOKE_HANDLER_ID",
    "CastCostComponentRegistry",
    "ConvokeCostHandler",
    "convoke_handler_descriptor",
    "default_cast_cost_component_registry",
]
