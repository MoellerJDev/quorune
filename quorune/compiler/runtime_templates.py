from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .continuous_templates import (
    attached_fixed_characteristics_handler,
    basic_land_type_addition_handler,
    fixed_power_toughness_anthem_handler,
)
from .counter_replacement_templates import (
    static_counter_quantity_replacement_handler,
)
from .counter_maximum_templates import static_counter_maximum_handler
from .damage_templates import static_damage_handler
from .draw_templates import (
    static_draw_reveal_handler,
    static_draw_result_handler,
    static_draw_restriction_handler,
)
from .life_templates import static_life_handler
from .token_templates import static_additional_token_replacement_handler
from .trigger_participation_templates import static_trigger_multiplier_handler
from .untap_step_templates import static_untap_step_handler
from .zone_templates import static_zone_destination_replacement_handler


@dataclass(frozen=True, slots=True)
class StaticRuntimeTemplate:
    compiled: tuple[str, Mapping[str, Any], str]
    kind: str
    event: str
    dependency_reason: str


def _trigger_multiplier_template(text: str) -> StaticRuntimeTemplate | None:
    compiled = static_trigger_multiplier_handler(text)
    if compiled is None:
        return None
    return StaticRuntimeTemplate(
        compiled=compiled,
        kind="static_ability",
        event="continuous",
        dependency_reason=(
            "generic trigger multiplication depends on an untrusted "
            "rules capability"
        ),
    )


def _counter_maximum_template(
    text: str,
    *,
    source_name: str | None,
    source_is_class: bool,
) -> StaticRuntimeTemplate | None:
    if source_name is None or source_is_class:
        return None
    compiled = static_counter_maximum_handler(
        text,
        source_name=source_name,
    )
    if compiled is None:
        return None
    return StaticRuntimeTemplate(
        compiled=compiled,
        kind="static_ability",
        event="continuous",
        dependency_reason=(
            "fixed self counter maximums depend on an untrusted "
            "state-based-action capability"
        ),
    )


def _draw_template(text: str) -> StaticRuntimeTemplate | None:
    draw_reveal = static_draw_reveal_handler(text)
    if draw_reveal is not None:
        return StaticRuntimeTemplate(
            compiled=draw_reveal,
            kind="static_ability",
            event="draw.reveal_as_drawn",
            dependency_reason=(
                "generic draw reveal depends on an untrusted rules capability"
            ),
        )
    draw_restriction = static_draw_restriction_handler(text)
    if draw_restriction is not None:
        return StaticRuntimeTemplate(
            compiled=draw_restriction,
            kind="static_ability",
            event="draw.permission",
            dependency_reason=(
                "generic draw restriction depends on an untrusted rules "
                "capability"
            ),
        )
    draw_result = static_draw_result_handler(text)
    if draw_result is None:
        return None
    return StaticRuntimeTemplate(
        compiled=draw_result,
        kind="replacement_effect",
        event="draw",
        dependency_reason=(
            "generic result-draw replacement depends on an untrusted rules "
            "capability"
        ),
    )


def static_runtime_template(
    text: str,
    *,
    source_name: str | None = None,
    source_damageable: bool | None = None,
    source_permanent: bool = True,
    source_is_class: bool = False,
) -> StaticRuntimeTemplate | None:
    """Select one closed static runtime production for an Oracle line."""

    if source_permanent:
        untap_step = (
            static_untap_step_handler(text, source_name=source_name)
            if source_name is not None
            else None
        )
        if untap_step is not None:
            return StaticRuntimeTemplate(
                compiled=untap_step,
                kind="static_ability",
                event="untap.step",
                dependency_reason=(
                    "generic untap-step participation requires its closed "
                    "typed runtime capability"
                ),
            )
        counter_maximum = _counter_maximum_template(
            text,
            source_name=source_name,
            source_is_class=source_is_class,
        )
        if counter_maximum is not None:
            return counter_maximum
        trigger_multiplier = _trigger_multiplier_template(text)
        if trigger_multiplier is not None:
            return trigger_multiplier
        counter_quantity = (
            None
            if source_is_class
            else static_counter_quantity_replacement_handler(text)
        )
        if counter_quantity is not None:
            return StaticRuntimeTemplate(
                compiled=counter_quantity,
                kind="replacement_effect",
                event="counter.place",
                dependency_reason=(
                    "generic counter-quantity replacement depends on an "
                    "untrusted rules capability"
                ),
            )
        additional_token = static_additional_token_replacement_handler(text)
        if additional_token is not None:
            return StaticRuntimeTemplate(
                compiled=additional_token,
                kind="replacement_effect",
                event="token.create",
                dependency_reason=(
                    "generic additional-token replacement depends on an "
                    "untrusted rules capability"
                ),
            )
        zone_replacement = static_zone_destination_replacement_handler(text)
        if zone_replacement is not None:
            return StaticRuntimeTemplate(
                compiled=zone_replacement,
                kind="replacement_effect",
                event="zone.change",
                dependency_reason=(
                    "generic destination replacement depends on an untrusted "
                    "rules capability"
                ),
            )
        draw = _draw_template(text)
        if draw is not None:
            return draw

    attached_characteristics = attached_fixed_characteristics_handler(text)
    if attached_characteristics is not None:
        return StaticRuntimeTemplate(
            compiled=attached_characteristics,
            kind="static_ability",
            event="characteristics.evaluate",
            dependency_reason=(
                "generic attached characteristics depend on an untrusted "
                "continuous-effect capability"
            ),
        )

    basic_land_type = basic_land_type_addition_handler(text)
    if basic_land_type is not None:
        return StaticRuntimeTemplate(
            compiled=basic_land_type,
            kind="static_ability",
            event="characteristics.evaluate",
            dependency_reason=(
                "generic basic-land-type addition depends on an untrusted "
                "rules capability"
            ),
        )
    fixed_anthem = fixed_power_toughness_anthem_handler(text)
    if fixed_anthem is not None:
        return StaticRuntimeTemplate(
            compiled=fixed_anthem,
            kind="static_ability",
            event="characteristics.evaluate",
            dependency_reason=(
                "generic fixed anthem depends on an untrusted continuous-effect capability"
            ),
        )
    static_life = static_life_handler(text)
    if static_life is not None:
        return StaticRuntimeTemplate(
            compiled=static_life,
            kind="replacement_effect",
            event="life.change",
            dependency_reason=(
                "generic life-gain replacement depends on an untrusted "
                "rules capability"
            ),
        )
    static_damage = static_damage_handler(text)
    if static_damage is None:
        return None
    if (
        static_damage[1]["handler_id"]
        == "replacement.damage.redirect-to-source.v1"
        and source_damageable is False
    ):
        # Damage can be redirected only to an object that can receive damage.
        # Keeping this type check at compilation prevents a future artifact or
        # enchantment with superficially similar wording from being promoted
        # to a trusted program that can only fail at runtime.
        return None
    return StaticRuntimeTemplate(
        compiled=static_damage,
        kind=(
            "prevention_effect"
            if static_damage[1]["handler_id"].startswith("prevention.")
            else "replacement_effect"
        ),
        event="damage",
        dependency_reason=(
            "generic damage replacement depends on an untrusted rules "
            "capability"
        ),
    )
