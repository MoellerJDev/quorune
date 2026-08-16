from __future__ import annotations

"""Resolution effects that grant typed combat declaration restrictions."""

from typing import Any, Mapping

from ..continuous_effect_state import resolution_effect_source
from ..effect_contracts import effect_family_contract
from ..errors import GameRuleError
from ..rules.temporary_declaration_restrictions import (
    commit_temporary_declaration_restriction,
    TemporaryDeclarationRestrictionError,
)


OPERATIONS = effect_family_contract("declaration-effects.v1").operations


def _apply_grant_declaration_restriction_until_end_of_turn(
    host: Any,
    effect: Mapping[str, Any],
    *,
    actor: str,
    operation: str,
    reason: str,
) -> str:
    del operation
    allowed = {"op", "card", "restriction", "reason", "_runtime_source"}
    unknown = set(effect) - allowed
    if unknown:
        raise GameRuleError(
            "Temporary declaration restriction has unknown fields: "
            + ", ".join(sorted(unknown))
        )
    card = host._resolve_object(
        actor,
        str(effect.get("card") or ""),
        zones={"battlefield"},
    )
    try:
        committed = commit_temporary_declaration_restriction(
            host,
            card=card,
            source=resolution_effect_source(
                host,
                effect,
                fallback_card=card,
            ),
            kind=str(effect.get("restriction") or ""),
        )
    except TemporaryDeclarationRestrictionError as exc:
        raise GameRuleError(str(exc)) from exc
    host._log(
        actor,
        "combat.declaration_restriction",
        f"{card.ref} gained a combat declaration restriction until end of turn.",
        {
            "object": card.ref,
            "restriction": str(effect.get("restriction") or ""),
            "continuous_effect": committed.effect_id,
            "reason": reason,
        },
        importance=1,
        changed_objects=[card.object_id],
    )
    return card.ref


HANDLERS = {
    "grant_declaration_restriction_until_end_of_turn": (
        _apply_grant_declaration_restriction_until_end_of_turn
    ),
}


def apply_effect(
    host: Any,
    effect: Mapping[str, Any],
    *,
    actor: str,
    operation: str,
    reason: str,
) -> Any:
    handler = HANDLERS.get(operation)
    if handler is None:
        raise GameRuleError(f"Unsupported owned effect {operation!r}")
    return handler(
        host,
        effect,
        actor=actor,
        operation=operation,
        reason=reason,
    )


__all__ = ["apply_effect", "HANDLERS", "OPERATIONS"]
