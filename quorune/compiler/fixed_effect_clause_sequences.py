from __future__ import annotations

"""Closed printed-order sequences of independently typed effect clauses."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Mapping


FIXED_EFFECT_CLAUSE_SEQUENCE_MECHANIC = "fixed-effect-clause-sequence"

CompiledEffectTemplate = tuple[
    str | None,
    tuple[Mapping[str, Any], ...],
    Mapping[str, Any] | None,
    tuple[str, ...],
]
ClauseCompiler = Callable[[str], CompiledEffectTemplate]


def _two_sentence_clauses(text: str) -> tuple[str, str] | None:
    """Split exactly two top-level sentences without entering quoted rules."""

    normalized = text.strip()
    if not normalized.endswith("."):
        return None
    clauses: list[str] = []
    start = 0
    parenthetical_depth = 0
    quoted = False
    for index, character in enumerate(normalized):
        if character == '"':
            quoted = not quoted
            continue
        if quoted:
            continue
        if character == "(":
            parenthetical_depth += 1
            continue
        if character == ")":
            if parenthetical_depth == 0:
                return None
            parenthetical_depth -= 1
            continue
        if (
            character == "."
            and parenthetical_depth == 0
            and (
                index == len(normalized) - 1
                or normalized[index + 1].isspace()
            )
        ):
            clause = normalized[start : index + 1].strip()
            if not clause:
                return None
            clauses.append(clause)
            start = index + 1
    if quoted or parenthetical_depth or normalized[start:].strip():
        return None
    if len(clauses) != 2:
        return None
    return clauses[0], clauses[1]


@dataclass(frozen=True, slots=True)
class FixedEffectClauseSequenceTemplate:
    """Exactly two independently closed effects sharing at most one target."""

    component_template_ids: tuple[str, str]
    _effects: tuple[Mapping[str, Any], Mapping[str, Any]]
    _target_schema: Mapping[str, Any] | None
    mechanic_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            len(self.component_template_ids) != 2
            or any(not value for value in self.component_template_ids)
            or len(self._effects) != 2
            or len(self.mechanic_ids) < 2
            or self.mechanic_ids[0] != FIXED_EFFECT_CLAUSE_SEQUENCE_MECHANIC
        ):
            raise ValueError("Fixed effect-clause sequence is malformed")
        object.__setattr__(self, "_effects", deepcopy(self._effects))
        object.__setattr__(self, "_target_schema", deepcopy(self._target_schema))

    @property
    def template_id(self) -> str:
        return "fixed-effect-clause-sequence-v1"

    @property
    def effects(self) -> tuple[Mapping[str, Any], ...]:
        return deepcopy(self._effects)

    @property
    def target_schema(self) -> Mapping[str, Any] | None:
        return deepcopy(self._target_schema)

    def compiled(self) -> CompiledEffectTemplate:
        return (
            self.template_id,
            self.effects,
            self.target_schema,
            self.mechanic_ids,
        )


def fixed_effect_clause_sequence_template(
    text: str,
    *,
    compile_clause: ClauseCompiler,
) -> FixedEffectClauseSequenceTemplate | None:
    """Lower two period-separated clauses already owned independently."""

    clauses = _two_sentence_clauses(text)
    if clauses is None:
        return None
    compiled = tuple(compile_clause(clause) for clause in clauses)
    if any(
        template_id is None
        or len(effects) != 1
        or not mechanics
        or FIXED_EFFECT_CLAUSE_SEQUENCE_MECHANIC in mechanics
        for template_id, effects, _target_schema, mechanics in compiled
    ):
        return None
    targeted = tuple(
        target_schema
        for _template_id, _effects, target_schema, _mechanics in compiled
        if target_schema is not None
    )
    if len(targeted) > 1:
        return None
    return FixedEffectClauseSequenceTemplate(
        component_template_ids=tuple(
            str(template_id)
            for template_id, _effects, _target_schema, _mechanics in compiled
        ),
        _effects=tuple(
            deepcopy(effects[0])
            for _template_id, effects, _target_schema, _mechanics in compiled
        ),
        _target_schema=targeted[0] if targeted else None,
        mechanic_ids=tuple(
            dict.fromkeys(
                (
                    FIXED_EFFECT_CLAUSE_SEQUENCE_MECHANIC,
                    *(
                        mechanic
                        for _template_id, _effects, _target_schema, mechanics
                        in compiled
                        for mechanic in mechanics
                    ),
                )
            )
        ),
    )


__all__ = [
    "FIXED_EFFECT_CLAUSE_SEQUENCE_MECHANIC",
    "FixedEffectClauseSequenceTemplate",
    "fixed_effect_clause_sequence_template",
]
