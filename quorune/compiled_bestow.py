from __future__ import annotations

from typing import Any, Protocol

from .bestow import BESTOW_MECHANIC_ID, BESTOW_RUNTIME_EVENT, FixedManaBestowSpec
from .card_programs.admission import program_has_complete_card_program_admission
from .semantic_runtime.bestow import default_fixed_mana_bestow_registry


class CompiledBestowHost(Protocol):
    semantics: Any
    def card_record(self, card: Any) -> Any: ...
    def semantic_program_is_current_trusted(self, program: Any) -> bool: ...


def compiled_fixed_mana_bestow_spec(host: CompiledBestowHost, card: Any) -> FixedManaBestowSpec | None:
    record = host.card_record(card)
    if (
        record is None or record.layout != "normal" or record.faces
        or BESTOW_MECHANIC_ID not in {str(value).casefold() for value in record.keywords}
        or card.annotations.get("copy_overrides") is not None
    ):
        return None
    registry = default_fixed_mana_bestow_registry()
    result: list[FixedManaBestowSpec] = []
    for program in host.semantics.runtime_handler_programs_for_oracle(record.oracle_id, active_zone="all", event=BESTOW_RUNTIME_EVENT):
        if not host.semantic_program_is_current_trusted(program) or not program_has_complete_card_program_admission(program):
            continue
        for descriptor in program.handlers:
            if registry.describe(str(descriptor.get("handler_id") or "")) is not None:
                result.extend(registry.lower(descriptor, None))
    return result[0] if len(result) == 1 else None


__all__ = ["CompiledBestowHost", "compiled_fixed_mana_bestow_spec"]
