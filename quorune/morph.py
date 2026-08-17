from __future__ import annotations

"""Typed ordinary fixed-mana Morph contracts.

The represented family is deliberately narrower than the aggregate mechanic:
one printed ``Morph {fixed ordinary mana}`` ability.  Variable, hybrid,
Phyrexian, snow, and nonmana costs, Megamorph, copied or granted Morph, and
other face-down methods remain outside this contract.
"""

from dataclasses import dataclass
import hashlib
import re
from typing import Any, Mapping, Protocol

from .card_programs.admission import REQUIRES_COMPLETE_CARD_PROGRAM_FIELD
from .keyword_abilities import normalized_characteristic_keywords
from .util import mana_cost_to_vector, stable_json


MORPH_CAPABILITY_ID = "casting.morph.fixed_mana"
MORPH_HANDLER_ID = "casting.morph.fixed-mana.v1"
MORPH_RUNTIME_EVENT = "morph.action"
MORPH_FACE_DOWN_ANNOTATION = "face_down_characteristics"
MORPH_METHOD_ANNOTATION = "face_down_method"
MORPH_CAST_METHOD = "morph"
MORPH_FACE_DOWN_LABEL = "Face-down spell"
MORPH_FACE_DOWN_VALUES: dict[str, Any] = {
    "name": "",
    "mana_cost": "",
    "mana_value": 0,
    "text": "",
    "supertypes": [],
    "card_types": ["Creature"],
    "subtypes": [],
    "colors": [],
    "abilities": [],
    "power": 2,
    "toughness": 2,
}
_MORPH_LINE = re.compile(
    r"^Morph\s+(?P<cost>(?:\{(?:0|[1-9]\d*|[WUBRGC])\})+)\.?$",
    re.IGNORECASE,
)
_MANA_FIELDS = ("GENERIC", "W", "U", "B", "R", "G", "C")


class MorphError(ValueError):
    """A Morph descriptor, state marker, or action is malformed."""


@dataclass(frozen=True, slots=True)
class FixedManaMorphSpec:
    requirements: tuple[int, int, int, int, int, int, int]
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise MorphError("Unsupported fixed-mana Morph schema version")
        if (
            not isinstance(self.requirements, tuple)
            or len(self.requirements) != len(_MANA_FIELDS)
            or any(type(value) is not int or value < 0 for value in self.requirements)
        ):
            raise MorphError(
                "Fixed-mana Morph requirements must be seven nonnegative integers"
            )

    @classmethod
    def from_cost(cls, cost: str) -> "FixedManaMorphSpec":
        requirements, complex_symbols = mana_cost_to_vector(cost)
        if complex_symbols:
            raise MorphError("Morph cost is outside the fixed ordinary-mana family")
        return cls(tuple(int(requirements[field]) for field in _MANA_FIELDS))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "FixedManaMorphSpec":
        if not isinstance(value, Mapping) or set(value) != {
            "schema_version",
            "requirements",
        }:
            raise MorphError("Fixed-mana Morph descriptors have a closed shape")
        requirements = value["requirements"]
        if not isinstance(requirements, Mapping) or set(requirements) != set(
            _MANA_FIELDS
        ):
            raise MorphError("Fixed-mana Morph requirements have a closed shape")
        return cls(
            tuple(requirements[field] for field in _MANA_FIELDS),
            schema_version=value["schema_version"],
        )

    @property
    def requirements_dict(self) -> dict[str, int]:
        return dict(zip(_MANA_FIELDS, self.requirements, strict=True))

    @property
    def cost_text(self) -> str:
        parts: list[str] = []
        generic = self.requirements_dict["GENERIC"]
        if generic:
            parts.append(f"{{{generic}}}")
        for color in "WUBRGC":
            parts.extend(f"{{{color}}}" for _ in range(self.requirements_dict[color]))
        return "".join(parts) or "{0}"

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(stable_json(self.to_dict()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "requirements": self.requirements_dict,
        }


def compile_fixed_mana_morph(material_line: str) -> FixedManaMorphSpec | None:
    match = _MORPH_LINE.fullmatch(material_line.strip())
    if match is None:
        return None
    try:
        return FixedManaMorphSpec.from_cost(match.group("cost"))
    except MorphError:
        return None


def morph_handler_descriptor(spec: FixedManaMorphSpec) -> dict[str, Any]:
    return {
        "handler_id": MORPH_HANDLER_ID,
        "schema_version": 1,
        "event": MORPH_RUNTIME_EVENT,
        REQUIRES_COMPLETE_CARD_PROGRAM_FIELD: True,
        "morph": spec.to_dict(),
    }


def morph_face_down_annotation(spec: FixedManaMorphSpec) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": MORPH_CAST_METHOD,
        "spec_fingerprint": spec.fingerprint,
    }


def validate_morph_face_down_state(card: Any, spec: FixedManaMorphSpec) -> None:
    marker = getattr(card, "annotations", {}).get(MORPH_METHOD_ANNOTATION)
    if (
        not getattr(card, "face_down", False)
        or not isinstance(marker, Mapping)
        or set(marker) != {"schema_version", "kind", "spec_fingerprint"}
        or marker.get("schema_version") != 1
        or marker.get("kind") != MORPH_CAST_METHOD
        or marker.get("spec_fingerprint") != spec.fingerprint
        or getattr(card, "annotations", {}).get(MORPH_FACE_DOWN_ANNOTATION)
        != MORPH_FACE_DOWN_VALUES
    ):
        raise MorphError("Face-down permanent is not the represented Morph object")


class MorphCharacteristicHost(Protocol):
    def _effective_card_data(
        self,
        card: Any,
        *,
        ignore_face_down: bool = False,
    ) -> Mapping[str, Any]: ...


def current_face_up_has_morph(
    host: MorphCharacteristicHost,
    card: Any,
) -> bool:
    """Use the shared effective-keyword boundary for layer-6 loss checks."""

    characteristics = host._effective_card_data(card, ignore_face_down=True)
    return "morph" in normalized_characteristic_keywords(characteristics)


__all__ = [
    "compile_fixed_mana_morph",
    "current_face_up_has_morph",
    "FixedManaMorphSpec",
    "MORPH_CAPABILITY_ID",
    "MORPH_CAST_METHOD",
    "MORPH_FACE_DOWN_ANNOTATION",
    "MORPH_FACE_DOWN_LABEL",
    "MORPH_FACE_DOWN_VALUES",
    "MORPH_HANDLER_ID",
    "MORPH_METHOD_ANNOTATION",
    "MORPH_RUNTIME_EVENT",
    "MorphError",
    "morph_face_down_annotation",
    "morph_handler_descriptor",
    "validate_morph_face_down_state",
]
