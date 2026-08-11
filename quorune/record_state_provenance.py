from __future__ import annotations

"""Additive Game Record v3 state-semantics provenance facade."""

from typing import Any, Mapping

from .record_commander_identity import (
    commander_damage_identity_version,
    validate_commander_damage_identity_provenance,
)
from .record_control_history import (
    serialized_control_history_version,
    validate_control_history_provenance,
)


def format_state_versions(state: Any) -> dict[str, int]:
    """Return canonical manifest markers for additive state semantics."""

    return {
        "commander_damage_identity_version": commander_damage_identity_version(
            state.commander_damage_identity_version
        ),
        "control_history_version": serialized_control_history_version(
            state.control_history_version
        ),
    }


def validate_state_versions(
    manifest: Mapping[str, Any],
    state: Any,
) -> None:
    """Require manifest and initial-checkpoint semantic versions to agree."""

    validate_commander_damage_identity_provenance(
        manifest, state.commander_damage_identity_version
    )
    validate_control_history_provenance(
        manifest, state.control_history_version
    )


__all__ = ["format_state_versions", "validate_state_versions"]
