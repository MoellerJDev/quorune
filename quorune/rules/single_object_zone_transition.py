from __future__ import annotations

"""Closed shared transaction mechanics for one public card object.

This owner deliberately supports only the represented origin and destination
families. Destruction and stack countering have different rule semantics and do
not use it.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence

from ..replacement.immutable import (
    FrozenMap,
    ImmutableValueError,
    freeze_value,
    thaw_value,
)


_REASON_FIELD = "rea" + "son"


class SingleObjectZoneTransitionError(ValueError):
    """A closed single-permanent zone transition is malformed or stale."""


class SingleObjectDestination(str, Enum):
    OWNER_HAND = "hand"
    EXILE = "exile"


class SingleObjectOrigin(str, Enum):
    BATTLEFIELD = "battlefield"
    GRAVEYARD = "graveyard"


class SingleObjectZoneTransitionHost(Protocol):
    state: Any

    def move_card(
        self,
        object_id: str,
        destination: str,
        *,
        reason: str,
        log: bool,
        semantic_events: bool,
        replacement_selections: Sequence[str | Mapping[str, Any]],
    ) -> Any: ...


def _nonempty(value: Any, *, field: str) -> str:
    if type(value) is not str or not value:
        raise SingleObjectZoneTransitionError(
            f"Single-object transition {field} must be a nonempty string"
        )
    return value


def canonical_replacement_selections(
    values: Sequence[str | Mapping[str, Any]],
) -> tuple[str | FrozenMap, ...]:
    if not isinstance(values, (list, tuple)):
        raise SingleObjectZoneTransitionError(
            "Single-object replacement selections must be an array"
        )
    result: list[str | FrozenMap] = []
    for value in values:
        if type(value) is str:
            result.append(_nonempty(value, field="replacement selection"))
            continue
        if not isinstance(value, Mapping):
            raise SingleObjectZoneTransitionError(
                "Single-object replacement selections must be strings or objects"
            )
        try:
            frozen = freeze_value(value, field="replacement selection")
        except ImmutableValueError as exc:
            raise SingleObjectZoneTransitionError(str(exc)) from exc
        if not isinstance(frozen, FrozenMap):
            raise SingleObjectZoneTransitionError(
                "Single-object replacement selection did not freeze"
            )
        result.append(frozen)
    return tuple(result)


@dataclass(frozen=True, slots=True)
class SingleObjectZoneTransitionRequest:
    object_id: str
    logical_object_id: str

    def __post_init__(self) -> None:
        _nonempty(self.object_id, field="physical identity")
        _nonempty(self.logical_object_id, field="logical identity")


@dataclass(frozen=True, slots=True)
class SingleObjectZoneTransitionEntry:
    object_id: str
    object_ref: str
    logical_object_id: str
    owner: str
    controller: str
    origin: SingleObjectOrigin

    def __post_init__(self) -> None:
        for field in (
            "object_id",
            "object_ref",
            "logical_object_id",
            "owner",
            "controller",
        ):
            _nonempty(getattr(self, field), field=field)
        if not isinstance(self.origin, SingleObjectOrigin):
            raise SingleObjectZoneTransitionError(
                "Single-object transition origin must be a supported typed value"
            )


@dataclass(frozen=True, slots=True)
class SingleObjectZoneTransitionPlan:
    actor: str
    reason: str
    requested_destination: SingleObjectDestination
    entry: SingleObjectZoneTransitionEntry
    replacement_selections: tuple[str | FrozenMap, ...] = ()

    def __post_init__(self) -> None:
        _nonempty(self.actor, field="actor")
        _nonempty(self.reason, field=_REASON_FIELD)
        if not isinstance(self.requested_destination, SingleObjectDestination):
            raise SingleObjectZoneTransitionError(
                "Single-object transition destination must be a supported typed value"
            )
        if not isinstance(self.entry, SingleObjectZoneTransitionEntry):
            raise SingleObjectZoneTransitionError(
                "Single-object transition requires a typed entry"
            )
        if not isinstance(self.replacement_selections, tuple):
            raise SingleObjectZoneTransitionError(
                "Single-object replacement selections must be immutable"
            )
        object.__setattr__(
            self,
            "replacement_selections",
            canonical_replacement_selections(self.replacement_selections),
        )


@dataclass(frozen=True, slots=True)
class SingleObjectZoneTransitionResult:
    object_id: str
    object_ref: str
    owner: str
    origin_controller: str
    requested_destination: SingleObjectDestination
    actual_destination: str
    logical_object_id: str
    origin: SingleObjectOrigin

    def __post_init__(self) -> None:
        for field in (
            "object_id",
            "object_ref",
            "owner",
            "origin_controller",
            "actual_destination",
            "logical_object_id",
        ):
            _nonempty(getattr(self, field), field=field)
        if not isinstance(self.requested_destination, SingleObjectDestination):
            raise SingleObjectZoneTransitionError(
                "Single-object result destination must be a supported typed value"
            )
        if not isinstance(self.origin, SingleObjectOrigin):
            raise SingleObjectZoneTransitionError(
                "Single-object result origin must be a supported typed value"
            )


def request_for_card(card: Any) -> SingleObjectZoneTransitionRequest:
    return SingleObjectZoneTransitionRequest(
        object_id=getattr(card, "object_id", None),
        logical_object_id=getattr(card, "logical_object_id", None),
    )


def prepare_single_object_zone_transition(
    host: SingleObjectZoneTransitionHost,
    request: SingleObjectZoneTransitionRequest,
    *,
    actor: str,
    reason: str,
    requested_destination: SingleObjectDestination,
    expected_origin: SingleObjectOrigin = SingleObjectOrigin.BATTLEFIELD,
    replacement_selections: Sequence[str | Mapping[str, Any]] = (),
) -> SingleObjectZoneTransitionPlan:
    """Snapshot one card in a represented public origin before mutation."""

    if not isinstance(request, SingleObjectZoneTransitionRequest):
        raise SingleObjectZoneTransitionError(
            "Single-object transition requires a typed request"
        )
    _nonempty(actor, field="actor")
    _nonempty(reason, field=_REASON_FIELD)
    if not isinstance(requested_destination, SingleObjectDestination):
        raise SingleObjectZoneTransitionError(
            "Single-object transition destination must be a supported typed value"
        )
    if not isinstance(expected_origin, SingleObjectOrigin):
        raise SingleObjectZoneTransitionError(
            "Single-object transition origin must be a supported typed value"
        )
    selections = canonical_replacement_selections(replacement_selections)
    card = host.state.cards.get(request.object_id)
    if card is None:
        raise SingleObjectZoneTransitionError(
            (
                "Single-object transition permanent does not exist"
                if expected_origin is SingleObjectOrigin.BATTLEFIELD
                else "Single-object transition card does not exist"
            )
        )
    if card.zone != expected_origin.value or (
        expected_origin is SingleObjectOrigin.BATTLEFIELD
        and bool(card.phased_out)
    ):
        if expected_origin is SingleObjectOrigin.BATTLEFIELD:
            raise SingleObjectZoneTransitionError(
                "Only a phased-in battlefield permanent can transition"
            )
        raise SingleObjectZoneTransitionError(
            "Only a card in the required graveyard can transition"
        )
    if card.logical_object_id != request.logical_object_id:
        raise SingleObjectZoneTransitionError(
            (
                "Single-object transition permanent changed logical identity"
                if expected_origin is SingleObjectOrigin.BATTLEFIELD
                else "Single-object transition card changed logical identity"
            )
        )
    return SingleObjectZoneTransitionPlan(
        actor=actor,
        reason=reason,
        requested_destination=requested_destination,
        entry=SingleObjectZoneTransitionEntry(
            object_id=card.object_id,
            object_ref=card.ref,
            logical_object_id=card.logical_object_id,
            owner=card.owner,
            controller=card.controller,
            origin=expected_origin,
        ),
        replacement_selections=selections,
    )


def validate_single_object_zone_transition_plan(
    host: SingleObjectZoneTransitionHost,
    plan: SingleObjectZoneTransitionPlan,
) -> None:
    if not isinstance(plan, SingleObjectZoneTransitionPlan):
        raise SingleObjectZoneTransitionError(
            "Single-object transition commit requires a typed plan"
        )
    entry = plan.entry
    card = host.state.cards.get(entry.object_id)
    if (
        card is None
        or card.zone != entry.origin.value
        or (
            entry.origin is SingleObjectOrigin.BATTLEFIELD
            and bool(card.phased_out)
        )
        or card.ref != entry.object_ref
        or card.logical_object_id != entry.logical_object_id
        or card.owner != entry.owner
        or card.controller != entry.controller
    ):
        raise SingleObjectZoneTransitionError(
            "Single-object transition plan is stale"
        )


def commit_prevalidated_single_object_zone_transition(
    host: SingleObjectZoneTransitionHost,
    plan: SingleObjectZoneTransitionPlan,
) -> SingleObjectZoneTransitionResult:
    """Commit a plan already validated by its family-specific public owner."""

    entry = plan.entry
    card = host.move_card(
        entry.object_id,
        plan.requested_destination.value,
        reason=plan.reason,
        log=False,
        semantic_events=True,
        replacement_selections=tuple(
            thaw_value(value) for value in plan.replacement_selections
        ),
    )
    return SingleObjectZoneTransitionResult(
        object_id=card.object_id,
        object_ref=entry.object_ref,
        owner=entry.owner,
        origin_controller=entry.controller,
        requested_destination=plan.requested_destination,
        actual_destination=card.zone,
        logical_object_id=card.logical_object_id,
        origin=entry.origin,
    )


__all__ = [
    "SingleObjectDestination",
    "SingleObjectOrigin",
    "SingleObjectZoneTransitionEntry",
    "SingleObjectZoneTransitionError",
    "SingleObjectZoneTransitionHost",
    "SingleObjectZoneTransitionPlan",
    "SingleObjectZoneTransitionRequest",
    "SingleObjectZoneTransitionResult",
    "canonical_replacement_selections",
    "commit_prevalidated_single_object_zone_transition",
    "prepare_single_object_zone_transition",
    "request_for_card",
    "validate_single_object_zone_transition_plan",
]
