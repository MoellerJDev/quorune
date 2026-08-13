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
AFFINITY_HANDLER_ID = "casting.payment.affinity-artifacts.v1"


@dataclass(frozen=True, slots=True)
class AffinitySpec:
    """One closed printed Affinity-for-artifacts cost reduction."""

    card_type: str = "artifact"

    def to_payment_mechanic(self) -> dict[str, Any]:
        return {"kind": "affinity", "card_type": self.card_type}


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


@dataclass(frozen=True, slots=True)
class AffinityCostHandler:
    handler_id: str = AFFINITY_HANDLER_ID
    schema_version: int = 1
    family: str = "casting.payment.affinity_artifacts"
    event: str = CONVOKE_COST_EVENT
    rule_references: tuple[str, ...] = (
        "601.2f",
        "601.2g",
        "601.2h",
        "702.41",
        "702.41a",
        "702.41b",
    )
    capability_dependencies: tuple[str, ...] = (
        "casting.payment.affinity_artifacts",
    )

    def validate(self, descriptor: Mapping[str, Any]) -> AffinitySpec:
        exact_fields(
            descriptor,
            {"handler_id", "schema_version", "event", "payment"},
            field="Affinity cost handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Affinity cost handler ID mismatch")
        if (
            type(descriptor["schema_version"]) is not int
            or descriptor["schema_version"] != self.schema_version
        ):
            raise SemanticNodeError("Unsupported Affinity cost handler version")
        if descriptor["event"] != self.event:
            raise SemanticNodeError(
                f"Affinity cost handler must use {self.event}"
            )
        payment = descriptor["payment"]
        if not isinstance(payment, Mapping):
            raise SemanticNodeError("Affinity payment descriptor must be an object")
        exact_fields(
            payment,
            {"schema_version", "kind", "card_type"},
            field="Affinity payment descriptor",
        )
        if (
            type(payment["schema_version"]) is not int
            or payment["schema_version"] != 1
        ):
            raise SemanticNodeError("Unsupported Affinity payment version")
        if payment["kind"] != "affinity" or payment["card_type"] != "artifact":
            raise SemanticNodeError(
                "Affinity payment must be the closed artifact-count family"
            )
        return AffinitySpec()

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: object,
    ) -> tuple[AffinitySpec, ...]:
        del context
        return (self.validate(descriptor),)


class CastCostComponentRegistry(
    RuntimeComponentRegistry[object, ConvokeSpec | AffinitySpec]
):
    pass


@lru_cache(maxsize=1)
def default_cast_cost_component_registry() -> CastCostComponentRegistry:
    registry = CastCostComponentRegistry(
        (AffinityCostHandler(), ConvokeCostHandler())
    )
    registry.require_registered_capabilities(load_default_capability_registry())
    return registry.freeze()


def convoke_handler_descriptor() -> dict[str, Any]:
    return {
        "handler_id": CONVOKE_HANDLER_ID,
        "schema_version": 1,
        "event": CONVOKE_COST_EVENT,
        "payment": ConvokeSpec().to_dict(),
    }


def affinity_handler_descriptor() -> dict[str, Any]:
    return {
        "handler_id": AFFINITY_HANDLER_ID,
        "schema_version": 1,
        "event": CONVOKE_COST_EVENT,
        "payment": {
            "schema_version": 1,
            "kind": "affinity",
            "card_type": "artifact",
        },
    }


__all__ = [
    "AFFINITY_HANDLER_ID",
    "AffinityCostHandler",
    "AffinitySpec",
    "CONVOKE_ACTIVE_ZONE",
    "CONVOKE_COST_EVENT",
    "CONVOKE_HANDLER_ID",
    "CastCostComponentRegistry",
    "ConvokeCostHandler",
    "affinity_handler_descriptor",
    "convoke_handler_descriptor",
    "default_cast_cost_component_registry",
]
