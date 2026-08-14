from __future__ import annotations

"""Typed cast-payment entry-counter replacement for Sunburst."""

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


SUNBURST_MECHANIC_ID = "sunburst"
SUNBURST_LABEL = SUNBURST_MECHANIC_ID.title()
SUNBURST_HANDLER_ID = "replacement.zone.sunburst.v1"
SUNBURST_CREATURE_COUNTER = "+1/+1"
SUNBURST_NONCREATURE_COUNTER = "charge"


class SunburstError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class SunburstSpec:
    """One printed CR 702.44a keyword instance."""

    counter_name: str

    def __post_init__(self) -> None:
        if self.counter_name not in {
            SUNBURST_CREATURE_COUNTER,
            SUNBURST_NONCREATURE_COUNTER,
        }:
            raise SunburstError(
                "Sunburst requires its printed creature or noncreature counter"
            )

    @classmethod
    def for_printed_types(cls, card_types: tuple[str, ...]) -> "SunburstSpec":
        if any(type(value) is not str or not value for value in card_types):
            raise SunburstError(
                "Sunburst printed card types must be canonical strings"
            )
        return cls(
            SUNBURST_CREATURE_COUNTER
            if "creature" in card_types
            else SUNBURST_NONCREATURE_COUNTER
        )

    def handler_descriptor(self) -> dict[str, Any]:
        return {
            "handler_id": SUNBURST_HANDLER_ID,
            "schema_version": 1,
            "event": "zone.change",
            "counter_name": self.counter_name,
            "rule_id": "702.44a",
        }


@dataclass(frozen=True, slots=True)
class SunburstNode:
    counter_name: str
    rule_id: str

    def __post_init__(self) -> None:
        if self.counter_name not in {
            SUNBURST_CREATURE_COUNTER,
            SUNBURST_NONCREATURE_COUNTER,
        }:
            raise SemanticNodeError(
                "Sunburst requires a typed +1/+1 or charge counter"
            )
        if type(self.rule_id) is not str or not self.rule_id.strip():
            raise SemanticNodeError("Sunburst requires rule identity")


@dataclass(frozen=True, slots=True)
class SunburstEntryCounterHandler:
    handler_id: str = SUNBURST_HANDLER_ID
    schema_version: int = 1
    family: str = "replacement.zone.sunburst"
    event: str = "zone.change"
    rule_references: tuple[str, ...] = (
        "122.1a",
        "122.6",
        "614.1c",
        "614.12",
        "614.16",
        "616.1",
        "702.44a",
        "702.44b",
        "702.44c",
        "702.44d",
    )
    capability_dependencies: tuple[str, ...] = (
        "counter.producer.sunburst",
    )

    def validate(self, descriptor: Mapping[str, Any]) -> SunburstNode:
        exact_fields(
            descriptor,
            {
                "handler_id",
                "schema_version",
                "event",
                "counter_name",
                "rule_id",
            },
            field="Sunburst handler",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Sunburst handler identity changed")
        if descriptor["schema_version"] != self.schema_version:
            raise SemanticNodeError("Unsupported Sunburst schema version")
        if descriptor["event"] != self.event:
            raise SemanticNodeError("Sunburst must handle zone changes")
        return SunburstNode(
            counter_name=descriptor["counter_name"],
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
    ) -> ReplacementEffect | None:
        node = self.validate(descriptor)
        if (
            subject.origin != "stack"
            or subject.destination != "battlefield"
            or not subject.mana_colors_spent
        ):
            return None
        if subject.destination_controller is None:
            raise SemanticNodeError(
                "Sunburst battlefield entry requires a controller"
            )
        if not component_id:
            raise SemanticNodeError(
                "Sunburst requires stable component identity"
            )
        amount = len(subject.mana_colors_spent)
        return ReplacementEffect(
            effect_id=f"{self.handler_id}:{subject.object_ref}:{component_id}",
            source_id=subject.object_ref,
            event_kind=self.event,
            replacement_class=ReplacementClass.OTHER,
            conditions={
                "origin": {"eq": "stack"},
                "destination": {"eq": "battlefield"},
                "object_ref": {"eq": subject.object_ref},
            },
            operations=(
                CreateAffectedObjectCounter(
                    counter_name=node.counter_name,
                    amount=amount,
                    placing_player=subject.destination_controller,
                    source_ref=subject.object_ref,
                    sequence=0,
                ),
            ),
            label=(
                f"{subject.object_ref}: enter with {amount} "
                f"{node.counter_name} counter(s) from Sunburst"
            ),
        )


__all__ = [
    "SUNBURST_CREATURE_COUNTER",
    "SUNBURST_HANDLER_ID",
    "SUNBURST_LABEL",
    "SUNBURST_MECHANIC_ID",
    "SUNBURST_NONCREATURE_COUNTER",
    "SunburstEntryCounterHandler",
    "SunburstError",
    "SunburstNode",
    "SunburstSpec",
]
