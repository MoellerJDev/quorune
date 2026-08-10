from __future__ import annotations

from typing import Any, Protocol

from .convoke import ConvokeSpec
from .semantic_runtime.cast_costs import (
    CONVOKE_ACTIVE_ZONE,
    CONVOKE_COST_EVENT,
    default_cast_cost_component_registry,
)


class CompiledCastCostHost(Protocol):
    semantics: Any

    def semantic_program_is_current_trusted(self, program: Any) -> bool: ...


def _selected_face_id(spell_program: Any) -> str:
    if spell_program is None:
        return "front"
    face_id = str(spell_program.provenance.get("face_id") or "")
    if face_id:
        return face_id
    ability_id = str(getattr(spell_program, "ability_id", "") or "")
    return ability_id.removeprefix("spell:") or "front"


def compiled_convoke_specs(
    host: CompiledCastCostHost,
    oracle_id: str,
    *,
    spell_program: Any,
) -> tuple[ConvokeSpec, ...]:
    """Return the selected face's trusted precompiled Convoke descriptor."""

    expected_face = _selected_face_id(spell_program)
    registry = default_cast_cost_component_registry()
    result: list[ConvokeSpec] = []
    for program in host.semantics.runtime_handler_programs_for_oracle(
        oracle_id,
        active_zone=CONVOKE_ACTIVE_ZONE,
        event=CONVOKE_COST_EVENT,
    ):
        if not host.semantic_program_is_current_trusted(program):
            continue
        if str(program.provenance.get("face_id") or "") != expected_face:
            continue
        for descriptor in program.handlers:
            if registry.describe(str(descriptor.get("handler_id") or "")) is None:
                continue
            result.extend(registry.lower(descriptor, None))
    return (ConvokeSpec(),) if result else ()


__all__ = ["CompiledCastCostHost", "compiled_convoke_specs"]
