from __future__ import annotations

"""Closed compiler owner for ordinary fixed ``Choose one`` spells."""

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import re
from typing import Any, Callable, Mapping, Sequence

from ..util import stable_json


FIXED_CHOOSE_ONE_MODAL_MECHANIC = "fixed-choose-one-modal-spell"
FIXED_CHOOSE_ONE_MODAL_CAPABILITY = "choice.modal.fixed_one"

CompiledEffectTemplate = tuple[
    str | None,
    tuple[Mapping[str, Any], ...],
    Mapping[str, Any] | None,
    tuple[str, ...],
]
EffectCompiler = Callable[[str], CompiledEffectTemplate]
MaterialRow = tuple[str, str, Any]

_HEADER = "Choose one —"
_BULLET_PREFIX = "• "
_NAMED_MODE = re.compile(
    r"^(?P<label>[A-Z][A-Za-z' ]*[A-Za-z']) — (?P<body>.+)$"
)


@dataclass(frozen=True, slots=True)
class FixedChooseOneModalSpellTemplate:
    """One mandatory choice among two or three independently closed modes."""

    component_template_ids: tuple[str, ...]
    _target_schema: Mapping[str, Any]
    mechanic_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            len(self.component_template_ids) not in {2, 3}
            or any(not value for value in self.component_template_ids)
            or self.mechanic_ids[:1] != (FIXED_CHOOSE_ONE_MODAL_MECHANIC,)
        ):
            raise ValueError("Fixed Choose one modal template is malformed")
        schema = deepcopy(dict(self._target_schema))
        if schema.get("mode_count") != 1:
            raise ValueError("Fixed Choose one modal template requires one mode")
        modes = schema.get("modes")
        expected = tuple(
            f"mode_{index}"
            for index in range(1, len(self.component_template_ids) + 1)
        )
        if not isinstance(modes, Mapping) or tuple(modes) != expected:
            raise ValueError("Fixed Choose one modal definitions are malformed")
        object.__setattr__(self, "_target_schema", schema)

    @property
    def template_id(self) -> str:
        digest = hashlib.sha256(
            stable_json(
                {
                    "components": self.component_template_ids,
                    "target_schema": self._target_schema,
                }
            ).encode("utf-8")
        ).hexdigest()[:16]
        return f"fixed-choose-one-modal-{digest}-v1"

    @property
    def effects(self) -> tuple[Mapping[str, Any], ...]:
        return ()

    @property
    def target_schema(self) -> Mapping[str, Any]:
        return deepcopy(self._target_schema)

    @property
    def mechanics(self) -> tuple[str, ...]:
        return self.mechanic_ids

    def compiled(self) -> CompiledEffectTemplate:
        return (
            self.template_id,
            self.effects,
            self.target_schema,
            self.mechanics,
        )


def _mode_body(material_line: str) -> str | None:
    if not material_line.startswith(_BULLET_PREFIX):
        return None
    body = material_line[len(_BULLET_PREFIX) :]
    named = _NAMED_MODE.fullmatch(body)
    return named.group("body") if named is not None else body


def fixed_choose_one_modal_spell_template(
    material_rows: Sequence[MaterialRow],
    *,
    compile_effect: EffectCompiler,
) -> FixedChooseOneModalSpellTemplate | None:
    """Lower only a complete ordinary two- or three-mode spell face."""

    if (
        len(material_rows) not in {3, 4}
        or material_rows[0][1] != _HEADER
    ):
        return None
    bodies = tuple(_mode_body(row[1]) for row in material_rows[1:])
    if any(body is None or not body.strip() for body in bodies):
        return None
    compiled = tuple(compile_effect(str(body)) for body in bodies)
    if any(
        template_id is None
        or not effects
        or not mechanics
        or target_schema is not None
        and "modes" in target_schema
        for template_id, effects, target_schema, mechanics in compiled
    ):
        return None

    modes: dict[str, dict[str, Any]] = {}
    mechanic_ids = [FIXED_CHOOSE_ONE_MODAL_MECHANIC]
    for index, (_template, effects, target_schema, mechanics) in enumerate(
        compiled,
        1,
    ):
        definition = deepcopy(dict(target_schema or {}))
        if target_schema is None:
            definition["groups"] = []
        definition["effects"] = [deepcopy(dict(effect)) for effect in effects]
        definition["mechanics"] = list(mechanics)
        modes[f"mode_{index}"] = definition
        mechanic_ids.extend(mechanics)
    return FixedChooseOneModalSpellTemplate(
        component_template_ids=tuple(
            str(template_id)
            for template_id, _effects, _schema, _mechanics in compiled
        ),
        _target_schema={"mode_count": 1, "modes": modes},
        mechanic_ids=tuple(dict.fromkeys(mechanic_ids)),
    )


__all__ = [
    "FIXED_CHOOSE_ONE_MODAL_CAPABILITY",
    "FIXED_CHOOSE_ONE_MODAL_MECHANIC",
    "FixedChooseOneModalSpellTemplate",
    "fixed_choose_one_modal_spell_template",
]
