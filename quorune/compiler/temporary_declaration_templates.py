from __future__ import annotations

"""Closed activated effects that restrict one target creature this turn."""

from dataclasses import dataclass
import re
from typing import Any, Mapping

from ..rules.temporary_declaration_restrictions import (
    TemporaryDeclarationRestrictionKind,
    temporary_declaration_restriction,
)


_TARGET_TEMPORARY_DECLARATION_RESTRICTION = re.compile(
    r"target creature can't (?P<restriction>attack or block|attack|block|be blocked) "
    r"this turn\.?",
    re.IGNORECASE,
)
_RESTRICTION_KINDS: dict[str, TemporaryDeclarationRestrictionKind] = {
    "attack": "cant_attack",
    "block": "cant_block",
    "attack or block": "cant_attack_or_block",
    "be blocked": "unblockable",
}


@dataclass(frozen=True, slots=True)
class ActivatedTemporaryDeclarationRestrictionTemplate:
    restriction: TemporaryDeclarationRestrictionKind

    def __post_init__(self) -> None:
        temporary_declaration_restriction(self.restriction)

    @property
    def template_id(self) -> str:
        return f"activated-target-{self.restriction.replace('_', '-')}-eot-v1"

    @property
    def effects(self) -> tuple[Mapping[str, Any], ...]:
        return (
            {
                "op": "grant_declaration_restriction_until_end_of_turn",
                "card": "$target.0",
                "restriction": self.restriction,
            },
        )

    @property
    def target_schema(self) -> Mapping[str, Any]:
        return {
            "zones": ["battlefield"],
            "categories": ["permanent"],
            "types_any": ["creature"],
            "count": 1,
        }

    def compiled(
        self,
    ) -> tuple[
        str,
        tuple[Mapping[str, Any], ...],
        Mapping[str, Any],
        tuple[str, ...],
    ]:
        restriction = temporary_declaration_restriction(self.restriction)
        return (
            self.template_id,
            self.effects,
            self.target_schema,
            (
                "cr-115-targets",
                "cr-611-continuous-effects",
                *restriction.mechanics,
            ),
        )


def activated_temporary_declaration_restriction_effect_template(
    text: str,
) -> ActivatedTemporaryDeclarationRestrictionTemplate | None:
    """Parse only the four whole-clause activated declaration instructions."""

    normalized = " ".join(text.strip().split())
    match = _TARGET_TEMPORARY_DECLARATION_RESTRICTION.fullmatch(normalized)
    if match is None:
        return None
    return ActivatedTemporaryDeclarationRestrictionTemplate(
        _RESTRICTION_KINDS[match.group("restriction").casefold()]
    )


__all__ = [
    "ActivatedTemporaryDeclarationRestrictionTemplate",
    "activated_temporary_declaration_restriction_effect_template",
]
