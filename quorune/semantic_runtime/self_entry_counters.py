from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..replacement_effects import (
    CreateAffectedObjectCounter,
    ReplacementClass,
    ReplacementEffect,
)
from .component_registry import exact_fields
from .context import SemanticNodeError
from .zone_replacement_model import (
    ZoneChangeReplacementContext,
    ZoneChangeSubjectSnapshot,
    ZoneDestinationIntent,
)


SELF_ENTRY_COUNTER_HANDLER_ID = "replacement.zone.self-entry-counter.v1"


@dataclass(frozen=True, slots=True)
class SelfEntryCounterNode:
    counter_name: str
    amount: int
    optional: bool
    rule_id: str

    def __post_init__(self) -> None:
        if type(self.counter_name) is not str:
            raise SemanticNodeError("Self-entry counter name must be a string")
        name = " ".join(self.counter_name.casefold().split())
        if not name:
            raise SemanticNodeError("Self-entry counter name must be nonempty")
        if type(self.amount) is not int or self.amount < 1:
            raise SemanticNodeError(
                "Self-entry counter amount must be a positive integer"
            )
        if type(self.optional) is not bool:
            raise SemanticNodeError("Self-entry counter optional must be boolean")
        if type(self.rule_id) is not str or not self.rule_id.strip():
            raise SemanticNodeError("Self-entry counter requires rule identity")
        object.__setattr__(self, "counter_name", name)


@dataclass(frozen=True, slots=True)
class SelfEntryCounterHandler:
    handler_id: str = SELF_ENTRY_COUNTER_HANDLER_ID
    schema_version: int = 1
    family: str = "replacement.zone.self-entry-counter"
    event: str = "zone.change"
    rule_references: tuple[str, ...] = (
        "122.6",
        "614.1c",
        "614.12",
        "614.16",
        "616.1",
        "702.98a",
    )
    capability_dependencies: tuple[str, ...] = (
        "counter.producer.optional_self_entry",
    )

    def validate(self, descriptor: Mapping[str, Any]) -> SelfEntryCounterNode:
        exact_fields(
            descriptor,
            {
                "handler_id",
                "schema_version",
                "event",
                "counter_name",
                "amount",
                "optional",
                "rule_id",
            },
            field="self-entry counter handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Self-entry counter handler identity changed")
        if descriptor["schema_version"] != self.schema_version:
            raise SemanticNodeError("Unsupported self-entry counter schema version")
        if descriptor["event"] != self.event:
            raise SemanticNodeError("Self-entry counter must handle zone changes")
        return SelfEntryCounterNode(
            counter_name=descriptor["counter_name"],
            amount=descriptor["amount"],
            optional=descriptor["optional"],
            rule_id=descriptor["rule_id"],
        )

    def lower(
        self,
        descriptor: Mapping[str, Any],
        context: ZoneChangeReplacementContext,
    ) -> tuple[ZoneDestinationIntent, ...]:
        self.validate(descriptor)
        return ()

    def subject_replacement_effect(
        self,
        descriptor: Mapping[str, Any],
        *,
        subject: ZoneChangeSubjectSnapshot,
        component_id: str,
    ) -> ReplacementEffect:
        node = self.validate(descriptor)
        if subject.destination_controller is None:
            raise SemanticNodeError(
                "Battlefield self-entry counters require a destination controller"
            )
        if not component_id:
            raise SemanticNodeError(
                "Self-entry counters require stable component identity"
            )
        return ReplacementEffect(
            effect_id=f"{self.handler_id}:{subject.object_ref}:{component_id}",
            source_id=subject.object_ref,
            event_kind=self.event,
            replacement_class=ReplacementClass.OTHER,
            conditions={
                "destination": {"eq": "battlefield"},
                "object_ref": {"eq": subject.object_ref},
            },
            operations=(
                CreateAffectedObjectCounter(
                    counter_name=node.counter_name,
                    amount=node.amount,
                    placing_player=subject.destination_controller,
                    source_ref=subject.object_ref,
                    sequence=0,
                ),
            ),
            optional=node.optional,
            label=(
                f"{subject.object_ref}: enter with {node.amount} "
                f"{node.counter_name} counter(s)"
            ),
        )


__all__ = [
    "SELF_ENTRY_COUNTER_HANDLER_ID",
    "SelfEntryCounterHandler",
    "SelfEntryCounterNode",
]
