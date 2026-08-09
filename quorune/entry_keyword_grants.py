from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from .continuous_effects import (
    ContinuousEffect,
    ContinuousEffectDuration,
    ContinuousEffectOrigin,
    ContinuousObjectIdentity,
    ContinuousOperation,
    Layer,
)
from .continuous_effect_state import (
    commit_continuous_effect,
    ContinuousEffectStateError,
)
from .object_predicate import ObjectQuerySpec


class EntryKeywordGrantError(ValueError):
    pass


@dataclass(frozen=True, slots=True, order=True)
class EntryKeywordGrant:
    effect_id: str
    keyword: str
    sequence: int = 0

    def __post_init__(self) -> None:
        if type(self.effect_id) is not str or not self.effect_id:
            raise EntryKeywordGrantError(
                "Entry keyword grants require replacement effect identity"
            )
        if type(self.keyword) is not str:
            raise EntryKeywordGrantError(
                "Entry keyword grants require a string keyword"
            )
        keyword = " ".join(self.keyword.casefold().split())
        if keyword not in {"haste"}:
            raise EntryKeywordGrantError(
                "Entry keyword grant is outside the represented vocabulary"
            )
        if type(self.sequence) is not int or self.sequence < 0:
            raise EntryKeywordGrantError(
                "Entry keyword grant sequence must be nonnegative"
            )
        object.__setattr__(self, "keyword", keyword)


class EntryKeywordGrantHost(Protocol):
    state: Any

    def _next_zone_timestamp(self) -> int: ...


def commit_entry_keyword_grants(
    host: EntryKeywordGrantHost,
    card: Any,
    grants: Sequence[EntryKeywordGrant],
) -> tuple[ContinuousEffect, ...]:
    """Commit replacement-created layer-6 grants to the entering zone object."""

    journal = host.state.continuous_effects
    if journal is None:
        raise EntryKeywordGrantError(
            "Entry keyword grants require continuous-effect state"
        )
    if getattr(card, "zone", None) != "battlefield":
        if grants:
            raise EntryKeywordGrantError(
                "Entry keyword grants require the affected object on the battlefield"
            )
        return ()
    result: list[ContinuousEffect] = []
    for grant in grants:
        if not isinstance(grant, EntryKeywordGrant):
            raise EntryKeywordGrantError(
                "Entry keyword grants require typed instructions"
            )
        effect = ContinuousEffect(
            effect_id=(
                f"entry-keyword:{grant.effect_id}:"
                f"{card.logical_object_id}:{grant.sequence}"
            ),
            source_id=grant.effect_id,
            layer=Layer.ABILITY,
            sublayer="6",
            timestamp=host._next_zone_timestamp(),
            operations=(ContinuousOperation("add_ability", grant.keyword),),
            origin=ContinuousEffectOrigin.REPLACEMENT,
            duration=ContinuousEffectDuration.ZONE_OBJECT,
            applies=ObjectQuerySpec(zones=("battlefield",)),
            locked_objects=(
                ContinuousObjectIdentity(
                    object_id=card.object_id,
                    logical_object_id=card.logical_object_id,
                ),
            ),
        )
        try:
            commit_continuous_effect(host.state, effect)
        except ContinuousEffectStateError as exc:
            raise EntryKeywordGrantError(str(exc)) from exc
        result.append(effect)
    return tuple(result)


__all__ = [
    "EntryKeywordGrant",
    "EntryKeywordGrantError",
    "commit_entry_keyword_grants",
]
