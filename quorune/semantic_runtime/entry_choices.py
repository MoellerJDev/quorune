from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..replacement_effects import (
    CreateAffectedObjectCounter,
    GrantAffectedObjectKeyword,
    ReplacementClass,
    ReplacementEffect,
)
from ..riot import RIOT_ENTRY_HANDLER_ID
from .component_registry import exact_fields
from .context import SemanticNodeError
from .zone_replacement_model import (
    ZoneChangeReplacementContext,
    ZoneChangeSubjectSnapshot,
    ZoneDestinationIntent,
)


@dataclass(frozen=True, slots=True)
class RiotEntryChoiceNode:
    counter_name: str
    amount: int
    alternative_keyword: str
    rule_id: str

    def __post_init__(self) -> None:
        if type(self.counter_name) is not str:
            raise SemanticNodeError("Riot counter name must be a string")
        counter_name = " ".join(self.counter_name.casefold().split())
        if not counter_name:
            raise SemanticNodeError("Riot requires a counter name")
        if type(self.amount) is not int or self.amount < 1:
            raise SemanticNodeError(
                "Riot counter amount must be a positive integer"
            )
        if type(self.alternative_keyword) is not str:
            raise SemanticNodeError("Riot alternative keyword must be a string")
        alternative_keyword = " ".join(
            self.alternative_keyword.casefold().split()
        )
        if alternative_keyword != "haste":
            raise SemanticNodeError(
                "Riot alternative is outside the represented keyword vocabulary"
            )
        if type(self.rule_id) is not str or not self.rule_id.strip():
            raise SemanticNodeError("Riot requires rule identity")
        object.__setattr__(self, "counter_name", counter_name)
        object.__setattr__(self, "alternative_keyword", alternative_keyword)


@dataclass(frozen=True, slots=True)
class RiotEntryChoiceHandler:
    handler_id: str = RIOT_ENTRY_HANDLER_ID
    schema_version: int = 1
    family: str = "replacement.zone.riot-entry-choice"
    event: str = "zone.change"
    rule_references: tuple[str, ...] = (
        "122.6",
        "614.1c",
        "614.12",
        "614.16",
        "616.1",
        "702.10",
        "702.136a",
        "702.136b",
    )
    capability_dependencies: tuple[str, ...] = ("counter.producer.riot",)

    def validate(self, descriptor: Mapping[str, Any]) -> RiotEntryChoiceNode:
        exact_fields(
            descriptor,
            {
                "handler_id",
                "schema_version",
                "event",
                "counter_name",
                "amount",
                "alternative_keyword",
                "rule_id",
            },
            field="Riot entry choice",
        )
        if descriptor["handler_id"] != self.handler_id:
            raise SemanticNodeError("Riot entry handler identity changed")
        if descriptor["schema_version"] != self.schema_version:
            raise SemanticNodeError("Unsupported Riot entry schema version")
        if descriptor["event"] != self.event:
            raise SemanticNodeError("Riot must handle a zone change")
        return RiotEntryChoiceNode(
            counter_name=descriptor["counter_name"],
            amount=descriptor["amount"],
            alternative_keyword=descriptor["alternative_keyword"],
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
                "Riot battlefield entry requires a destination controller"
            )
        if not component_id:
            raise SemanticNodeError("Riot requires stable component identity")
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
            decline_operations=(
                GrantAffectedObjectKeyword(
                    keyword=node.alternative_keyword,
                    sequence=0,
                ),
            ),
            optional=True,
            label=(
                f"{subject.object_ref}: enter with {node.amount} "
                f"{node.counter_name} counter(s); otherwise gain haste"
            ),
        )


__all__ = ["RiotEntryChoiceHandler", "RiotEntryChoiceNode"]
