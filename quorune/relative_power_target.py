from __future__ import annotations

"""Immutable relative-power target restrictions.

The model pins the public last-known power of a source while allowing the
targeting adapter to supply that source's current power when the same logical
object is still present.  It contains no game-state access or Oracle text.
"""

from dataclasses import dataclass, replace
from typing import Any, Mapping, Protocol, Sequence


class RelativePowerTargetError(ValueError):
    """A relative-power target condition is malformed."""


class RelativePowerDepartureHost(Protocol):
    state: Any

    def _numeric_stat(self, object_id: str, stat: str) -> int: ...


def _identity(value: Any, *, field: str) -> str:
    if type(value) is not str or not value:
        raise RelativePowerTargetError(f"{field} must be a nonempty string")
    return value


@dataclass(frozen=True, slots=True)
class RelativePowerSourceSnapshot:
    object_id: str
    logical_object_id: str
    reference: str
    last_known_power: int

    def __post_init__(self) -> None:
        _identity(self.object_id, field="Relative-power source object ID")
        _identity(
            self.logical_object_id,
            field="Relative-power source logical identity",
        )
        _identity(self.reference, field="Relative-power source reference")
        if type(self.last_known_power) is not int:
            raise RelativePowerTargetError(
                "Relative-power source power must be an exact integer"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "logical_object_id": self.logical_object_id,
            "reference": self.reference,
            "last_known_power": self.last_known_power,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "RelativePowerSourceSnapshot":
        expected = {
            "object_id",
            "logical_object_id",
            "reference",
            "last_known_power",
        }
        if not isinstance(value, Mapping) or set(value) != expected:
            raise RelativePowerTargetError(
                "Relative-power source snapshots have a closed schema"
            )
        return cls(**dict(value))


@dataclass(frozen=True, slots=True)
class RelativePowerDepartureSnapshot:
    object_id: str
    logical_object_id: str
    last_known_power: int

    def __post_init__(self) -> None:
        _identity(self.object_id, field="Departing source object ID")
        _identity(
            self.logical_object_id,
            field="Departing source logical identity",
        )
        if type(self.last_known_power) is not int:
            raise RelativePowerTargetError(
                "Departing source power must be an exact integer"
            )


@dataclass(frozen=True, slots=True)
class RelativePowerTargetCondition:
    source: RelativePowerSourceSnapshot
    schema_version: int = 1
    kind: str = "power_less_than_source"

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise RelativePowerTargetError(
                "Unsupported relative-power target schema version"
            )
        if self.kind != "power_less_than_source":
            raise RelativePowerTargetError(
                "Unsupported relative-power target condition"
            )
        if not isinstance(self.source, RelativePowerSourceSnapshot):
            raise RelativePowerTargetError(
                "Relative-power conditions require a typed source snapshot"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "source": self.source.to_dict(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "RelativePowerTargetCondition":
        expected = {"schema_version", "kind", "source"}
        if not isinstance(value, Mapping) or set(value) != expected:
            raise RelativePowerTargetError(
                "Relative-power target conditions have a closed schema"
            )
        source = value["source"]
        if not isinstance(source, Mapping):
            raise RelativePowerTargetError(
                "Relative-power target source must be an object"
            )
        return cls(
            schema_version=value["schema_version"],
            kind=value["kind"],
            source=RelativePowerSourceSnapshot.from_dict(source),
        )

    def permits(
        self,
        *,
        target_power: int,
        current_source_power: int | None,
    ) -> bool:
        if type(target_power) is not int or (
            current_source_power is not None
            and type(current_source_power) is not int
        ):
            raise RelativePowerTargetError(
                "Relative-power comparisons require exact integer power"
            )
        source_power = (
            self.source.last_known_power
            if current_source_power is None
            else current_source_power
        )
        return target_power < source_power


def relative_power_source_identities(
    stack_items: Sequence[Any],
) -> frozenset[tuple[str, str]]:
    """Return source incarnations used by pending relative-power targets."""

    identities: set[tuple[str, str]] = set()
    for item in stack_items:
        context = getattr(item, "context", None)
        if not isinstance(context, Mapping):
            continue
        schema = context.get("target_schema_override")
        if not isinstance(schema, Mapping):
            continue
        groups = schema.get("groups")
        if not isinstance(groups, (list, tuple)):
            continue
        for group in groups:
            if not isinstance(group, Mapping) or group.get("predicate") != (
                "power_less_than_source"
            ):
                continue
            condition = RelativePowerTargetCondition.from_dict(
                group.get("resolution_condition")
            )
            identities.add(
                (
                    condition.source.object_id,
                    condition.source.logical_object_id,
                )
            )
    return frozenset(identities)


def pin_relative_power_source_departures(
    stack_items: Sequence[Any],
    departures: Sequence[RelativePowerDepartureSnapshot],
) -> int:
    """Pin immediate predeparture power into matching pending target schemas."""

    values = tuple(departures)
    if any(
        not isinstance(value, RelativePowerDepartureSnapshot)
        for value in values
    ):
        raise RelativePowerTargetError(
            "Relative-power departures require typed snapshots"
        )
    by_identity = {
        (value.object_id, value.logical_object_id): value for value in values
    }
    if len(by_identity) != len(values):
        raise RelativePowerTargetError(
            "Relative-power departure identities must be unique"
        )
    updated_items = 0
    for item in stack_items:
        context = getattr(item, "context", None)
        if not isinstance(context, Mapping):
            continue
        schema = context.get("target_schema_override")
        if not isinstance(schema, Mapping):
            continue
        groups = schema.get("groups")
        if not isinstance(groups, (list, tuple)):
            continue
        updated_groups: list[Any] = []
        changed = False
        for raw_group in groups:
            if not isinstance(raw_group, Mapping) or raw_group.get(
                "predicate"
            ) != "power_less_than_source":
                updated_groups.append(raw_group)
                continue
            condition = RelativePowerTargetCondition.from_dict(
                raw_group.get("resolution_condition")
            )
            departure = by_identity.get(
                (
                    condition.source.object_id,
                    condition.source.logical_object_id,
                )
            )
            if departure is None:
                updated_groups.append(raw_group)
                continue
            updated_condition = replace(
                condition,
                source=replace(
                    condition.source,
                    last_known_power=departure.last_known_power,
                ),
            )
            updated_groups.append(
                {
                    **dict(raw_group),
                    "resolution_condition": updated_condition.to_dict(),
                }
            )
            changed = True
        if not changed:
            continue
        item.context = {
            **dict(context),
            "target_schema_override": {
                **dict(schema),
                "groups": updated_groups,
            },
        }
        updated_items += 1
    return updated_items


def pin_host_relative_power_source_departures(
    host: RelativePowerDepartureHost,
    cards: Sequence[Any],
) -> int:
    """Capture all relevant current powers before a host mutates any card."""

    identities = relative_power_source_identities(host.state.stack)
    departures = tuple(
        RelativePowerDepartureSnapshot(
            object_id=card.object_id,
            logical_object_id=card.logical_object_id,
            last_known_power=host._numeric_stat(card.object_id, "power"),
        )
        for card in cards
        if getattr(card, "zone", None) == "battlefield"
        and (card.object_id, card.logical_object_id) in identities
    )
    return pin_relative_power_source_departures(
        host.state.stack,
        departures,
    )


__all__ = [
    "RelativePowerDepartureSnapshot",
    "RelativePowerDepartureHost",
    "RelativePowerSourceSnapshot",
    "RelativePowerTargetCondition",
    "RelativePowerTargetError",
    "pin_relative_power_source_departures",
    "pin_host_relative_power_source_departures",
    "relative_power_source_identities",
]
