from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Any, Mapping, TypeAlias

from .util import stable_json


class TriggerParticipationError(ValueError):
    """A compiled static trigger-participation value is malformed."""


class TriggerMultiplierPredicate(str, Enum):
    """Closed represented CR 603.2d participation predicates."""

    ARTIFACT_OR_CREATURE_ENTERS = "artifact_or_creature_enters"
    ANOTHER_CREATURE_OF_CHOSEN_TYPE = "another_creature_of_chosen_type"


_MULTIPLIER_CAPABILITIES = {
    TriggerMultiplierPredicate.ARTIFACT_OR_CREATURE_ENTERS: (
        "trigger.multiplier.artifact_or_creature_enters"
    ),
    TriggerMultiplierPredicate.ANOTHER_CREATURE_OF_CHOSEN_TYPE: (
        "trigger.multiplier.another_creature_of_chosen_type"
    ),
}


def _nonempty(value: Any, *, field: str) -> str:
    if type(value) is not str or not value.strip():
        raise TriggerParticipationError(f"{field} must be a nonempty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class TriggerMultiplierSpec:
    """One typed static effect that makes a represented ability trigger again."""

    predicate: TriggerMultiplierPredicate
    additional_count: int = 1
    exclude_self: bool = False
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise TriggerParticipationError(
                "Unsupported trigger-multiplier schema version"
            )
        if not isinstance(self.predicate, TriggerMultiplierPredicate):
            raise TriggerParticipationError(
                "Unsupported trigger-multiplier predicate"
            )
        if type(self.additional_count) is not int or self.additional_count <= 0:
            raise TriggerParticipationError(
                "Trigger-multiplier additional_count must be positive"
            )
        if type(self.exclude_self) is not bool:
            raise TriggerParticipationError(
                "Trigger-multiplier exclude_self must be a boolean"
            )
        required_exclusion = (
            self.predicate
            is TriggerMultiplierPredicate.ANOTHER_CREATURE_OF_CHOSEN_TYPE
        )
        if self.exclude_self is not required_exclusion:
            raise TriggerParticipationError(
                "Trigger-multiplier self exclusion disagrees with its predicate"
            )

    @property
    def capability_id(self) -> str:
        return _MULTIPLIER_CAPABILITIES[self.predicate]

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return ("603.2d",)

    @property
    def requires_chosen_creature_type(self) -> bool:
        return (
            self.predicate
            is TriggerMultiplierPredicate.ANOTHER_CREATURE_OF_CHOSEN_TYPE
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "predicate": self.predicate.value,
            "additional_count": self.additional_count,
            "exclude_self": self.exclude_self,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TriggerMultiplierSpec":
        expected = {
            "schema_version",
            "predicate",
            "additional_count",
            "exclude_self",
        }
        if not isinstance(value, Mapping) or set(value) != expected:
            raise TriggerParticipationError(
                "Trigger-multiplier fragments have a closed schema"
            )
        try:
            predicate = TriggerMultiplierPredicate(value["predicate"])
        except (TypeError, ValueError) as exc:
            raise TriggerParticipationError(
                "Unsupported trigger-multiplier predicate"
            ) from exc
        return cls(
            schema_version=value["schema_version"],
            predicate=predicate,
            additional_count=value["additional_count"],
            exclude_self=value["exclude_self"],
        )


@dataclass(frozen=True, slots=True)
class WardSpec:
    """One represented fixed-generic Ward ability (CR 702.21)."""

    generic_cost: int
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise TriggerParticipationError("Unsupported Ward schema version")
        if type(self.generic_cost) is not int or self.generic_cost < 0:
            raise TriggerParticipationError(
                "Ward generic_cost must be a nonnegative integer"
            )

    @property
    def capability_id(self) -> str:
        return "trigger.keyword.ward.fixed_generic"

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return ("603.3", "702.21", "702.21a")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generic_cost": self.generic_cost,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "WardSpec":
        if not isinstance(value, Mapping) or set(value) != {
            "schema_version",
            "generic_cost",
        }:
            raise TriggerParticipationError(
                "Ward fragments have a closed schema"
            )
        return cls(
            schema_version=value["schema_version"],
            generic_cost=value["generic_cost"],
        )


StaticTriggerParticipationSpec: TypeAlias = TriggerMultiplierSpec | WardSpec


@dataclass(frozen=True, slots=True)
class StaticTriggerParticipation:
    """Effective battlefield participation snapshot for a static trigger rule.

    This is deliberately separate from the compiled fragment.  It freezes the
    physical object, current logical incarnation, controller, chosen value,
    and effective ability presence used by one trigger-discovery transaction.
    """

    source_object_id: str
    source_logical_object_id: str
    source_controller: str
    active_zone: str
    spec: StaticTriggerParticipationSpec
    chosen_creature_type: str | None = None
    effective_ability_present: bool = True
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise TriggerParticipationError(
                "Unsupported static trigger-participation schema version"
            )
        for field in (
            "source_object_id",
            "source_logical_object_id",
            "source_controller",
            "active_zone",
        ):
            object.__setattr__(
                self,
                field,
                _nonempty(getattr(self, field), field=field),
            )
        if self.active_zone != "battlefield":
            raise TriggerParticipationError(
                "Static trigger participation is battlefield-only"
            )
        if not isinstance(self.spec, (TriggerMultiplierSpec, WardSpec)):
            raise TriggerParticipationError(
                "Unsupported static trigger-participation spec"
            )
        if type(self.effective_ability_present) is not bool:
            raise TriggerParticipationError(
                "effective_ability_present must be a boolean"
            )
        chosen = self.chosen_creature_type
        if chosen is not None:
            chosen = _nonempty(chosen, field="chosen_creature_type").casefold()
            object.__setattr__(self, "chosen_creature_type", chosen)
        requires_choice = (
            isinstance(self.spec, TriggerMultiplierSpec)
            and self.spec.requires_chosen_creature_type
        )
        if requires_choice is not bool(chosen):
            raise TriggerParticipationError(
                "Chosen creature type presence disagrees with the static spec"
            )
        if isinstance(self.spec, WardSpec) and chosen is not None:
            raise TriggerParticipationError(
                "Ward participation cannot carry a chosen creature type"
            )

    @property
    def capability_id(self) -> str:
        return self.spec.capability_id

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return self.spec.rule_ids

    def to_dict(self) -> dict[str, Any]:
        kind = "trigger_multiplier" if isinstance(
            self.spec, TriggerMultiplierSpec
        ) else "ward"
        return {
            "schema_version": self.schema_version,
            "source_object_id": self.source_object_id,
            "source_logical_object_id": self.source_logical_object_id,
            "source_controller": self.source_controller,
            "active_zone": self.active_zone,
            "spec": {"kind": kind, "value": self.spec.to_dict()},
            "chosen_creature_type": self.chosen_creature_type,
            "effective_ability_present": self.effective_ability_present,
            "capability_id": self.capability_id,
            "rule_ids": list(self.rule_ids),
        }

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            stable_json(self.to_dict()).encode("utf-8")
        ).hexdigest()


__all__ = [
    "StaticTriggerParticipation",
    "StaticTriggerParticipationSpec",
    "TriggerMultiplierPredicate",
    "TriggerMultiplierSpec",
    "TriggerParticipationError",
    "WardSpec",
]
