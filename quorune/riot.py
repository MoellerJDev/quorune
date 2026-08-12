from __future__ import annotations


RIOT_MECHANIC = "riot"
RIOT_COUNTER = "+1/+1"
RIOT_ENTRY_HANDLER_ID = "replacement.zone.riot-entry-choice.v1"


def riot_entry_handler_descriptor() -> dict[str, object]:
    return {
        "handler_id": RIOT_ENTRY_HANDLER_ID,
        "schema_version": 1,
        "event": "zone.change",
        "counter_name": RIOT_COUNTER,
        "amount": 1,
        "alternative_keyword": "haste",
        "rule_id": "702.136a",
    }


__all__ = [
    "RIOT_COUNTER",
    "RIOT_ENTRY_HANDLER_ID",
    "RIOT_MECHANIC",
    "riot_entry_handler_descriptor",
]
