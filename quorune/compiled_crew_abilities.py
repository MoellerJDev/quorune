from __future__ import annotations

"""Runtime access to trusted source-pinned ordinary Crew descriptors."""

from typing import Any

from .compiled_activated_abilities import (
    CompiledActivatedAbilityHost,
    trusted_face_handler_family_present,
    trusted_face_handler_programs,
)
from .crew import CREW_HANDLER_ID, OrdinaryCrewAbilitySpec
from .semantic_runtime.crew_abilities import (
    ordinary_crew_specs_from_descriptors,
)


def compiled_ordinary_crew_abilities(
    host: CompiledActivatedAbilityHost,
    card: Any,
    *,
    executable_oracle_text: str,
) -> tuple[OrdinaryCrewAbilitySpec, ...]:
    result = [
        spec
        for program in trusted_face_handler_programs(
            host,
            card,
            executable_oracle_text=executable_oracle_text,
            active_zone="battlefield",
            event="activate",
        )
        for spec in ordinary_crew_specs_from_descriptors(program.handlers)
    ]
    return tuple(sorted(result, key=lambda spec: spec.line_index))


def compiled_ordinary_crew_family_present(
    host: CompiledActivatedAbilityHost,
    card: Any,
) -> bool:
    return trusted_face_handler_family_present(
        host,
        card,
        active_zone="battlefield",
        event="activate",
        handler_id=CREW_HANDLER_ID,
    )


__all__ = [
    "compiled_ordinary_crew_abilities",
    "compiled_ordinary_crew_family_present",
]
