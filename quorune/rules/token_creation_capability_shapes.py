from __future__ import annotations

"""Strict capability shape for fixed-definition token instructions."""

import re
from typing import Any, Mapping, Sequence

from ..compiler.token_templates import fixed_token_creation_effect_template


_TOKEN_MECHANIC = "cr-111-tokens"
_COLOR_ORDER = "WUBRG"
_CREATURE_KEYWORDS = frozenset(
    {
        "Deathtouch",
        "Defender",
        "Double Strike",
        "First Strike",
        "Flying",
        "Haste",
        "Hexproof",
        "Indestructible",
        "Lifelink",
        "Menace",
        "Reach",
        "Trample",
        "Vigilance",
    }
)
_PREDEFINED_CAPABILITIES = {
    "Treasure": ("mana.activated.fixed_output",),
    "Food": ("life.change.effect",),
    "Map": ("keyword_action.explore.single",),
}
_AUXILIARY_MECHANICS = frozenset(
    {
        "activated_ability",
        "cr-603-handling-triggered-abilities",
        "exhaust",
        "generated_oracle_ir",
        "spell_resolution",
        "triggered_ability",
    }
)


def _token_specific_mechanics(mechanics: set[str]) -> set[str]:
    """Exclude independently gated trigger and activation scaffolding."""

    return {
        mechanic
        for mechanic in mechanics
        if mechanic not in _AUXILIARY_MECHANICS
        and not mechanic.startswith("trigger-event-")
    }


def _fixed_predefined_effect_is_closed(
    effect: Mapping[str, Any],
) -> tuple[str, ...]:
    name = effect.get("name")
    if name not in _PREDEFINED_CAPABILITIES:
        return ()
    expected = fixed_token_creation_effect_template(
        f"Create a {name} token."
    )
    if expected is None:
        return ()
    canonical = dict(expected.effect)
    supplied = dict(effect)
    supplied["quantity"] = 1
    supplied.pop("tapped", None)
    if supplied != canonical:
        return ()
    return (
        "token.creation.fixed_definition",
        *_PREDEFINED_CAPABILITIES[str(name)],
    )


def _fixed_creature_effect_is_closed(
    effect: Mapping[str, Any],
    mechanics: set[str],
) -> bool:
    characteristics = effect.get("characteristics")
    if not isinstance(characteristics, Mapping):
        return False
    allowed = {"type_line", "colors", "power", "toughness", "keywords"}
    required = {"type_line", "colors", "power", "toughness"}
    if not required.issubset(characteristics) or set(characteristics) - allowed:
        return False
    name = effect.get("name")
    if not isinstance(name, str) or re.fullmatch(
        r"[A-Z][A-Za-z']*(?:[ -][A-Z][A-Za-z']*)*", name
    ) is None:
        return False
    if re.fullmatch(
        rf"Token (?:Artifact )?Creature — {re.escape(name)}",
        str(characteristics.get("type_line") or ""),
    ) is None:
        return False
    colors = characteristics.get("colors")
    if (
        not isinstance(colors, list)
        or len(colors) > 2
        or any(color not in _COLOR_ORDER for color in colors)
        or colors != sorted(set(colors), key=_COLOR_ORDER.index)
    ):
        return False
    for field in ("power", "toughness"):
        value = characteristics.get(field)
        if not isinstance(value, str) or not value.isdigit():
            return False
    keywords = characteristics.get("keywords", [])
    if (
        not isinstance(keywords, list)
        or any(keyword not in _CREATURE_KEYWORDS for keyword in keywords)
        or len(keywords) != len(set(keywords))
    ):
        return False
    expected_mechanics = {
        _TOKEN_MECHANIC,
        *(keyword.casefold() for keyword in keywords),
    }
    return _token_specific_mechanics(mechanics) == expected_mechanics


def fixed_token_creation_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: set[str],
) -> tuple[str, ...]:
    """Recognize one compiler-owned fixed token creation effect."""

    if target_schema is not None or len(effects) != 1:
        return ()
    effect = effects[0]
    expected_fields = {
        "op",
        "controller",
        "name",
        "quantity",
        "characteristics",
    }
    if "tapped" in effect:
        expected_fields.add("tapped")
    if set(effect) != expected_fields:
        return ()
    if (
        effect.get("op") != "create_token"
        or effect.get("controller") != "$controller"
    ):
        return ()
    quantity = effect.get("quantity")
    if type(quantity) is not int or quantity <= 0:
        return ()
    if "tapped" in effect and effect.get("tapped") is not True:
        return ()
    if _token_specific_mechanics(mechanic_ids) == {_TOKEN_MECHANIC}:
        predefined = _fixed_predefined_effect_is_closed(effect)
        if predefined:
            return predefined
    if _fixed_creature_effect_is_closed(effect, mechanic_ids):
        return ("token.creation.fixed_definition",)
    return ()


__all__ = ["fixed_token_creation_node_capabilities"]
