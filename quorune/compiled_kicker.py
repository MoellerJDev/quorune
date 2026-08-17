from __future__ import annotations

from typing import Any, Protocol

from .card_programs.admission import program_has_complete_card_program_admission
from .kicker import FixedManaKickerSpec, KICKER_MECHANIC_ID, KICKER_RUNTIME_EVENT
from .semantic_runtime.kicker import default_fixed_mana_kicker_registry


class CompiledKickerHost(Protocol):
    semantics: Any

    def card_record(self, card: Any) -> Any: ...

    def semantic_program_is_current_trusted(self, program: Any) -> bool: ...


def compiled_fixed_mana_kicker_spec(
    host: CompiledKickerHost,
    card: Any,
) -> FixedManaKickerSpec | None:
    """Return one complete-card-admitted source-pinned Kicker descriptor."""

    record = host.card_record(card)
    if (
        record is None
        or record.layout != "normal"
        or record.faces
        or KICKER_MECHANIC_ID
        not in {str(value).casefold() for value in record.keywords}
        or card.annotations.get("copy_overrides") is not None
    ):
        return None
    registry = default_fixed_mana_kicker_registry()
    result: list[FixedManaKickerSpec] = []
    for program in host.semantics.runtime_handler_programs_for_oracle(
        record.oracle_id,
        active_zone="all",
        event=KICKER_RUNTIME_EVENT,
    ):
        if (
            not host.semantic_program_is_current_trusted(program)
            or not program_has_complete_card_program_admission(program)
        ):
            continue
        for descriptor in program.handlers:
            if registry.describe(str(descriptor.get("handler_id") or "")) is None:
                continue
            result.extend(registry.lower(descriptor, None))
    return result[0] if len(result) == 1 else None


__all__ = ["CompiledKickerHost", "compiled_fixed_mana_kicker_spec"]
