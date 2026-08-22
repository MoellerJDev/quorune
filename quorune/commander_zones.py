from __future__ import annotations

"""Typed CR 903.9 commander movement boundaries."""

from dataclasses import dataclass
from typing import Any, Iterable, Protocol

from .replacement_effects import ReplacementClass, ReplacementEffect


COMMANDER_ZONE_REPLACEMENT_CAPABILITY = "variant.commander.zone_return"
COMMANDER_ZONE_REPLACEMENT_EFFECT_PREFIX = "rule.commander-zone-replacement"


class CommanderZoneError(ValueError):
    """A commander zone replacement or state action is malformed."""


class CommanderZoneCard(Protocol):
    object_id: str
    logical_object_id: str
    ref: str
    owner: str
    zone: str
    is_commander: bool
    commander_designation_id: str | None
    commander_zone_choice_logical_id: str | None


class CommanderZoneSubject(Protocol):
    object_id: str
    object_ref: str
    logical_object_id: str
    owner: str
    destination: str
    is_commander: bool
    commander_designation_id: str | None


@dataclass(frozen=True, slots=True)
class CommanderZoneStateChoice:
    object_id: str
    logical_object_id: str
    ref: str
    owner: str
    zone: str
    designation_id: str

    def __post_init__(self) -> None:
        if any(
            type(value) is not str or not value
            for value in (
                self.object_id,
                self.logical_object_id,
                self.ref,
                self.owner,
                self.zone,
                self.designation_id,
            )
        ):
            raise CommanderZoneError(
                "Commander zone choices require complete public identity"
            )
        if self.zone not in {"graveyard", "exile"}:
            raise CommanderZoneError(
                "Commander state choices originate in graveyard or exile"
            )

    def to_dict(self) -> dict[str, str]:
        return {
            "object_id": self.object_id,
            "logical_object_id": self.logical_object_id,
            "ref": self.ref,
            "owner": self.owner,
            "zone": self.zone,
            "designation_id": self.designation_id,
        }

    @classmethod
    def from_dict(cls, value: Any) -> "CommanderZoneStateChoice":
        if not isinstance(value, dict) or set(value) != {
            "object_id",
            "logical_object_id",
            "ref",
            "owner",
            "zone",
            "designation_id",
        }:
            raise CommanderZoneError(
                "Commander zone choice fields are incomplete or unknown"
            )
        return cls(**value)


def pending_commander_zone_state_choices(
    cards: Iterable[CommanderZoneCard],
    *,
    active_seats: Iterable[str],
    apnap_order: Iterable[str],
) -> tuple[CommanderZoneStateChoice, ...]:
    """Return unchecked CR 903.9a candidates in deterministic APNAP order."""

    active = tuple(active_seats)
    order = tuple(apnap_order)
    if (
        len(active) != len(set(active))
        or len(order) != len(active)
        or set(order) != set(active)
    ):
        raise CommanderZoneError(
            "Commander zone choices require a complete APNAP view"
        )
    index = {seat: position for position, seat in enumerate(order)}
    result: list[CommanderZoneStateChoice] = []
    for card in cards:
        if (
            not card.is_commander
            or card.zone not in {"graveyard", "exile"}
            or card.owner not in index
            or card.commander_zone_choice_logical_id == card.logical_object_id
        ):
            continue
        designation = str(card.commander_designation_id or "")
        if not designation:
            raise CommanderZoneError(
                "Current commander movement requires designation identity"
            )
        result.append(
            CommanderZoneStateChoice(
                object_id=card.object_id,
                logical_object_id=card.logical_object_id,
                ref=card.ref,
                owner=card.owner,
                zone=card.zone,
                designation_id=designation,
            )
        )
    return tuple(
        sorted(
            result,
            key=lambda value: (
                index[value.owner],
                value.designation_id,
                value.logical_object_id,
                value.object_id,
            ),
        )
    )


def commander_hand_library_replacement_effect(
    subject: CommanderZoneSubject,
) -> ReplacementEffect | None:
    """Return CR 903.9b's owner-optional command-zone replacement."""

    if not subject.is_commander or subject.destination not in {"hand", "library"}:
        return None
    designation = str(subject.commander_designation_id or "")
    if not designation:
        raise CommanderZoneError(
            "Current commander replacement requires designation identity"
        )
    return ReplacementEffect(
        effect_id=(
            f"{COMMANDER_ZONE_REPLACEMENT_EFFECT_PREFIX}:"
            f"{designation}:{subject.logical_object_id}"
        ),
        source_id=f"rule:903.9b:{designation}",
        event_kind="zone.change",
        replacement_class=ReplacementClass.OTHER,
        conditions={
            "object_ref": {"eq": subject.object_ref},
            "logical_object_id": {"eq": subject.logical_object_id},
            "destination": {"in": ["hand", "library"]},
        },
        operations=(
            {"op": "set", "field": "destination", "value": "command"},
        ),
        optional=True,
        label=(
            f"{subject.owner}: put commander {subject.object_ref} into the "
            "command zone instead"
        ),
    )


def commit_commander_zone_choice_decline(
    card: CommanderZoneCard,
    choice: CommanderZoneStateChoice,
) -> None:
    """Mark exactly one unchanged graveyard/exile incarnation as checked."""

    if (
        not isinstance(choice, CommanderZoneStateChoice)
        or not card.is_commander
        or card.object_id != choice.object_id
        or card.logical_object_id != choice.logical_object_id
        or card.ref != choice.ref
        or card.owner != choice.owner
        or card.zone != choice.zone
        or card.commander_designation_id != choice.designation_id
    ):
        raise CommanderZoneError(
            "Commander zone decline no longer matches that incarnation"
        )
    card.commander_zone_choice_logical_id = card.logical_object_id


__all__ = [
    "commander_hand_library_replacement_effect",
    "commit_commander_zone_choice_decline",
    "CommanderZoneError",
    "CommanderZoneStateChoice",
    "COMMANDER_ZONE_REPLACEMENT_CAPABILITY",
    "COMMANDER_ZONE_REPLACEMENT_EFFECT_PREFIX",
    "pending_commander_zone_state_choices",
]
