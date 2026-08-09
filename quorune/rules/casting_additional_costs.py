from __future__ import annotations

"""Typed nonmana casting-cost descriptors and candidate queries."""

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any, Protocol

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


def _unbound_creature_you_control_query() -> ObjectQuerySpec:
    return ObjectQuerySpec(
        zones=("battlefield",),
        controller="$actor",
        types_all=("creature",),
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


def fixed_counter_additional_cost(
    value: Mapping[str, Any],
) -> FixedCounterPlacementAdditionalCost | None:
    if not isinstance(value, Mapping):
        raise AdditionalCostError("Additional costs must be objects")
    if value.get("kind") != "counter_placement":
        return None
    return FixedCounterPlacementAdditionalCost.from_descriptor(value)


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


__all__ = [
    "AdditionalCostError",
    "AdditionalCostQueryHost",
    "FixedCounterPlacementAdditionalCost",
    "fixed_counter_additional_cost",
    "fixed_counter_cost_candidates",
]
