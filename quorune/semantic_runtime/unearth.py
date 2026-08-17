from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

from ..card_programs.admission import REQUIRES_COMPLETE_CARD_PROGRAM_FIELD
from ..rules.capabilities import load_default_capability_registry
from ..unearth import (
    OrdinaryUnearthAbilitySpec,
    UNEARTH_ABILITY_HANDLER_ID,
    UNEARTH_CAPABILITY_ID,
    UNEARTH_EFFECT_HANDLER_ID,
    UNEARTH_EFFECT_OPERATION,
    UnearthError,
    UnearthIntent,
)
from .component_registry import RuntimeComponentRegistry, exact_fields
from .context import ReadOnlyHandlerContext, SemanticNodeError
from .intents import IntentPlan


@dataclass(frozen=True, slots=True)
class OrdinaryUnearthAbilityHandler:
    handler_id: str = UNEARTH_ABILITY_HANDLER_ID
    schema_version: int = 1
    family: str = "ability.activated.unearth"
    event: str = "activate"
    rule_references: tuple[str, ...] = (
        "602.1",
        "602.2",
        "702.84",
        "702.84a",
    )
    capability_dependencies: tuple[str, ...] = (UNEARTH_CAPABILITY_ID,)

    def validate(
        self,
        descriptor: Mapping[str, Any],
    ) -> OrdinaryUnearthAbilitySpec:
        exact_fields(
            descriptor,
            {
                "handler_id",
                "schema_version",
                "event",
                REQUIRES_COMPLETE_CARD_PROGRAM_FIELD,
                "ability",
            },
            field="ordinary Unearth handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Unearth handler ID mismatch")
        if descriptor["schema_version"] != self.schema_version:
            raise SemanticNodeError("Unsupported Unearth handler schema version")
        if descriptor["event"] != self.event:
            raise SemanticNodeError("Unearth ability handler must use activate")
        if descriptor[REQUIRES_COMPLETE_CARD_PROGRAM_FIELD] is not True:
            raise SemanticNodeError(
                "Unearth requires complete-card program admission"
            )
        ability = descriptor["ability"]
        if not isinstance(ability, Mapping):
            raise SemanticNodeError("Unearth ability must be an object")
        try:
            return OrdinaryUnearthAbilitySpec.from_dict(ability)
        except UnearthError as exc:
            raise SemanticNodeError(str(exc)) from exc

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: object,
    ) -> tuple[OrdinaryUnearthAbilitySpec, ...]:
        del context
        return (self.validate(descriptor),)


class OrdinaryUnearthAbilityRegistry(
    RuntimeComponentRegistry[object, OrdinaryUnearthAbilitySpec]
):
    pass


@lru_cache(maxsize=1)
def default_ordinary_unearth_ability_registry(
) -> OrdinaryUnearthAbilityRegistry:
    registry = OrdinaryUnearthAbilityRegistry((OrdinaryUnearthAbilityHandler(),))
    registry.require_registered_capabilities(load_default_capability_registry())
    return registry.freeze()


def ordinary_unearth_specs_from_descriptors(
    descriptors: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]],
) -> tuple[OrdinaryUnearthAbilitySpec, ...]:
    registry = default_ordinary_unearth_ability_registry()
    result: list[OrdinaryUnearthAbilitySpec] = []
    for descriptor in descriptors:
        if registry.describe(str(descriptor.get("handler_id") or "")) is None:
            continue
        result.extend(registry.lower(descriptor, None))
    return tuple(result)


@dataclass(frozen=True, slots=True)
class UnearthEffectHandler:
    operation: str = UNEARTH_EFFECT_OPERATION
    handler_id: str = UNEARTH_EFFECT_HANDLER_ID
    schema_version: int = 1
    family: str = "zone.unearth"
    rule_references: tuple[str, ...] = ("702.84", "702.84a")
    capability_dependencies: tuple[str, ...] = (UNEARTH_CAPABILITY_ID,)

    def lower(
        self,
        effect: Mapping[str, Any],
        context: ReadOnlyHandlerContext,
    ) -> IntentPlan:
        allowed = {"op", "action", "_replacement_selections"}
        unknown = sorted(set(effect) - allowed)
        missing = sorted({"op", "action"} - set(effect))
        if missing or unknown:
            raise SemanticNodeError(
                "Unearth effect has an invalid shape"
            )
        if effect["op"] != self.operation:
            raise SemanticNodeError("Unearth effect operation mismatch")
        action = str(effect["action"] or "")
        if action not in {"return", "exile"}:
            raise SemanticNodeError("Unearth effect action is unsupported")
        source = context.source
        if source is None or not all(
            (source.stack_ref, source.object_id, source.logical_object_id, source.card_ref)
        ):
            raise SemanticNodeError("Unearth effect requires typed source identity")
        selections = effect.get("_replacement_selections") or ()
        if not isinstance(selections, (list, tuple)):
            raise SemanticNodeError(
                "Unearth replacement selections must be an array"
            )
        try:
            intent = UnearthIntent(
                action=action,
                actor=context.actor,
                stack_ref=source.stack_ref,
                object_id=str(source.object_id),
                card_ref=str(source.card_ref),
                logical_object_id=str(source.logical_object_id),
                replacement_selections=tuple(selections),
            )
        except UnearthError as exc:
            raise SemanticNodeError(str(exc)) from exc
        return IntentPlan(
            operation=self.operation,
            handler_id=self.handler_id,
            intents=(intent,),
        )


UNEARTH_EFFECT_HANDLERS = (UnearthEffectHandler(),)


__all__ = [
    "default_ordinary_unearth_ability_registry",
    "OrdinaryUnearthAbilityHandler",
    "OrdinaryUnearthAbilityRegistry",
    "ordinary_unearth_specs_from_descriptors",
    "UNEARTH_EFFECT_HANDLERS",
    "UnearthEffectHandler",
]
