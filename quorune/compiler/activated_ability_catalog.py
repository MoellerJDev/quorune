from __future__ import annotations

"""Compile complete activated-ability discovery descriptors once."""

from dataclasses import replace
from typing import Any, Iterable, Mapping

from ..abilities import ActivatedAbility, parse_activated_abilities
from ..carddb import CardRecord
from ..color_set_mana_abilities import (
    compile_color_set_activated_mana_ability,
)
from ..fixed_mana_abilities import (
    compile_fixed_activated_mana_ability,
    fixed_mana_modes_from_effect,
)
from ..replacement.immutable import FrozenMap
from ..semantic_runtime.activated_abilities import (
    ACTIVATED_ABILITY_CATALOG_HANDLER_ID,
    activated_ability_catalog_descriptor,
)
from ..semantic_runtime.color_set_mana_abilities import (
    color_set_mana_specs_from_descriptors,
)
from ..semantic_runtime.crew_abilities import (
    ordinary_crew_specs_from_descriptors,
)
from ..semantic_runtime.cycling_abilities import (
    ordinary_cycling_specs_from_descriptors,
)
from ..semantic_runtime.mana_abilities import (
    fixed_mana_specs_from_descriptors,
)
from ..semantics import SemanticProgram


def _face_material(
    record: CardRecord,
) -> tuple[tuple[str, str, str, tuple[str, ...]], ...]:
    if not record.faces:
        return (("front", record.name, record.oracle_text, record.keywords),)
    return tuple(
        (
            str(face.get("name") or "front"),
            str(face.get("name") or record.name),
            str(face.get("oracle_text") or ""),
            record.keywords,
        )
        for face in record.faces
    )


def compile_activated_ability_catalog(
    record: CardRecord,
) -> dict[str, tuple[ActivatedAbility, ...]]:
    """Return source-face keyed typed abilities for one pinned record."""

    return {
        face_id: tuple(
            _specialize_compiled_ability(ability)
            for ability in parse_activated_abilities(
                card_name=face_name,
                oracle_text=oracle_text,
                keywords=keywords,
            )
        )
        for face_id, face_name, oracle_text, keywords in _face_material(record)
    }


def _specialize_compiled_ability(
    ability: ActivatedAbility,
) -> ActivatedAbility:
    candidates = tuple(
        spec.to_activated_ability()
        for spec in (
            compile_fixed_activated_mana_ability(ability),
            compile_color_set_activated_mana_ability(ability),
        )
        if spec is not None
    )
    if len(candidates) > 1:
        raise ValueError(
            f"{ability.ability_id} belongs to competing activation families"
        )
    if candidates:
        return candidates[0]
    if ability.mana_ability and _mana_output_tail_is_typed(ability):
        output_clause = ability.effect_text.split(".", 1)[0].strip() + "."
        modes = fixed_mana_modes_from_effect(output_clause)
        if modes is not None:
            return replace(ability, fixed_mana_outputs=modes)
    return ability


def _mana_output_tail_is_typed(ability: ActivatedAbility) -> bool:
    sentences = tuple(
        sentence.strip().casefold()
        for sentence in ability.effect_text.split(".")[1:]
        if sentence.strip()
    )
    return all(
        sentence.startswith(
            (
                "activate only ",
                "spend this mana ",
                "this mana can't ",
                "that spell can't ",
            )
        )
        for sentence in sentences
    )


def _program_face_id(
    record: CardRecord,
    program: SemanticProgram,
) -> str | None:
    explicit = str(program.provenance.get("face_id") or "").strip()
    face_ids = tuple(face_id for face_id, *_ in _face_material(record))
    if explicit in face_ids:
        return explicit
    if explicit in {"front", "back"} and len(face_ids) == 2:
        return face_ids[0 if explicit == "front" else 1]
    return face_ids[0] if len(face_ids) == 1 else None


def _specialized_ability(
    program: SemanticProgram,
) -> ActivatedAbility | None:
    handlers = tuple(program.handlers)
    candidates = tuple(
        spec.to_activated_ability()
        for specs in (
            fixed_mana_specs_from_descriptors(handlers),
            color_set_mana_specs_from_descriptors(handlers),
            ordinary_cycling_specs_from_descriptors(handlers),
            ordinary_crew_specs_from_descriptors(handlers),
        )
        for spec in specs
    )
    if len(candidates) > 1:
        raise ValueError(
            f"{program.key} declares competing activated-ability descriptors"
        )
    return candidates[0] if candidates else None


def _ability_id(program: SemanticProgram) -> str | None:
    prefix, separator, value = program.ability_id.partition(":")
    if prefix != "ability" or not separator or not value:
        return None
    return value


def _catalog_ability_for_program(
    record: CardRecord,
    program: SemanticProgram,
    *,
    catalog: Mapping[str, tuple[ActivatedAbility, ...]],
    reference_programs: Iterable[SemanticProgram],
) -> ActivatedAbility | None:
    references = tuple(reference_programs)
    reference = next(
        (candidate for candidate in references if candidate.key == program.key),
        None,
    )
    if reference is None:
        reference = next(
            (
                candidate
                for candidate in references
                if candidate.ability_id == program.ability_id
                and candidate.active_zone == program.active_zone
                and candidate.event == program.event
            ),
            None,
        )
    specialized = _specialized_ability(reference or program)
    if specialized is not None:
        ability = specialized
    else:
        ability_id = _ability_id(program)
        if ability_id is None:
            return None
        face_id = _program_face_id(record, program)
        face_candidates = (
            catalog.get(face_id, ())
            if face_id is not None
            else tuple(
                ability
                for abilities in catalog.values()
                for ability in abilities
            )
        )
        matches = tuple(
            ability
            for ability in face_candidates
            if ability.ability_id == ability_id
            and program.active_zone in ability.zones
        )
        if len(matches) != 1:
            return None
        ability = matches[0]
    target_schema = (
        FrozenMap(program.target_schema)
        if program.target_schema is not None
        else ability.target_schema
    )
    return replace(
        ability,
        zones=(program.active_zone,),
        target_schema=target_schema,
        builtin_semantic_key=(
            ability.builtin_semantic_key or program.key
        ),
    )


def with_activated_ability_catalog(
    record: CardRecord,
    programs: Iterable[SemanticProgram],
    *,
    reference_programs: Iterable[SemanticProgram] = (),
    carrier_provenance: Mapping[str, Any] | None = None,
) -> tuple[SemanticProgram, ...]:
    """Attach closed discovery descriptors to represented activations.

    ``carrier_provenance`` is supplied only by the pinned Oracle compiler.  It
    lets a completely typed activation (for example a fetchland built-in)
    retain its catalog even when no separate effect program was generated for
    that Oracle line.  Reviewed-pack augmentation deliberately omits it, so a
    reviewed descriptor can never manufacture an unreviewed companion.
    """

    catalog = compile_activated_ability_catalog(record)
    references = tuple(reference_programs)
    result: list[SemanticProgram] = []
    for program in programs:
        if program.event != "activate" or any(
            handler.get("handler_id")
            == ACTIVATED_ABILITY_CATALOG_HANDLER_ID
            for handler in program.handlers
        ):
            result.append(program)
            continue
        ability = _catalog_ability_for_program(
            record,
            program,
            catalog=catalog,
            reference_programs=references,
        )
        if ability is None:
            result.append(program)
            continue
        result.append(
            replace(
                program,
                handlers=[
                    *program.handlers,
                    activated_ability_catalog_descriptor(ability),
                ],
            )
        )
    if carrier_provenance is not None:
        _append_catalog_carriers(
            record,
            catalog=catalog,
            programs=result,
            provenance=carrier_provenance,
        )
    return tuple(result)


def _append_catalog_carriers(
    record: CardRecord,
    *,
    catalog: Mapping[str, tuple[ActivatedAbility, ...]],
    programs: list[SemanticProgram],
    provenance: Mapping[str, Any],
) -> None:
    required = {
        "source_oracle_hash",
        "source_rulings_hash",
        "authored_by",
        "review_status",
    }
    if not required.issubset(provenance) or any(
        not str(provenance.get(field) or "").strip() for field in required
    ):
        raise ValueError(
            "Activated-ability catalog carriers require source-pinned provenance"
        )
    represented = {
        (_program_face_id(record, program), ability.ability_id)
        for program in programs
        for ability in activated_abilities_from_program(program)
    }
    for face_id, abilities in catalog.items():
        for ability in abilities:
            if (face_id, ability.ability_id) in represented:
                continue
            programs.append(
                SemanticProgram(
                    key=(
                        f"{record.oracle_id}:catalog:{face_id}:"
                        f"ability:{ability.ability_id}"
                    ),
                    label=f"{record.name} activated ability catalog",
                    oracle_id=record.oracle_id,
                    ability_id=(
                        f"ability:catalog:{face_id}:{ability.ability_id}"
                    ),
                    active_zone=ability.zones[0],
                    event="activate",
                    trust_level="provisional",
                    provenance={
                        **dict(provenance),
                        "face_id": face_id,
                        "template_id": "activated-ability-catalog-v1",
                    },
                    handlers=[activated_ability_catalog_descriptor(ability)],
                )
            )


def activated_abilities_from_program(
    program: SemanticProgram,
) -> tuple[ActivatedAbility, ...]:
    """Return only the closed catalog entries already carried by a program."""

    from ..semantic_runtime.activated_abilities import (
        activated_abilities_from_descriptors,
    )

    return activated_abilities_from_descriptors(program.handlers)


__all__ = [
    "compile_activated_ability_catalog",
    "with_activated_ability_catalog",
]
