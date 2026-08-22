from __future__ import annotations

"""Closed source-permanent return-to-owner-hand grammar."""

from dataclasses import dataclass
import re
from typing import Any, Mapping


FIXED_SELF_RETURN_MECHANIC = "fixed-self-return-to-owner-hand"

_SELF_RETURN = re.compile(
    r"return this (?P<kind>artifact|creature|enchantment|permanent) "
    r"to its owner'?s hand\.?",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class FixedSelfReturnTemplate:
    source_kind: str

    def __post_init__(self) -> None:
        if self.source_kind not in {
            "artifact",
            "creature",
            "enchantment",
            "permanent",
        }:
            raise ValueError("Fixed self-return source kind is unsupported")

    @property
    def template_id(self) -> str:
        return f"bounce-self-{self.source_kind}-v1"

    def compiled(
        self,
    ) -> tuple[
        str,
        tuple[Mapping[str, Any], ...],
        None,
        tuple[str, ...],
    ]:
        return (
            self.template_id,
            ({"op": "bounce", "card": "$source"},),
            None,
            (FIXED_SELF_RETURN_MECHANIC,),
        )


def fixed_self_return_effect_template(
    text: str,
) -> FixedSelfReturnTemplate | None:
    """Lower one mandatory return of the source permanent."""

    match = _SELF_RETURN.fullmatch(text.strip())
    if match is None:
        return None
    return FixedSelfReturnTemplate(match.group("kind").casefold())


__all__ = [
    "FIXED_SELF_RETURN_MECHANIC",
    "FixedSelfReturnTemplate",
    "fixed_self_return_effect_template",
]
