from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any, Iterable, Mapping

from ..util import stable_json


class SpellCastEventError(ValueError):
    """A normalized spell-cast event is malformed or unsupported."""


def _identity(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SpellCastEventError(f"{field} must be a nonempty string")
    return value.strip()


def _types(values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise SpellCastEventError(
            "Spell card types must be an iterable of strings"
        )
    normalized: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise SpellCastEventError(
                "Spell card types must contain nonempty strings"
            )
        normalized.add(value.strip().casefold())
    if not normalized:
        raise SpellCastEventError("A cast spell must have at least one card type")
    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class SpellCastEvent:
    """Immutable facts captured when CR 601.2i makes a spell cast."""

    card_ref: str
    object_id: str
    logical_object_id: str
    controller: str
    origin: str
    stack_ref: str
    types: tuple[str, ...]
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise SpellCastEventError(
                "Unsupported normalized spell-cast event schema version"
            )
        for field in (
            "card_ref",
            "object_id",
            "logical_object_id",
            "controller",
            "origin",
            "stack_ref",
        ):
            object.__setattr__(
                self,
                field,
                _identity(getattr(self, field), field=field),
            )
        object.__setattr__(self, "types", _types(self.types))

    def to_context(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "card": self.card_ref,
            "object_id": self.object_id,
            "logical_object_id": self.logical_object_id,
            "controller": self.controller,
            "player": self.controller,
            "from": self.origin,
            "to": "stack",
            "types": list(self.types),
            "stack": self.stack_ref,
        }

    @classmethod
    def from_context(cls, value: Mapping[str, Any]) -> "SpellCastEvent":
        expected = {
            "schema_version",
            "card",
            "object_id",
            "logical_object_id",
            "controller",
            "player",
            "from",
            "to",
            "types",
            "stack",
        }
        if not isinstance(value, Mapping) or set(value) != expected:
            raise SpellCastEventError(
                "Normalized spell-cast events have a closed schema"
            )
        if value["player"] != value["controller"]:
            raise SpellCastEventError(
                "Spell-cast player and controller must agree"
            )
        if value["to"] != "stack":
            raise SpellCastEventError(
                "Normalized spell-cast events must describe the stack move"
            )
        raw_types = value["types"]
        if not isinstance(raw_types, (list, tuple)):
            raise SpellCastEventError("Spell-cast types must be an array")
        return cls(
            schema_version=value["schema_version"],
            card_ref=value["card"],
            object_id=value["object_id"],
            logical_object_id=value["logical_object_id"],
            controller=value["controller"],
            origin=value["from"],
            stack_ref=value["stack"],
            types=tuple(raw_types),
        )

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            stable_json(self.to_context()).encode("utf-8")
        ).hexdigest()


__all__ = ["SpellCastEvent", "SpellCastEventError"]
