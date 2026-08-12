from __future__ import annotations

"""Closed descriptors for ordinary printed Unleash."""


UNLEASH_MECHANIC = "unleash"
UNLEASH_COUNTER = "+1/+1"
UNLEASH_ENTRY_HANDLER_ID = "replacement.zone.self-entry-counter.v1"
UNLEASH_BLOCK_HANDLER_ID = "combat.block.self-counter-prohibition.v1"


def unleash_entry_handler_descriptor() -> dict[str, object]:
    return {
        "handler_id": UNLEASH_ENTRY_HANDLER_ID,
        "schema_version": 1,
        "event": "zone.change",
        "counter_name": UNLEASH_COUNTER,
        "amount": 1,
        "optional": True,
        "rule_id": "702.98a",
    }


def unleash_block_handler_descriptor() -> dict[str, object]:
    return {
        "handler_id": UNLEASH_BLOCK_HANDLER_ID,
        "schema_version": 1,
        "event": "combat.block",
        "counter_name": UNLEASH_COUNTER,
        "minimum": 1,
        "rule_id": "702.98a",
    }


__all__ = [
    "UNLEASH_BLOCK_HANDLER_ID",
    "UNLEASH_COUNTER",
    "UNLEASH_ENTRY_HANDLER_ID",
    "UNLEASH_MECHANIC",
    "unleash_block_handler_descriptor",
    "unleash_entry_handler_descriptor",
]
