from __future__ import annotations

"""Typed ordinary Mentor occurrences and stack projection."""

from dataclasses import dataclass
import hashlib
from typing import Any, Mapping, Sequence

from .ability_fragments import CombatKeywordTriggerKind
from .attack_transition_model import (
    AttackObjectIdentity,
    AttackTransitionError,
    AttackTransitionEvent,
)
from .model import StackItem
from .relative_power_target import (
    RelativePowerSourceSnapshot,
    RelativePowerTargetCondition,
)
from .util import stable_json


MENTOR_TRIGGER_SEMANTIC_KEY = "builtin:mentor-trigger"
_ATTACKING_FIELD = "attacking"


def _identity(value: Any, *, field: str) -> str:
    if type(value) is not str or not value:
        raise AttackTransitionError(f"{field} must be a nonempty string")
    return value


def _payload(
    *,
    transition_id: str,
    controller: str,
    source: AttackObjectIdentity,
    source_power: int,
    instance_index: int,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "transition_id": transition_id,
        "controller": controller,
        "source": source.to_dict(),
        "source_power": source_power,
        "instance_index": instance_index,
    }


def _occurrence_id(payload: Mapping[str, Any]) -> str:
    return "mentor-trigger:" + hashlib.sha256(
        stable_json(payload).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class MentorTriggerOccurrence:
    occurrence_id: str
    transition_id: str
    controller: str
    source: AttackObjectIdentity
    source_power: int
    instance_index: int
    schema_version: int = 1

    def __post_init__(self) -> None:
        _identity(self.occurrence_id, field="Mentor occurrence identity")
        _identity(self.transition_id, field="Mentor transition identity")
        _identity(self.controller, field="Mentor controller")
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise AttackTransitionError(
                "Unsupported Mentor occurrence schema version"
            )
        if not isinstance(self.source, AttackObjectIdentity):
            raise AttackTransitionError(
                "Mentor occurrences require a typed source identity"
            )
        if type(self.source_power) is not int:
            raise AttackTransitionError(
                "Mentor source power must be an exact integer"
            )
        if type(self.instance_index) is not int or self.instance_index < 0:
            raise AttackTransitionError(
                "Mentor instance index must be a nonnegative exact integer"
            )
        payload = _payload(
            transition_id=self.transition_id,
            controller=self.controller,
            source=self.source,
            source_power=self.source_power,
            instance_index=self.instance_index,
        )
        if self.occurrence_id != _occurrence_id(payload):
            raise AttackTransitionError(
                "Mentor occurrence identity does not match its contents"
            )

    @property
    def label(self) -> str:
        return f"{self.source.reference} — Mentor"

    @property
    def target_condition(self) -> RelativePowerTargetCondition:
        return RelativePowerTargetCondition(
            source=RelativePowerSourceSnapshot(
                object_id=self.source.object_id,
                logical_object_id=self.source.logical_object_id,
                reference=self.source.reference,
                last_known_power=self.source_power,
            )
        )

    @property
    def target_schema(self) -> dict[str, Any]:
        return {
            "groups": [
                {
                    "id": "mentored_creature",
                    "zones": ["battlefield"],
                    "categories": ["permanent"],
                    "types_any": ["creature"],
                    _ATTACKING_FIELD: True,
                    "count": 1,
                    "predicate": "power_less_than_source",
                    "resolution_condition": self.target_condition.to_dict(),
                }
            ]
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **_payload(
                transition_id=self.transition_id,
                controller=self.controller,
                source=self.source,
                source_power=self.source_power,
                instance_index=self.instance_index,
            ),
            "occurrence_id": self.occurrence_id,
        }

    @classmethod
    def create(
        cls,
        *,
        transition_id: str,
        controller: str,
        source: AttackObjectIdentity,
        source_power: int,
        instance_index: int,
    ) -> "MentorTriggerOccurrence":
        payload = _payload(
            transition_id=transition_id,
            controller=controller,
            source=source,
            source_power=source_power,
            instance_index=instance_index,
        )
        return cls(
            occurrence_id=_occurrence_id(payload),
            transition_id=transition_id,
            controller=controller,
            source=source,
            source_power=source_power,
            instance_index=instance_index,
        )

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "MentorTriggerOccurrence":
        expected = {
            "schema_version",
            "occurrence_id",
            "transition_id",
            "controller",
            "source",
            "source_power",
            "instance_index",
        }
        if not isinstance(value, Mapping) or set(value) != expected:
            raise AttackTransitionError(
                "Mentor trigger occurrences have a closed field set"
            )
        source = value["source"]
        if not isinstance(source, Mapping):
            raise AttackTransitionError("Mentor source must be an object")
        return cls(
            schema_version=value["schema_version"],
            occurrence_id=value["occurrence_id"],
            transition_id=value["transition_id"],
            controller=value["controller"],
            source=AttackObjectIdentity.from_dict(source),
            source_power=value["source_power"],
            instance_index=value["instance_index"],
        )


def derive_mentor_trigger_occurrences(
    event: AttackTransitionEvent,
) -> tuple[MentorTriggerOccurrence, ...]:
    if not isinstance(event, AttackTransitionEvent):
        raise AttackTransitionError(
            "Mentor triggers require a typed attack transition"
        )
    participants = {value.object_id: value for value in event.participants}
    attackers = tuple(
        participants[value.attacker_object_id] for value in event.assignments
    )
    occurrences = []
    for source in attackers:
        mentor_specs = tuple(
            value
            for value in source.trigger_specs
            if value.kind is CombatKeywordTriggerKind.MENTOR
        )
        if mentor_specs and source.power is None:
            raise AttackTransitionError(
                "A Mentor source requires captured effective power"
            )
        occurrences.extend(
            MentorTriggerOccurrence.create(
                transition_id=event.transition_id,
                controller=source.controller,
                source=source.identity,
                source_power=source.power,
                instance_index=index,
            )
            for index, _spec in enumerate(mentor_specs)
        )
    return tuple(
        sorted(
            occurrences,
            key=lambda value: (
                value.source.reference,
                value.source.object_id,
                value.instance_index,
            ),
        )
    )


def mentor_trigger_stack_item(
    occurrence: MentorTriggerOccurrence,
    *,
    ref: str,
    stack_id: str,
    visibility: Sequence[str],
) -> StackItem:
    if not isinstance(occurrence, MentorTriggerOccurrence):
        raise AttackTransitionError(
            "A Mentor stack item requires a typed occurrence"
        )
    _identity(ref, field="Mentor stack reference")
    _identity(stack_id, field="Mentor stack identity")
    return StackItem(
        stack_id=stack_id,
        ref=ref,
        kind="triggered_ability",
        controller=occurrence.controller,
        label=occurrence.label,
        source_object_id=occurrence.source.object_id,
        semantic_key=MENTOR_TRIGGER_SEMANTIC_KEY,
        visibility=list(visibility),
        context={
            "event": "combat.attack_transition",
            "mentor_trigger": occurrence.to_dict(),
            "target_schema_override": occurrence.target_schema,
            "trigger_target_selection_pending": True,
        },
        referred_object_ids=[occurrence.source.object_id],
    )


def mentor_counter_effect() -> dict[str, Any]:
    return {
        "op": "place_counters",
        "card": "$target.0",
        "counter": "+1/+1",
        "amount": 1,
        "source": "$source",
    }


__all__ = [
    "MENTOR_TRIGGER_SEMANTIC_KEY",
    "MentorTriggerOccurrence",
    "derive_mentor_trigger_occurrences",
    "mentor_counter_effect",
    "mentor_trigger_stack_item",
]
