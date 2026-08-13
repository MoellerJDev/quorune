from __future__ import annotations

from typing import Any, Mapping, Protocol

from .ability_fragments import canonical_ability_fragments
from .characteristic_fragments import (
    CharacteristicCountKind,
    ConditionalKeywordSpec,
    DynamicPowerToughnessSpec,
    PowerToughnessCalculation,
)
from .util import unique_preserving_order


class DynamicCharacteristicHost(Protocol):
    state: Any

    def _copyable_characteristics(self, card: Any) -> Mapping[str, Any]: ...

    def _type_parts(
        self, type_line: str
    ) -> tuple[set[str], set[str], set[str]]: ...


def _has_card_type(
    host: DynamicCharacteristicHost,
    card: Any,
    card_type: str,
) -> bool:
    copyable = host._copyable_characteristics(card)
    return card_type in host._type_parts(
        str(copyable.get("type_line") or "")
    )[0]


def _matching_count(
    host: DynamicCharacteristicHost,
    card: Any,
    kind: CharacteristicCountKind,
) -> int:
    if kind is CharacteristicCountKind.CONTROLLER_BATTLEFIELD_ARTIFACTS:
        object_ids = host.state.players[card.controller].zones["battlefield"]
        return sum(
            1
            for object_id in object_ids
            if not host.state.cards[object_id].phased_out
            and _has_card_type(
                host,
                host.state.cards[object_id],
                "artifact",
            )
        )
    object_ids = host.state.players[card.owner].zones["graveyard"]
    card_type = (
        "creature"
        if kind
        is CharacteristicCountKind.OWNER_GRAVEYARD_CREATURE_CARDS
        else "land"
    )
    return sum(
        1
        for object_id in object_ids
        if _has_card_type(host, host.state.cards[object_id], card_type)
    )


def _modify_power_toughness(
    result: dict[str, Any],
    *,
    power: int,
    toughness: int,
    multiplier: int,
) -> None:
    for field, amount in (("power", power), ("toughness", toughness)):
        try:
            result[field] = str(
                int(str(result.get(field))) + amount * multiplier
            )
        except (TypeError, ValueError):
            continue


def apply_dynamic_characteristic_fragments(
    host: DynamicCharacteristicHost,
    card: Any,
    characteristics: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply compiled live-state fragments without interpreting rules prose."""

    result = dict(characteristics)
    if card.zone != "battlefield" or card.phased_out:
        return result
    fragments = canonical_ability_fragments(
        result.get("ability_fragments", ())
    )
    for fragment in fragments:
        if isinstance(fragment, ConditionalKeywordSpec):
            if any(
                seat != card.controller
                and player.in_game
                and player.life <= fragment.opponent_life_at_most
                for seat, player in host.state.players.items()
            ):
                result["keywords"] = unique_preserving_order(
                    [*result.get("keywords", ()), fragment.keyword]
                )
            continue
        if not isinstance(fragment, DynamicPowerToughnessSpec):
            continue
        count = _matching_count(host, card, fragment.count_kind)
        multiplier = (
            count
            if fragment.calculation
            is PowerToughnessCalculation.PER_MATCHING_OBJECT
            else int(count >= fragment.minimum_count)
        )
        _modify_power_toughness(
            result,
            power=fragment.power,
            toughness=fragment.toughness,
            multiplier=multiplier,
        )
    return result


__all__ = [
    "DynamicCharacteristicHost",
    "apply_dynamic_characteristic_fragments",
]
