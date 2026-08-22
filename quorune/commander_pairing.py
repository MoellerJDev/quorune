from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Protocol

from .characteristic_evaluation import type_parts

if TYPE_CHECKING:
    from .carddb import CardDatabase, CardRecord
    from .semantics import SemanticProgram


COMMANDER_PAIRING_TEMPLATE_ID = "commander-pairing-eligibility-v1"
COMMANDER_PAIRING_EVENT = "game.setup"
COMMANDER_PAIRING_COVERAGE = "commander_pairing_eligibility"


class CommanderPairingKind(str, Enum):
    PARTNER = "partner"
    CHOOSE_A_BACKGROUND = "choose a background"
    DOCTORS_COMPANION = "doctor's companion"


PAIRING_CAPABILITY_BY_KIND = {
    CommanderPairingKind.PARTNER: "format.commander.pairing.partner",
    CommanderPairingKind.CHOOSE_A_BACKGROUND: (
        "format.commander.pairing.choose_background"
    ),
    CommanderPairingKind.DOCTORS_COMPANION: (
        "format.commander.pairing.doctors_companion"
    ),
}


class CommanderPairingError(ValueError):
    """A proposed two-commander designation is not compiler-certified."""


class PairingProgramRegistry(Protocol):
    def programs_for_oracle(
        self,
        oracle_id: str,
        *,
        active_zone: str | None = None,
        event: str | None = None,
    ) -> list["SemanticProgram"]: ...

    def card_program_for_oracle(self, oracle_id: str) -> object | None: ...


@dataclass(frozen=True, slots=True)
class CommanderPairingDeclaration:
    kind: CommanderPairingKind
    capability_id: str
    program_key: str


def pairing_kind_for_material_line(
    material_line: str,
) -> CommanderPairingKind | None:
    """Recognize only the three exact ordinary setup declarations."""

    normalized = material_line.strip().rstrip(".").casefold()
    try:
        return CommanderPairingKind(normalized)
    except ValueError:
        return None


def _program_pairing_kind(
    program: "SemanticProgram",
) -> CommanderPairingKind | None:
    matches = [
        kind
        for kind, capability_id in PAIRING_CAPABILITY_BY_KIND.items()
        if program.capability_dependencies == [capability_id]
    ]
    if len(matches) != 1:
        return None
    kind = matches[0]
    closure = program.capability_closure
    if (
        program.trust_level != "trusted"
        or program.requires_arbiter
        or not program.ability_id.startswith("static:")
        or program.active_zone != "all"
        or program.event != COMMANDER_PAIRING_EVENT
        or program.provenance.get("template_id")
        != COMMANDER_PAIRING_TEMPLATE_ID
        or program.effects
        or program.handlers
        or program.target_schema is not None
        or program.cost_schema is not None
        or program.event_condition is not None
        or COMMANDER_PAIRING_COVERAGE not in program.coverage
        or kind.value not in program.coverage
        or not isinstance(closure, dict)
        or closure.get("requested") != [PAIRING_CAPABILITY_BY_KIND[kind]]
        or closure.get("trusted") is not True
        or closure.get("blockers") != []
    ):
        return None
    return kind


def commander_pairing_declaration(
    card_db: "CardDatabase",
    registry: PairingProgramRegistry | None,
    card: "CardRecord",
) -> CommanderPairingDeclaration | None:
    """Read one current typed setup declaration without reparsing Oracle text."""

    if registry is None:
        return None
    # Imported lazily because the compiler also imports the declaration
    # constants from this module while CardProgram adapters are initializing.
    from .card_programs.validation import (
        canonical_program_fingerprint,
        program_source_is_current,
    )

    candidates: list[tuple[SemanticProgram, CommanderPairingKind]] = []
    for program in registry.programs_for_oracle(
        card.oracle_id,
        active_zone="all",
        event=COMMANDER_PAIRING_EVENT,
    ):
        kind = _program_pairing_kind(program)
        if (
            kind is None
            or program.oracle_id != card.oracle_id
            or canonical_program_fingerprint(registry, program) is None
            or not program_source_is_current(card_db, program)
        ):
            continue
        candidates.append((program, kind))
    if len(candidates) != 1:
        return None
    program, kind = candidates[0]
    return CommanderPairingDeclaration(
        kind=kind,
        capability_id=PAIRING_CAPABILITY_BY_KIND[kind],
        program_key=program.key,
    )


def _is_legendary(card: "CardRecord") -> bool:
    _, _, supertypes = type_parts(card.type_line)
    return "legendary" in supertypes


def _is_background(card: "CardRecord") -> bool:
    card_types, subtypes, supertypes = type_parts(card.type_line)
    return bool(
        "legendary" in supertypes
        and "enchantment" in card_types
        and "background" in subtypes
    )


def _is_legendary_creature(card: "CardRecord") -> bool:
    card_types, _, supertypes = type_parts(card.type_line)
    return "legendary" in supertypes and "creature" in card_types


def _is_doctor(card: "CardRecord") -> bool:
    card_types, subtypes, supertypes = type_parts(card.type_line)
    return bool(
        "legendary" in supertypes
        and "creature" in card_types
        and subtypes == {"time lord", "doctor"}
    )


def validate_commander_pair(
    card_db: "CardDatabase",
    registry: PairingProgramRegistry | None,
    commanders: tuple["CardRecord", "CardRecord"],
) -> tuple[CommanderPairingDeclaration | None, ...]:
    """Validate CR 702.124h/k/m through one shared typed setup owner."""

    first, second = commanders
    if first.oracle_id == second.oracle_id:
        raise CommanderPairingError(
            "Two commanders must designate distinct Commander-legal cards"
        )
    if not _is_legendary(first) or not _is_legendary(second):
        raise CommanderPairingError(
            "Both cards in a two-commander designation must be legendary"
        )

    declarations = (
        commander_pairing_declaration(card_db, registry, first),
        commander_pairing_declaration(card_db, registry, second),
    )
    kinds = tuple(
        declaration.kind if declaration is not None else None
        for declaration in declarations
    )
    if kinds == (
        CommanderPairingKind.PARTNER,
        CommanderPairingKind.PARTNER,
    ) and all(_is_legendary_creature(card) for card in commanders):
        return declarations
    if (
        kinds[0] == CommanderPairingKind.CHOOSE_A_BACKGROUND
        and _is_background(second)
    ) or (
        kinds[1] == CommanderPairingKind.CHOOSE_A_BACKGROUND
        and _is_background(first)
    ):
        return declarations
    if (
        kinds[0] == CommanderPairingKind.DOCTORS_COMPANION
        and _is_legendary_creature(first)
        and _is_doctor(second)
    ) or (
        kinds[1] == CommanderPairingKind.DOCTORS_COMPANION
        and _is_legendary_creature(second)
        and _is_doctor(first)
    ):
        return declarations
    raise CommanderPairingError(
        "Two commanders require matching typed Partner, Choose a Background, "
        "or Doctor's companion setup declarations"
    )


__all__ = [
    "COMMANDER_PAIRING_COVERAGE",
    "COMMANDER_PAIRING_EVENT",
    "COMMANDER_PAIRING_TEMPLATE_ID",
    "CommanderPairingDeclaration",
    "CommanderPairingError",
    "CommanderPairingKind",
    "PAIRING_CAPABILITY_BY_KIND",
    "commander_pairing_declaration",
    "pairing_kind_for_material_line",
    "validate_commander_pair",
]
