from __future__ import annotations

"""Typed resolution-created combat declaration restrictions."""

from typing import Any, Literal, Protocol

from ..ability_fragments import ability_fragment_to_dict
from ..continuous_effect_model import (
    ContinuousEffect,
    ContinuousEffectDuration,
    ContinuousEffectError,
    ContinuousOperation,
    Layer,
)
from ..continuous_effect_state import (
    ContinuousEffectStateError,
    ResolutionEffectSource,
    create_resolution_continuous_effect,
)
from ..declaration_fragments import DeclarationRestrictionTemplate


TemporaryDeclarationRestrictionKind = Literal[
    "cant_attack",
    "cant_block",
    "cant_attack_or_block",
    "unblockable",
]

TEMPORARY_DECLARATION_RESTRICTION_KINDS = frozenset(
    {
        "cant_attack",
        "cant_block",
        "cant_attack_or_block",
        "unblockable",
    }
)


class TemporaryDeclarationRestrictionError(ValueError):
    """A temporary combat declaration restriction was malformed or stale."""


class TemporaryDeclarationRestrictionHost(Protocol):
    state: Any

    def _next_ref(self, prefix: str) -> str: ...

    def _next_zone_timestamp(self) -> int: ...


def temporary_declaration_restriction(
    kind: TemporaryDeclarationRestrictionKind | str,
) -> DeclarationRestrictionTemplate:
    """Return one of the four closed declaration fragments this owner grants."""

    if kind == "cant_attack":
        return DeclarationRestrictionTemplate(
            template_id="intrinsic-attack-prohibition-v1",
            declarations=("attack",),
            scope="self",
        )
    if kind == "cant_block":
        return DeclarationRestrictionTemplate(
            template_id="intrinsic-block-prohibition-v1",
            declarations=("block",),
            scope="self",
        )
    if kind == "cant_attack_or_block":
        return DeclarationRestrictionTemplate(
            template_id="intrinsic-attack-block-prohibition-v1",
            declarations=("attack", "block"),
            scope="self",
        )
    if kind == "unblockable":
        return DeclarationRestrictionTemplate(
            template_id="intrinsic-unblockable-v1",
            declarations=("block",),
            scope="source_option",
        )
    raise TemporaryDeclarationRestrictionError(
        f"Unsupported temporary declaration restriction {kind!r}"
    )


def commit_temporary_declaration_restriction(
    host: TemporaryDeclarationRestrictionHost,
    *,
    card: Any,
    source: ResolutionEffectSource,
    kind: TemporaryDeclarationRestrictionKind | str,
) -> ContinuousEffect:
    """Grant one locked layer-6 declaration fragment until cleanup."""

    if getattr(card, "zone", None) != "battlefield" or bool(
        getattr(card, "phased_out", False)
    ):
        raise TemporaryDeclarationRestrictionError(
            "Temporary declaration restrictions require a phased-in battlefield permanent"
        )
    if not isinstance(source, ResolutionEffectSource):
        raise TemporaryDeclarationRestrictionError(
            "Temporary declaration restrictions require typed resolution source identity"
        )
    restriction = temporary_declaration_restriction(kind)
    try:
        effect = create_resolution_continuous_effect(
            host,
            source=source,
            targets=(card,),
            layer=Layer.ABILITY,
            sublayer="6",
            operations=(
                ContinuousOperation(
                    "add_ability_fragment",
                    ability_fragment_to_dict(restriction),
                ),
            ),
            duration=ContinuousEffectDuration.UNTIL_END_OF_TURN,
        )
    except (ContinuousEffectError, ContinuousEffectStateError) as exc:
        raise TemporaryDeclarationRestrictionError(str(exc)) from exc
    if effect is None:
        raise TemporaryDeclarationRestrictionError(
            "Temporary declaration restrictions require continuous-effect state"
        )
    return effect


__all__ = [
    "TEMPORARY_DECLARATION_RESTRICTION_KINDS",
    "TemporaryDeclarationRestrictionError",
    "TemporaryDeclarationRestrictionKind",
    "commit_temporary_declaration_restriction",
    "temporary_declaration_restriction",
]
