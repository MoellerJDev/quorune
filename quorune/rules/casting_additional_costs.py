from __future__ import annotations

"""Typed nonmana casting-cost descriptors and candidate queries."""

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any, Protocol

from ..additional_cost_vocabulary import SACRIFICE_COST_KIND
from ..object_predicate import ObjectQuerySpec
from ..object_query import object_query_result, query_objects


class AdditionalCostError(ValueError):
    """A casting additional-cost descriptor or selection is malformed."""


class AdditionalCostQueryHost(Protocol):
    state: Any

    def _effective_card_data(self, card: Any) -> Mapping[str, Any]: ...

    def _type_parts(
        self, type_line: str
    ) -> tuple[set[str], set[str], set[str]]: ...


_FIXED_COUNTER_FIELDS = frozenset(
    {
        "schema_version",
        "kind",
        "counter",
        "amount",
        "choice_field",
        "predicate",
    }
)
_FIXED_SACRIFICE_FIELDS = frozenset(
    {
        "schema_version",
        "kind",
        "count",
        "choice_field",
        "predicate",
    }
)
_PERMANENT_CARD_TYPES = frozenset(
    {
        "artifact",
        "battle",
        "creature",
        "enchantment",
        "land",
        "planeswalker",
    }
)


def _unbound_creature_you_control_query() -> ObjectQuerySpec:
    return ObjectQuerySpec(
        zones=("battlefield",),
        controller="$actor",
        types_all=("creature",),
        known_to_actor=True,
    )


def _unbound_permanent_you_control_query(
    types_any: tuple[str, ...] = (),
) -> ObjectQuerySpec:
    return ObjectQuerySpec(
        zones=("battlefield",),
        controller="$actor",
        types_any=types_any,
        known_to_actor=True,
    )


@dataclass(frozen=True, slots=True)
class FixedCounterPlacementAdditionalCost:
    """Place fixed counters on one chosen controlled creature as a cost."""

    counter_name: str
    amount: int
    choice_field: str
    predicate: ObjectQuerySpec
    schema_version: int = 1
    kind: str = "counter_placement"

    def __post_init__(self) -> None:
        if type(self.counter_name) is not str:
            raise AdditionalCostError(
                "Counter additional costs require a counter name"
            )
        normalized = " ".join(self.counter_name.casefold().split())
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise AdditionalCostError(
                "Counter additional-cost schema version is unsupported"
            )
        if self.kind != "counter_placement":
            raise AdditionalCostError(
                "Counter additional-cost kind is unsupported"
            )
        if not normalized:
            raise AdditionalCostError(
                "Counter additional costs require a counter name"
            )
        if type(self.amount) is not int or self.amount <= 0:
            raise AdditionalCostError(
                "Counter additional-cost amount must be a positive integer"
            )
        if type(self.choice_field) is not str or (
            not self.choice_field
            or self.choice_field != self.choice_field.strip()
        ):
            raise AdditionalCostError(
                "Counter additional costs require a canonical choice field"
            )
        if not isinstance(self.predicate, ObjectQuerySpec):
            raise AdditionalCostError(
                "Counter additional costs require a typed object predicate"
            )
        if self.predicate != _unbound_creature_you_control_query():
            raise AdditionalCostError(
                "Counter additional-cost predicate is outside the closed family"
            )
        object.__setattr__(self, "counter_name", normalized)

    @classmethod
    def from_descriptor(
        cls, value: Mapping[str, Any]
    ) -> "FixedCounterPlacementAdditionalCost":
        if not isinstance(value, Mapping) or set(value) != _FIXED_COUNTER_FIELDS:
            raise AdditionalCostError(
                "Counter additional-cost descriptor fields are closed"
            )
        try:
            predicate = ObjectQuerySpec.from_dict(value["predicate"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AdditionalCostError(
                "Counter additional-cost predicate is malformed"
            ) from exc
        return cls(
            schema_version=value["schema_version"],
            kind=value["kind"],
            counter_name=value["counter"],
            amount=value["amount"],
            choice_field=value["choice_field"],
            predicate=predicate,
        )

    def to_descriptor(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "counter": self.counter_name,
            "amount": self.amount,
            "choice_field": self.choice_field,
            "predicate": self.predicate.to_dict(),
        }

    def bound_predicate(self, actor: str) -> ObjectQuerySpec:
        if type(actor) is not str or not actor:
            raise AdditionalCostError(
                "Counter additional-cost actor must be nonempty"
            )
        return replace(self.predicate, controller=actor)


@dataclass(frozen=True, slots=True)
class FixedSacrificeAdditionalCost:
    """Sacrifice exactly one controlled permanent matching a closed query."""

    choice_field: str
    predicate: ObjectQuerySpec
    schema_version: int = 1
    kind: str = SACRIFICE_COST_KIND
    count: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise AdditionalCostError(
                "Sacrifice additional-cost schema version is unsupported"
            )
        if self.kind != SACRIFICE_COST_KIND:
            raise AdditionalCostError(
                "Sacrifice additional-cost kind is unsupported"
            )
        if type(self.count) is not int or self.count != 1:
            raise AdditionalCostError(
                "Fixed sacrifice additional costs require exactly one object"
            )
        if self.choice_field != "sacrifice_cards":
            raise AdditionalCostError(
                "Sacrifice additional costs require the canonical choice field"
            )
        if not isinstance(self.predicate, ObjectQuerySpec):
            raise AdditionalCostError(
                "Sacrifice additional costs require a typed object predicate"
            )
        expected = _unbound_permanent_you_control_query(
            self.predicate.types_any
        )
        if self.predicate != expected:
            raise AdditionalCostError(
                "Sacrifice additional-cost predicate is outside the closed family"
            )
        if not set(self.predicate.types_any).issubset(_PERMANENT_CARD_TYPES):
            raise AdditionalCostError(
                "Sacrifice additional-cost types must be permanent card types"
            )
        if len(self.predicate.types_any) > 2:
            raise AdditionalCostError(
                "Sacrifice additional costs support at most two permanent types"
            )

    @classmethod
    def from_descriptor(
        cls, value: Mapping[str, Any]
    ) -> "FixedSacrificeAdditionalCost":
        if not isinstance(value, Mapping) or set(value) != _FIXED_SACRIFICE_FIELDS:
            raise AdditionalCostError(
                "Sacrifice additional-cost descriptor fields are closed"
            )
        try:
            predicate = ObjectQuerySpec.from_dict(value["predicate"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AdditionalCostError(
                "Sacrifice additional-cost predicate is malformed"
            ) from exc
        return cls(
            schema_version=value["schema_version"],
            kind=value["kind"],
            count=value["count"],
            choice_field=value["choice_field"],
            predicate=predicate,
        )

    def to_descriptor(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "count": self.count,
            "choice_field": self.choice_field,
            "predicate": self.predicate.to_dict(),
        }

    def bound_predicate(self, actor: str) -> ObjectQuerySpec:
        if type(actor) is not str or not actor:
            raise AdditionalCostError(
                "Sacrifice additional-cost actor must be nonempty"
            )
        return replace(self.predicate, controller=actor)


def fixed_counter_additional_cost(
    value: Mapping[str, Any],
) -> FixedCounterPlacementAdditionalCost | None:
    if not isinstance(value, Mapping):
        raise AdditionalCostError("Additional costs must be objects")
    if value.get("kind") != "counter_placement":
        return None
    return FixedCounterPlacementAdditionalCost.from_descriptor(value)


def fixed_sacrifice_additional_cost(
    value: Mapping[str, Any],
) -> FixedSacrificeAdditionalCost | None:
    if not isinstance(value, Mapping):
        raise AdditionalCostError("Additional costs must be objects")
    if (
        value.get("kind") != SACRIFICE_COST_KIND
        or "schema_version" not in value
    ):
        return None
    return FixedSacrificeAdditionalCost.from_descriptor(value)


def fixed_counter_cost_candidates(
    host: AdditionalCostQueryHost,
    *,
    actor: str,
    cost: FixedCounterPlacementAdditionalCost,
) -> tuple[str, ...]:
    """Return public candidate refs using effective characteristics."""

    rows = []
    for object_id in host.state.players[actor].zones["battlefield"]:
        card = host.state.cards[object_id]
        effective = host._effective_card_data(card)
        rows.append(
            object_query_result(
                card,
                effective,
                type_parts=host._type_parts(
                    str(effective.get("type_line") or "")
                ),
                known_to_actor=True,
                attached_to_ref=None,
            )
        )
    return tuple(
        row.ref
        for row in query_objects(rows, cost.bound_predicate(actor))
    )


def fixed_sacrifice_cost_candidates(
    host: AdditionalCostQueryHost,
    *,
    actor: str,
    cost: FixedSacrificeAdditionalCost,
) -> tuple[str, ...]:
    """Return controlled sacrifice candidates using effective characteristics."""

    rows = []
    for object_id in host.state.players[actor].zones["battlefield"]:
        card = host.state.cards[object_id]
        effective = host._effective_card_data(card)
        rows.append(
            object_query_result(
                card,
                effective,
                type_parts=host._type_parts(
                    str(effective.get("type_line") or "")
                ),
                known_to_actor=True,
                attached_to_ref=None,
            )
        )
    return tuple(
        row.ref
        for row in query_objects(rows, cost.bound_predicate(actor))
    )


__all__ = [
    "AdditionalCostError",
    "AdditionalCostQueryHost",
    "FixedCounterPlacementAdditionalCost",
    "FixedSacrificeAdditionalCost",
    "fixed_counter_additional_cost",
    "fixed_counter_cost_candidates",
    "fixed_sacrifice_additional_cost",
    "fixed_sacrifice_cost_candidates",
]
