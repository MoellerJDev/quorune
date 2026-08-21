from __future__ import annotations

from typing import Any, Mapping


_COUNT_DIMENSIONS = (
    "card_named_helpers",
    "legacy_card_specific_operations",
    "oracle_id_literals",
    "oversized_functions_and_methods",
    "oversized_modules",
)


def project_architecture_metrics(
    source: Mapping[str, Any],
) -> dict[str, int]:
    if "architecture" in source:
        dimensions = (
            source.get("architecture", {})
            .get("debt_trend", {})
            .get("dimensions", {})
        )
        return {
            str(key): int(value.get("current") or 0)
            for key, value in sorted(dimensions.items())
            if isinstance(value, Mapping)
        }

    engine = source.get("engine") or {}
    writes = source.get("direct_game_state_writes_by_file") or {}
    return {
        **{key: len(source.get(key) or ()) for key in _COUNT_DIMENSIONS},
        "direct_game_state_writes": sum(int(value) for value in writes.values()),
        "engine_logical_lines": int(engine.get("logical_lines") or 0),
        "prohibited_identity_dispatch_count": 0,
    }


__all__ = ["project_architecture_metrics"]
