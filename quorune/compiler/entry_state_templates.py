from __future__ import annotations

"""Closed Oracle grammar for battlefield entry tap-state replacements."""

import re
from typing import Any, Mapping

from ..landwalk import BASIC_LAND_TYPES
from .fixed_numbers import FIXED_COUNT_PATTERN, fixed_number
from ..rules.source_references import SourceReferenceSpec


EntryStateHandlerTemplate = tuple[str, Mapping[str, Any], str]


_UNCONDITIONAL = re.compile(
    r"^(?P<subject>This (?:artifact|creature|enchantment|land|permanent)) "
    r"enters tapped\.?$",
    re.IGNORECASE,
)
_LIVE_OPPONENTS = re.compile(
    rf"^This land enters tapped unless you have "
    rf"(?P<count>{FIXED_COUNT_PATTERN}|\d+) or more opponents\.?$",
    re.IGNORECASE,
)
_CONTROLLED_BASIC_TYPES = re.compile(
    r"^This land enters (?:the battlefield )?tapped unless you control "
    r"(?P<types>.+)\.?$",
    re.IGNORECASE,
)
_OPTIONAL_LIFE = re.compile(
    rf"^As this land enters, you may pay "
    rf"(?P<amount>{FIXED_COUNT_PATTERN}|\d+) life\. If you don['’]t, "
    rf"it enters tapped\.?$",
    re.IGNORECASE,
)
_AMBIENT_UNTAPPED = re.compile(
    r"^Lands you control enter untapped\.?$",
    re.IGNORECASE,
)
_BASIC_TYPE_LIST = re.compile(
    r"(?:a|an) (?P<kind>Plains|Island|Swamp|Mountain|Forest)",
    re.IGNORECASE,
)


def _count(value: str) -> int:
    return int(value) if value.isdigit() else fixed_number(value)


def _descriptor(
    *,
    source_relation: str,
    subject_types: tuple[str, ...],
    tapped: bool,
    minimum_opponents: int | None = None,
    controlled_basic_types_any: tuple[str, ...] = (),
    optional_life: int = 0,
) -> dict[str, Any]:
    return {
        "handler_id": "replacement.zone.entry-state.v1",
        "schema_version": 1,
        "event": "zone.change",
        "source_relation": source_relation,
        "subject": {"types_all": list(subject_types)},
        "condition": {
            "minimum_opponents": minimum_opponents,
            "controlled_basic_types_any": list(
                controlled_basic_types_any
            ),
        },
        "instruction": {
            "tapped": tapped,
            "optional_life": optional_life,
        },
    }


def _unconditional_match(text: str, source_name: str) -> bool:
    if _UNCONDITIONAL.fullmatch(text) is not None:
        return True
    if not source_name:
        return False
    source = SourceReferenceSpec(source_name).regex_pattern
    return (
        re.fullmatch(
            rf"{source} enters tapped\.?",
            text,
            re.IGNORECASE,
        )
        is not None
    )


def _controlled_basic_types(text: str) -> tuple[str, ...] | None:
    match = _CONTROLLED_BASIC_TYPES.fullmatch(text)
    if match is None:
        return None
    clause = match.group("types")
    matches = tuple(
        value.casefold()
        for value in _BASIC_TYPE_LIST.findall(clause)
    )
    if not matches or len(matches) != len(set(matches)):
        return None
    reconstructed = " or ".join(
        f"{'an' if value[0] in 'aeiou' else 'a'} {value.title()}"
        for value in matches
    )
    if clause.rstrip(".").casefold() != reconstructed.casefold():
        return None
    if any(value not in BASIC_LAND_TYPES for value in matches):
        return None
    return tuple(sorted(matches))


def static_entry_state_handler(
    text: str,
    *,
    source_name: str,
) -> EntryStateHandlerTemplate | None:
    """Lower one exact tap-state replacement from a closed grammar."""

    normalized = text.strip()
    if _unconditional_match(normalized, source_name):
        return (
            "zone-entry-state-self-tapped-v1",
            _descriptor(
                source_relation="affected_object",
                subject_types=(),
                tapped=True,
            ),
            "zone.entry.tapped_state",
        )

    opponents = _LIVE_OPPONENTS.fullmatch(normalized)
    if opponents is not None:
        count = _count(opponents.group("count"))
        if count < 1:
            return None
        return (
            f"zone-entry-state-self-minimum-{count}-opponents-v1",
            _descriptor(
                source_relation="affected_object",
                subject_types=("land",),
                tapped=True,
                minimum_opponents=count,
            ),
            "zone.entry.tapped_state",
        )

    controlled_types = _controlled_basic_types(normalized)
    if controlled_types is not None:
        return (
            "zone-entry-state-self-controlled-basic-types-v1",
            _descriptor(
                source_relation="affected_object",
                subject_types=("land",),
                tapped=True,
                controlled_basic_types_any=controlled_types,
            ),
            "zone.entry.tapped_state",
        )

    optional_life = _OPTIONAL_LIFE.fullmatch(normalized)
    if optional_life is not None:
        amount = _count(optional_life.group("amount"))
        if amount < 1:
            return None
        return (
            f"zone-entry-state-self-pay-{amount}-life-v1",
            _descriptor(
                source_relation="affected_object",
                subject_types=("land",),
                tapped=True,
                optional_life=amount,
            ),
            "zone.entry.tapped_state",
        )

    if _AMBIENT_UNTAPPED.fullmatch(normalized) is not None:
        return (
            "zone-entry-state-controlled-lands-untapped-v1",
            _descriptor(
                source_relation="controller",
                subject_types=("land",),
                tapped=False,
            ),
            "zone.entry.tapped_state",
        )
    return None


__all__ = ["EntryStateHandlerTemplate", "static_entry_state_handler"]
