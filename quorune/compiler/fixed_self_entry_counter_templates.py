from __future__ import annotations

"""Closed Oracle lowering for mandatory fixed self-entry counters."""

from dataclasses import dataclass
import re
from typing import Any, Mapping

from ..keyword_counters import keyword_counter_mechanic
from ..rules.source_references import (
    SourceReferenceSpec,
    source_self_permanent_type,
)
from .counter_placement_templates import FIXED_COUNTER_NAME_PATTERN
from .fixed_numbers import FIXED_COUNT_PATTERN, fixed_number


FIXED_SELF_ENTRY_COUNTER_CAPABILITY = "counter.producer.fixed_self_entry"
FIXED_SELF_ENTRY_COUNTER_TEMPLATE = "fixed-self-entry-counter-v1"
_ENTRY = re.compile(
    rf"^(?P<subject>.+?) enters with "
    rf"(?P<count>an|{FIXED_COUNT_PATTERN}) "
    rf"(?P<counter>{FIXED_COUNTER_NAME_PATTERN}) "
    r"(?P<plural>counter|counters) on it\.?$",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class FixedSelfEntryCounterTemplate:
    counter_name: str
    amount: int

    def __post_init__(self) -> None:
        name = " ".join(str(self.counter_name).casefold().split())
        if not name:
            raise ValueError("Self-entry counter name must be nonempty")
        if type(self.amount) is not int or not 1 <= self.amount <= 10:
            raise ValueError("Self-entry counter amount must be from 1 through 10")
        object.__setattr__(self, "counter_name", name)

    @property
    def capabilities(self) -> tuple[str, ...]:
        return (
            FIXED_SELF_ENTRY_COUNTER_CAPABILITY,
            *(
                ("counter.characteristic.keyword",)
                if keyword_counter_mechanic(self.counter_name) is not None
                else ()
            ),
        )

    def compiled(
        self,
    ) -> tuple[str, Mapping[str, Any], tuple[str, ...]]:
        return (
            FIXED_SELF_ENTRY_COUNTER_TEMPLATE,
            {
                "handler_id": "replacement.zone.self-entry-counter.v1",
                "schema_version": 1,
                "event": "zone.change",
                "counter_name": self.counter_name,
                "amount": self.amount,
                "optional": False,
                "rule_id": "614.1c",
            },
            self.capabilities,
        )


def fixed_self_entry_counter_handler(
    text: str,
    *,
    source_name: str,
) -> tuple[str, Mapping[str, Any], tuple[str, ...]] | None:
    """Lower one source-relative mandatory fixed entry-counter sentence."""

    match = _ENTRY.fullmatch(" ".join(text.strip().split()))
    if match is None:
        return None
    subject = match.group("subject")
    if (
        source_self_permanent_type(subject) is None
        and not SourceReferenceSpec(source_name).matches(subject)
    ):
        return None
    amount = fixed_number(match.group("count"))
    if (
        not 1 <= amount <= 10
        or (match.group("plural").casefold() == "counter") != (amount == 1)
    ):
        return None
    return FixedSelfEntryCounterTemplate(
        counter_name=match.group("counter"),
        amount=amount,
    ).compiled()


__all__ = [
    "FIXED_SELF_ENTRY_COUNTER_CAPABILITY",
    "FIXED_SELF_ENTRY_COUNTER_TEMPLATE",
    "FixedSelfEntryCounterTemplate",
    "fixed_self_entry_counter_handler",
]
