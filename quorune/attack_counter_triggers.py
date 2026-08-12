from __future__ import annotations

"""Typed declaration-time Dethrone and Training counter triggers."""

from dataclasses import dataclass
import hashlib
from typing import Any, Mapping, Sequence

from .ability_fragments import CombatKeywordTriggerKind
from .attack_transition_model import (
    AttackObjectIdentity,
    AttackRecipientKind,
    AttackTransitionError,
    AttackTransitionEvent,
    AttackTransitionParticipant,
)
from .model import StackItem
from .util import stable_json


ATTACK_COUNTER_TRIGGER_SEMANTIC_KEY = "builtin:attack-counter-trigger"
_LIFE_FIELD = "life"
ATTACK_COUNTER_TRIGGER_KINDS = frozenset(
    {
        CombatKeywordTriggerKind.DETHRONE,
        CombatKeywordTriggerKind.TRAINING,
    }
)


def _identity(value: Any, *, field: str) -> str:
    if type(value) is not str or not value:
        raise AttackTransitionError(f"{field} must be a nonempty string")
    return value


def _integer(value: Any, *, field: str, minimum: int | None = None) -> int:
    if type(value) is not int or (minimum is not None and value < minimum):
        suffix = "" if minimum is None else f" no less than {minimum}"
        raise AttackTransitionError(
            f"{field} must be an exact integer{suffix}"
        )
    return value


def _exact_mapping(
    value: Any,
    expected: set[str],
    *,
    field: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise AttackTransitionError(f"{field} has a closed field set")
    return value


@dataclass(frozen=True, slots=True)
class PlayerLifeTotal:
    player: str
    life: int

    def __post_init__(self) -> None:
        _identity(self.player, field="Attack life-total player")
        _integer(self.life, field="Attack life total")

    def to_dict(self) -> dict[str, Any]:
        return {"player": self.player, _LIFE_FIELD: self.life}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "PlayerLifeTotal":
        return cls(
            **dict(
                _exact_mapping(
                    value,
                    {"player", _LIFE_FIELD},
                    field="Attack player life total",
                )
            )
        )


@dataclass(frozen=True, slots=True)
class AttackPlayerLifeSnapshot:
    """Complete public life totals for the players still in the game."""

    totals: tuple[PlayerLifeTotal, ...]
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise AttackTransitionError(
                "Unsupported attack player-life snapshot schema version"
            )
        totals = tuple(self.totals)
        if not totals or any(
            not isinstance(value, PlayerLifeTotal) for value in totals
        ):
            raise AttackTransitionError(
                "Attack player-life snapshots require typed totals"
            )
        if len(totals) != len({value.player for value in totals}):
            raise AttackTransitionError(
                "Attack player-life snapshot players must be unique"
            )
        object.__setattr__(
            self,
            "totals",
            tuple(sorted(totals, key=lambda value: value.player)),
        )

    @property
    def maximum_life(self) -> int:
        return max(value.life for value in self.totals)

    def life_for(self, player: str) -> int:
        for value in self.totals:
            if value.player == player:
                return value.life
        raise AttackTransitionError(
            "Attack player-life snapshot omitted a referenced player"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "totals": [value.to_dict() for value in self.totals],
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "AttackPlayerLifeSnapshot":
        data = _exact_mapping(
            value,
            {"schema_version", "totals"},
            field="Attack player-life snapshot",
        )
        raw_totals = data["totals"]
        if not isinstance(raw_totals, (list, tuple)):
            raise AttackTransitionError(
                "Attack player-life snapshot totals must be an array"
            )
        if any(not isinstance(item, Mapping) for item in raw_totals):
            raise AttackTransitionError(
                "Attack player-life snapshot totals must contain objects"
            )
        return cls(
            schema_version=data["schema_version"],
            totals=tuple(PlayerLifeTotal.from_dict(item) for item in raw_totals),
        )


@dataclass(frozen=True, slots=True)
class DethroneQualification:
    attacked_player: str
    player_life: AttackPlayerLifeSnapshot
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise AttackTransitionError(
                "Unsupported Dethrone qualification schema version"
            )
        _identity(self.attacked_player, field="Dethrone attacked player")
        if not isinstance(self.player_life, AttackPlayerLifeSnapshot):
            raise AttackTransitionError(
                "Dethrone requires a typed player-life snapshot"
            )
        if self.player_life.life_for(self.attacked_player) != (
            self.player_life.maximum_life
        ):
            raise AttackTransitionError(
                "Dethrone qualification requires a player tied for most life"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": CombatKeywordTriggerKind.DETHRONE.value,
            "attacked_player": self.attacked_player,
            "player_life": self.player_life.to_dict(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "DethroneQualification":
        data = _exact_mapping(
            value,
            {"schema_version", "kind", "attacked_player", "player_life"},
            field="Dethrone qualification",
        )
        if data["kind"] != CombatKeywordTriggerKind.DETHRONE.value:
            raise AttackTransitionError(
                "Dethrone qualification kind is invalid"
            )
        raw_life = data["player_life"]
        if not isinstance(raw_life, Mapping):
            raise AttackTransitionError(
                "Dethrone player-life snapshot must be an object"
            )
        return cls(
            schema_version=data["schema_version"],
            attacked_player=data["attacked_player"],
            player_life=AttackPlayerLifeSnapshot.from_dict(raw_life),
        )


@dataclass(frozen=True, slots=True)
class AttackerPowerSnapshot:
    attacker: AttackObjectIdentity
    power: int

    def __post_init__(self) -> None:
        if not isinstance(self.attacker, AttackObjectIdentity):
            raise AttackTransitionError(
                "Training attacker power requires a typed identity"
            )
        _integer(self.power, field="Training attacker power")

    def to_dict(self) -> dict[str, Any]:
        return {"attacker": self.attacker.to_dict(), "power": self.power}

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "AttackerPowerSnapshot":
        data = _exact_mapping(
            value,
            {"attacker", "power"},
            field="Training attacker power",
        )
        raw_attacker = data["attacker"]
        if not isinstance(raw_attacker, Mapping):
            raise AttackTransitionError(
                "Training attacker identity must be an object"
            )
        return cls(
            attacker=AttackObjectIdentity.from_dict(raw_attacker),
            power=data["power"],
        )


@dataclass(frozen=True, slots=True)
class TrainingQualification:
    source: AttackObjectIdentity
    attacker_powers: tuple[AttackerPowerSnapshot, ...]
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise AttackTransitionError(
                "Unsupported Training qualification schema version"
            )
        if not isinstance(self.source, AttackObjectIdentity):
            raise AttackTransitionError(
                "Training qualification requires a typed source"
            )
        values = tuple(self.attacker_powers)
        if len(values) < 2 or any(
            not isinstance(value, AttackerPowerSnapshot) for value in values
        ):
            raise AttackTransitionError(
                "Training qualification requires at least two typed attackers"
            )
        object_ids = [value.attacker.object_id for value in values]
        if len(object_ids) != len(set(object_ids)):
            raise AttackTransitionError(
                "Training attacker-power identities must be unique"
            )
        canonical = tuple(
            sorted(
                values,
                key=lambda value: (
                    value.attacker.reference,
                    value.attacker.object_id,
                ),
            )
        )
        object.__setattr__(self, "attacker_powers", canonical)
        by_id = {value.attacker.object_id: value for value in canonical}
        source = by_id.get(self.source.object_id)
        if source is None or source.attacker != self.source:
            raise AttackTransitionError(
                "Training qualification source must be one declared attacker"
            )
        if not any(
            value.attacker.object_id != self.source.object_id
            and value.power > source.power
            for value in canonical
        ):
            raise AttackTransitionError(
                "Training requires another attacker with greater power"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": CombatKeywordTriggerKind.TRAINING.value,
            "source": self.source.to_dict(),
            "attacker_powers": [
                value.to_dict() for value in self.attacker_powers
            ],
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "TrainingQualification":
        data = _exact_mapping(
            value,
            {"schema_version", "kind", "source", "attacker_powers"},
            field="Training qualification",
        )
        if data["kind"] != CombatKeywordTriggerKind.TRAINING.value:
            raise AttackTransitionError(
                "Training qualification kind is invalid"
            )
        raw_powers = data["attacker_powers"]
        if not isinstance(raw_powers, (list, tuple)):
            raise AttackTransitionError(
                "Training attacker powers must be an array"
            )
        raw_source = data["source"]
        if not isinstance(raw_source, Mapping):
            raise AttackTransitionError(
                "Training source identity must be an object"
            )
        if any(not isinstance(item, Mapping) for item in raw_powers):
            raise AttackTransitionError(
                "Training attacker powers must contain objects"
            )
        return cls(
            schema_version=data["schema_version"],
            source=AttackObjectIdentity.from_dict(raw_source),
            attacker_powers=tuple(
                AttackerPowerSnapshot.from_dict(item) for item in raw_powers
            ),
        )


AttackCounterQualification = DethroneQualification | TrainingQualification


def _occurrence_payload(
    *,
    transition_id: str,
    kind: CombatKeywordTriggerKind,
    controller: str,
    source: AttackObjectIdentity,
    qualification: AttackCounterQualification,
    instance_index: int,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "transition_id": transition_id,
        "kind": kind.value,
        "controller": controller,
        "source": source.to_dict(),
        "qualification": qualification.to_dict(),
        "instance_index": instance_index,
    }


def _occurrence_id(payload: Mapping[str, Any]) -> str:
    return "attack-counter-trigger:" + hashlib.sha256(
        stable_json(payload).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class AttackCounterTriggerOccurrence:
    occurrence_id: str
    transition_id: str
    kind: CombatKeywordTriggerKind
    controller: str
    source: AttackObjectIdentity
    qualification: AttackCounterQualification
    instance_index: int
    schema_version: int = 1

    def __post_init__(self) -> None:
        _identity(self.occurrence_id, field="Attack-counter occurrence identity")
        _identity(self.transition_id, field="Attack-counter transition identity")
        _identity(self.controller, field="Attack-counter trigger controller")
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise AttackTransitionError(
                "Unsupported attack-counter occurrence schema version"
            )
        if self.kind not in ATTACK_COUNTER_TRIGGER_KINDS:
            raise AttackTransitionError(
                "Unsupported attack-counter trigger kind"
            )
        if not isinstance(self.source, AttackObjectIdentity):
            raise AttackTransitionError(
                "Attack-counter triggers require a typed source identity"
            )
        expected_type = (
            DethroneQualification
            if self.kind is CombatKeywordTriggerKind.DETHRONE
            else TrainingQualification
        )
        if not isinstance(self.qualification, expected_type):
            raise AttackTransitionError(
                "Attack-counter trigger kind and qualification do not match"
            )
        if (
            isinstance(self.qualification, TrainingQualification)
            and self.qualification.source != self.source
        ):
            raise AttackTransitionError(
                "Training occurrence source does not match its qualification"
            )
        _integer(
            self.instance_index,
            field="Attack-counter trigger instance index",
            minimum=0,
        )
        payload = _occurrence_payload(
            transition_id=self.transition_id,
            kind=self.kind,
            controller=self.controller,
            source=self.source,
            qualification=self.qualification,
            instance_index=self.instance_index,
        )
        if self.occurrence_id != _occurrence_id(payload):
            raise AttackTransitionError(
                "Attack-counter occurrence identity does not match its contents"
            )

    @property
    def label(self) -> str:
        name = (
            "Dethrone"
            if self.kind is CombatKeywordTriggerKind.DETHRONE
            else "Training"
        )
        return f"{self.source.reference} — {name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            **_occurrence_payload(
                transition_id=self.transition_id,
                kind=self.kind,
                controller=self.controller,
                source=self.source,
                qualification=self.qualification,
                instance_index=self.instance_index,
            ),
            "occurrence_id": self.occurrence_id,
        }

    @classmethod
    def create(
        cls,
        *,
        transition_id: str,
        kind: CombatKeywordTriggerKind,
        controller: str,
        source: AttackObjectIdentity,
        qualification: AttackCounterQualification,
        instance_index: int,
    ) -> "AttackCounterTriggerOccurrence":
        payload = _occurrence_payload(
            transition_id=transition_id,
            kind=kind,
            controller=controller,
            source=source,
            qualification=qualification,
            instance_index=instance_index,
        )
        return cls(
            occurrence_id=_occurrence_id(payload),
            transition_id=transition_id,
            kind=kind,
            controller=controller,
            source=source,
            qualification=qualification,
            instance_index=instance_index,
        )

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "AttackCounterTriggerOccurrence":
        data = _exact_mapping(
            value,
            {
                "schema_version",
                "occurrence_id",
                "transition_id",
                "kind",
                "controller",
                "source",
                "qualification",
                "instance_index",
            },
            field="Attack-counter trigger occurrence",
        )
        try:
            kind = CombatKeywordTriggerKind(data["kind"])
        except (TypeError, ValueError) as exc:
            raise AttackTransitionError(
                "Unsupported attack-counter trigger kind"
            ) from exc
        raw_qualification = data["qualification"]
        if not isinstance(raw_qualification, Mapping):
            raise AttackTransitionError(
                "Attack-counter qualification must be an object"
            )
        raw_source = data["source"]
        if not isinstance(raw_source, Mapping):
            raise AttackTransitionError(
                "Attack-counter source identity must be an object"
            )
        qualification = (
            DethroneQualification.from_dict(raw_qualification)
            if kind is CombatKeywordTriggerKind.DETHRONE
            else TrainingQualification.from_dict(raw_qualification)
            if kind is CombatKeywordTriggerKind.TRAINING
            else None
        )
        if qualification is None:
            raise AttackTransitionError(
                "Unsupported attack-counter trigger kind"
            )
        return cls(
            schema_version=data["schema_version"],
            occurrence_id=data["occurrence_id"],
            transition_id=data["transition_id"],
            kind=kind,
            controller=data["controller"],
            source=AttackObjectIdentity.from_dict(raw_source),
            qualification=qualification,
            instance_index=data["instance_index"],
        )


def derive_attack_counter_trigger_occurrences(
    event: AttackTransitionEvent,
    player_life: AttackPlayerLifeSnapshot,
) -> tuple[AttackCounterTriggerOccurrence, ...]:
    """Derive qualified Dethrone and Training triggers from one declaration."""

    if not isinstance(event, AttackTransitionEvent):
        raise AttackTransitionError(
            "Attack-counter triggers require a typed attack transition"
        )
    if not isinstance(player_life, AttackPlayerLifeSnapshot):
        raise AttackTransitionError(
            "Attack-counter triggers require a typed player-life snapshot"
        )
    participants = {value.object_id: value for value in event.participants}
    assignment_by_attacker = {
        value.attacker_object_id: value for value in event.assignments
    }
    attackers = tuple(
        participants[value.attacker_object_id] for value in event.assignments
    )
    life_players = {value.player for value in player_life.totals}
    if event.active_player not in life_players or any(
        assignment.recipient.defending_player not in life_players
        for assignment in event.assignments
    ):
        raise AttackTransitionError(
            "Attack player-life snapshot must cover every represented player"
        )
    has_training = any(
        spec.kind is CombatKeywordTriggerKind.TRAINING
        for source in attackers
        for spec in source.trigger_specs
    )
    if has_training and any(source.power is None for source in attackers):
        raise AttackTransitionError(
            "Training requires captured effective power for every attacker"
        )
    training_powers: tuple[AttackerPowerSnapshot, ...] = ()
    if has_training:
        power_values = []
        for source in attackers:
            if source.power is None:
                raise AttackTransitionError(
                    "Training requires captured effective power for every "
                    "attacker"
                )
            power_values.append(
                AttackerPowerSnapshot(source.identity, source.power)
            )
        training_powers = tuple(power_values)
    drafts: list[
        tuple[
            CombatKeywordTriggerKind,
            AttackTransitionParticipant,
            AttackCounterQualification,
            int,
        ]
    ] = []
    for source in attackers:
        assignment = assignment_by_attacker[source.object_id]
        dethrone_specs = tuple(
            spec
            for spec in source.trigger_specs
            if spec.kind is CombatKeywordTriggerKind.DETHRONE
        )
        if (
            dethrone_specs
            and assignment.recipient.kind is AttackRecipientKind.PLAYER
            and player_life.life_for(assignment.recipient.reference)
            == player_life.maximum_life
        ):
            qualification = DethroneQualification(
                attacked_player=assignment.recipient.reference,
                player_life=player_life,
            )
            drafts.extend(
                (
                    CombatKeywordTriggerKind.DETHRONE,
                    source,
                    qualification,
                    index,
                )
                for index, _spec in enumerate(dethrone_specs)
            )

        training_specs = tuple(
            spec
            for spec in source.trigger_specs
            if spec.kind is CombatKeywordTriggerKind.TRAINING
        )
        if training_specs:
            source_power = source.power
            if source_power is None:
                raise AttackTransitionError(
                    "Training source power is absent from the declaration "
                    "snapshot"
                )
            if any(
                other.object_id != source.object_id
                and other.power is not None
                and other.power > source_power
                for other in attackers
            ):
                qualification = TrainingQualification(
                    source=source.identity,
                    attacker_powers=training_powers,
                )
                drafts.extend(
                    (
                        CombatKeywordTriggerKind.TRAINING,
                        source,
                        qualification,
                        index,
                    )
                    for index, _spec in enumerate(training_specs)
                )
    drafts.sort(
        key=lambda value: (
            value[1].reference,
            value[0].value,
            value[3],
        )
    )
    return tuple(
        AttackCounterTriggerOccurrence.create(
            transition_id=event.transition_id,
            kind=kind,
            controller=source.controller,
            source=source.identity,
            qualification=qualification,
            instance_index=index,
        )
        for kind, source, qualification, index in drafts
    )


def attack_counter_trigger_stack_item(
    occurrence: AttackCounterTriggerOccurrence,
    *,
    ref: str,
    stack_id: str,
    visibility: Sequence[str],
) -> StackItem:
    if not isinstance(occurrence, AttackCounterTriggerOccurrence):
        raise AttackTransitionError(
            "An attack-counter stack item requires a typed occurrence"
        )
    _identity(ref, field="Attack-counter stack reference")
    _identity(stack_id, field="Attack-counter stack identity")
    return StackItem(
        stack_id=stack_id,
        ref=ref,
        kind="triggered_ability",
        controller=occurrence.controller,
        label=occurrence.label,
        source_object_id=occurrence.source.object_id,
        semantic_key=ATTACK_COUNTER_TRIGGER_SEMANTIC_KEY,
        visibility=list(visibility),
        context={
            "event": "combat.attack_transition",
            "attack_counter_trigger": occurrence.to_dict(),
            "source_logical_object_id": occurrence.source.logical_object_id,
        },
        referred_object_ids=[occurrence.source.object_id],
    )


def attack_counter_effect(object_ref: str) -> dict[str, Any]:
    """One ordinary self-counter result routed through the shared owner."""

    _identity(object_ref, field="Attack-counter result object reference")
    return {
        "op": "place_counters",
        "card": object_ref,
        "counter": "+1/+1",
        "amount": 1,
        "source": "$source",
    }


__all__ = [
    "ATTACK_COUNTER_TRIGGER_KINDS",
    "ATTACK_COUNTER_TRIGGER_SEMANTIC_KEY",
    "AttackCounterTriggerOccurrence",
    "AttackPlayerLifeSnapshot",
    "AttackerPowerSnapshot",
    "DethroneQualification",
    "PlayerLifeTotal",
    "TrainingQualification",
    "attack_counter_effect",
    "attack_counter_trigger_stack_item",
    "derive_attack_counter_trigger_occurrences",
]
