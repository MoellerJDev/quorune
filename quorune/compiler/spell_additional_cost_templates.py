from __future__ import annotations

"""Closed Oracle grammar for reusable spell additional costs."""

from dataclasses import dataclass
import re
from typing import Any, Mapping

from ..object_predicate import ObjectQuerySpec
from .fixed_numbers import FIXED_COUNT_PATTERN, fixed_number


_COUNTER_NAME = (
    r"[+-]\d+/[+-]\d+|"
    r"[A-Za-z][A-Za-z'-]*(?: [A-Za-z][A-Za-z'-]*){0,2}"
)
_FIXED_COUNTER_COST = re.compile(
    rf"As an additional cost to cast this spell, put "
    rf"(?P<count>{FIXED_COUNT_PATTERN}) (?P<counter>{_COUNTER_NAME}) "
    r"(?P<plural>counter|counters) on a creature you control\.?",
    re.IGNORECASE,
)


def _creature_you_control_query() -> ObjectQuerySpec:
    return ObjectQuerySpec(
        zones=("battlefield",),
        controller="$actor",
        types_all=("creature",),
        known_to_actor=True,
    )


@dataclass(frozen=True, slots=True)
class FixedCounterAdditionalCostTemplate:
    """One mandatory fixed counter placement paid while casting a spell."""

    amount: int
    counter_name: str

    def __post_init__(self) -> None:
        normalized = " ".join(self.counter_name.casefold().split())
        if type(self.amount) is not int or self.amount <= 0:
            raise ValueError("Counter additional-cost amount must be positive")
        if not normalized or re.fullmatch(_COUNTER_NAME, normalized) is None:
            raise ValueError("Counter additional-cost name is unsupported")
        object.__setattr__(self, "counter_name", normalized)

    @property
    def template_id(self) -> str:
        return "spell-additional-cost-fixed-counter-creature-you-control-v1"

    @property
    def descriptor(self) -> Mapping[str, Any]:
        return {
            "schema_version": 1,
            "kind": "counter_placement",
            "counter": self.counter_name,
            "amount": self.amount,
            "choice_field": "counter_cost_card",
            "predicate": _creature_you_control_query().to_dict(),
        }

    @property
    def cost_schema(self) -> Mapping[str, Any]:
        return {"additional_costs": [dict(self.descriptor)]}


def fixed_counter_additional_cost_template(
    text: str,
) -> FixedCounterAdditionalCostTemplate | None:
    """Parse one exact mandatory creature-counter casting cost."""

    match = _FIXED_COUNTER_COST.fullmatch(text.strip())
    if match is None:
        return None
    amount = fixed_number(match.group("count"))
    if amount <= 0 or (match.group("plural").casefold() == "counter") != (
        amount == 1
    ):
        return None
    return FixedCounterAdditionalCostTemplate(
        amount=amount,
        counter_name=match.group("counter"),
    )


__all__ = [
    "FixedCounterAdditionalCostTemplate",
    "fixed_counter_additional_cost_template",
]
