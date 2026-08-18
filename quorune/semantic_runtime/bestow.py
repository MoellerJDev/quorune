from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping

from ..bestow import BESTOW_CAPABILITY_ID, BESTOW_HANDLER_ID, BESTOW_RUNTIME_EVENT, BestowError, FixedManaBestowSpec
from ..card_programs.admission import REQUIRES_COMPLETE_CARD_PROGRAM_FIELD
from ..rules.capabilities import load_default_capability_registry
from .component_registry import RuntimeComponentRegistry, exact_fields
from .context import SemanticNodeError


@dataclass(frozen=True, slots=True)
class FixedManaBestowHandler:
    handler_id: str = BESTOW_HANDLER_ID
    schema_version: int = 1
    family: str = "casting.bestow.fixed_mana"
    event: str = BESTOW_RUNTIME_EVENT
    rule_references: tuple[str, ...] = ("601.2b", "601.2f", "702.103a", "702.103b")
    capability_dependencies: tuple[str, ...] = (BESTOW_CAPABILITY_ID,)

    def validate(self, descriptor: Mapping[str, Any]) -> FixedManaBestowSpec:
        exact_fields(descriptor, {"handler_id", "schema_version", "event", REQUIRES_COMPLETE_CARD_PROGRAM_FIELD, "bestow"}, field="fixed-mana Bestow handler")
        if descriptor["handler_id"] != self.handler_id or descriptor["schema_version"] != 1 or descriptor["event"] != self.event:
            raise SemanticNodeError("Bestow handler identity, version, or event changed")
        if descriptor[REQUIRES_COMPLETE_CARD_PROGRAM_FIELD] is not True:
            raise SemanticNodeError("Bestow requires complete-card admission")
        try:
            return FixedManaBestowSpec.from_dict(descriptor["bestow"])
        except BestowError as exc:
            raise SemanticNodeError(str(exc)) from exc

    def lower(self, descriptor: Mapping[str, Any], context: object) -> tuple[FixedManaBestowSpec, ...]:
        del context
        return (self.validate(descriptor),)


class FixedManaBestowRegistry(RuntimeComponentRegistry[object, FixedManaBestowSpec]):
    pass


@lru_cache(maxsize=1)
def default_fixed_mana_bestow_registry() -> FixedManaBestowRegistry:
    registry = FixedManaBestowRegistry((FixedManaBestowHandler(),))
    registry.require_registered_capabilities(load_default_capability_registry())
    return registry.freeze()


__all__ = ["FixedManaBestowHandler", "FixedManaBestowRegistry", "default_fixed_mana_bestow_registry"]
