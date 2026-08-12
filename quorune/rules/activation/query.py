from __future__ import annotations

from typing import Any, Protocol

from ...abilities import ActivatedAbility
from ...ability_fragments import (
    canonical_ability_fragments,
    granted_activated_specs,
)
from ...card_overrides.game_record_v3 import (
    historical_game_record_v3_activated_abilities,
)
from ...fixed_mana_abilities import FixedManaMode
from ...mana import BASIC_LAND_MANA
from ...util import normalize_mana_bundle


class ActivatedAbilityQueryHost(Protocol):
    semantics: Any

    def _effective_card_data(self, card: Any) -> dict[str, Any]: ...

    def _type_parts(
        self, type_line: str
    ) -> tuple[set[str], set[str], set[str]]: ...


def activated_abilities(
    host: ActivatedAbilityQueryHost,
    card: Any,
) -> tuple[ActivatedAbility, ...]:
    """Return compiler-pinned, intrinsic, and typed granted abilities."""

    data = host._effective_card_data(card)
    raw_abilities = data.get("activated_abilities", ())
    if not isinstance(raw_abilities, (list, tuple)):
        raise ValueError("activated_abilities must be an array")
    abilities = [
        value
        if isinstance(value, ActivatedAbility)
        else ActivatedAbility.from_dict(value)
        for value in raw_abilities
    ]
    if (
        not abilities
        and bool(
            getattr(
                getattr(host, "semantics", None),
                "runtime_handler_compatibility_enabled",
                False,
            )
        )
    ):
        abilities.extend(
            historical_game_record_v3_activated_abilities(card, data)
        )
    abilities.sort(key=lambda ability: ability.line_index)
    _append_intrinsic_land_abilities(host, data, abilities)
    abilities.extend(_typed_granted_abilities(data))
    return tuple(abilities)


def _typed_granted_abilities(
    data: dict[str, Any],
) -> tuple[ActivatedAbility, ...]:
    specs = granted_activated_specs(
        canonical_ability_fragments(data.get("ability_fragments", ()))
    )
    counts: dict[str, int] = {}
    result: list[ActivatedAbility] = []
    for index, spec in enumerate(specs):
        ordinal = counts.get(spec.ability_id, 0) + 1
        counts[spec.ability_id] = ordinal
        result.append(
            ActivatedAbility(
                ability_id=(
                    spec.ability_id
                    if ordinal == 1
                    else f"{spec.ability_id}#{ordinal}"
                ),
                line_index=25_000 + index,
                oracle_line=f"{spec.cost_text}: {spec.effect_text}",
                cost_text=spec.cost_text,
                effect_text=spec.effect_text,
                zones=("battlefield",),
                mana={
                    key: spec.mana_bundle.get(key, 0)
                    for key in ("GENERIC", "W", "U", "B", "R", "G", "C")
                },
                tap_source=spec.tap_source,
                sorcery_speed=spec.sorcery_speed,
                mana_ability=spec.mana_ability,
                fixed_mana_outputs=tuple(
                    FixedManaMode.from_bundle(dict(output))
                    for output in spec.fixed_mana_outputs
                ),
                builtin_semantic_key=spec.semantic_key,
            )
        )
    return tuple(result)


def _append_intrinsic_land_abilities(
    host: ActivatedAbilityQueryHost,
    data: dict[str, Any],
    abilities: list[ActivatedAbility],
) -> None:
    card_types, subtypes, _ = host._type_parts(str(data.get("type_line") or ""))
    if "land" not in card_types:
        return
    represented = {
        color
        for ability in abilities
        if ability.mana_ability
        for mode in ability.fixed_mana_outputs
        for color, amount in mode.bundle.items()
        if amount
    }
    for subtype, color in BASIC_LAND_MANA.items():
        if subtype in subtypes and color not in represented:
            abilities.append(
                ActivatedAbility(
                    ability_id=f"intrinsic_{subtype}",
                    line_index=20_000 + len(abilities),
                    oracle_line=f"{{T}}: Add {{{color}}}.",
                    cost_text="{T}",
                    effect_text=f"Add {{{color}}}.",
                    zones=("battlefield",),
                    mana=normalize_mana_bundle(None),
                    tap_source=True,
                    mana_ability=True,
                    fixed_mana_outputs=(
                        FixedManaMode.from_bundle({color: 1}),
                    ),
                )
            )
__all__ = ["ActivatedAbilityQueryHost", "activated_abilities"]
