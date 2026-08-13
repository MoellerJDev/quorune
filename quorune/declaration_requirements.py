from __future__ import annotations

"""Compiler-only whole-line combat declaration requirement grammar."""

import re

from .declaration_costs import normalized_oracle_line
from .declaration_fragments import (
    DECLARATION_COMPONENT_CAPABILITY_ID,
    DeclarationRequirementKind,
    DeclarationRequirementTemplate,
)


_ATTACK_EACH_COMBAT = re.compile(
    r"this creature attacks each combat if able\."
)
_BLOCK_EACH_COMBAT = re.compile(
    r"this creature blocks each combat if able\."
)
_MUST_BE_BLOCKED = re.compile(
    r"this creature must be blocked if able\."
)
_ALL_ABLE_BLOCKERS = re.compile(
    r"all creatures able to block this creature do so\."
)


def parse_declaration_requirement_line(
    text: str,
    *,
    card_name: str = "",
) -> DeclarationRequirementTemplate | None:
    """Compile the bounded whole-line CR 508/509 requirement family."""

    line = normalized_oracle_line(text, card_name=card_name)
    matched = (
        (
            _ATTACK_EACH_COMBAT,
            "intrinsic-attack-each-combat-if-able-v1",
            "attack",
            "attack_each_combat",
        ),
        (
            _BLOCK_EACH_COMBAT,
            "intrinsic-block-each-combat-if-able-v1",
            "block",
            "block_each_combat",
        ),
        (
            _MUST_BE_BLOCKED,
            "intrinsic-must-be-blocked-if-able-v1",
            "block",
            "must_be_blocked",
        ),
        (
            _ALL_ABLE_BLOCKERS,
            "intrinsic-all-able-blockers-v1",
            "block",
            "all_able_blockers",
        ),
    )
    for pattern, template_id, declaration, kind in matched:
        if pattern.fullmatch(line):
            return DeclarationRequirementTemplate(
                template_id=template_id,
                declaration=declaration,
                kind=kind,
            )
    return None


__all__ = [
    "DECLARATION_COMPONENT_CAPABILITY_ID",
    "DeclarationRequirementKind",
    "DeclarationRequirementTemplate",
    "parse_declaration_requirement_line",
]
