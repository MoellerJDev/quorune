from __future__ import annotations

"""Closed Oracle-IR lowering for fixed-output activated mana abilities."""

from dataclasses import replace
import re
from typing import Any, Callable, Mapping, Sequence

from ..activation_usage import ActivationLimit
from ..abilities import parse_activated_abilities
from ..color_set_mana_abilities import (
    color_set_mana_handler_descriptor,
    compile_color_set_activated_mana_ability,
)
from ..fixed_mana_abilities import (
    compile_fixed_activated_mana_ability,
    fixed_mana_handler_descriptor,
)
from ..rules.capabilities import CapabilityRegistry
from .activated_costs import activated_ability_cost
from .dependency_gate import (
    DependencyGate,
    dependency_gate,
    explicit_capabilities_gate,
)
from .ir_model import (
    append_residual,
    OracleNode,
    OracleResidual,
    SourceSpan,
)


def fixed_activated_mana_node(
    ability: Any,
    node_id: str,
    line: str,
    span: SourceSpan,
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> tuple[Any, OracleNode | None]:
    ability = replace(
        ability,
        ability_id=f"ab{span.line}",
        line_index=span.line - 1,
    )
    reminder_line = line.strip()
    reminder_only = (
        reminder_line.startswith("(") and reminder_line.endswith(")")
    )
    spec = (
        None
        if reminder_only
        else compile_fixed_activated_mana_ability(ability)
    )
    if spec is None:
        return ability, None
    capabilities = ["mana.activated.fixed_output"]
    if ability.activation_limit is ActivationLimit.EXHAUST_ONCE:
        capabilities.append("activation.exhaust.once_per_object")
    gate = explicit_capabilities_gate(
        capabilities,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    residual_ids = (
        (
            append_residual(
                residuals,
                kind="dependency_contract",
                text=line,
                span=span,
                reason=(
                    "fixed-output activated mana ability lacks a trusted "
                    "capability closure"
                ),
                blockers=gate.blockers,
            ),
        )
        if gate.blockers
        else ()
    )
    return ability, OracleNode(
        node_id=node_id,
        kind="mana_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="activate",
        lowerable=True,
        exact=not gate.blockers,
        template_id="activated-mana-fixed-output-v1",
        cost=activated_ability_cost(ability),
        handlers=(fixed_mana_handler_descriptor(spec),),
        mechanics=(
            ("exhaust",)
            if ability.activation_limit is ActivationLimit.EXHAUST_ONCE
            else ()
        ),
        residual_ids=residual_ids,
        capability_dependencies=gate.capabilities,
        capability_closure=(
            gate.closure.reachable if gate.closure is not None else ()
        ),
        capability_profile=(
            gate.closure.profile if gate.closure is not None else None
        ),
        capability_fingerprint=(
            gate.closure.fingerprint if gate.closure is not None else None
        ),
    )


def color_set_activated_mana_node(
    ability: Any,
    node_id: str,
    line: str,
    span: SourceSpan,
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> OracleNode | None:
    spec = compile_color_set_activated_mana_ability(ability)
    if spec is None:
        return None
    capabilities = ["mana.activated.color_set"]
    if ability.activation_limit is ActivationLimit.EXHAUST_ONCE:
        capabilities.append("activation.exhaust.once_per_object")
    gate = explicit_capabilities_gate(
        capabilities,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    residual_ids = (
        (
            append_residual(
                residuals,
                kind="dependency_contract",
                text=line,
                span=span,
                reason=(
                    "color-set activated mana ability lacks a trusted "
                    "capability closure"
                ),
                blockers=gate.blockers,
            ),
        )
        if gate.blockers
        else ()
    )
    return OracleNode(
        node_id=node_id,
        kind="mana_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="activate",
        lowerable=True,
        exact=not gate.blockers,
        template_id="activated-mana-color-set-v1",
        cost=activated_ability_cost(ability),
        handlers=(color_set_mana_handler_descriptor(spec),),
        mechanics=(
            ("exhaust",)
            if ability.activation_limit is ActivationLimit.EXHAUST_ONCE
            else ()
        ),
        residual_ids=residual_ids,
        capability_dependencies=gate.capabilities,
        capability_closure=(
            gate.closure.reachable if gate.closure is not None else ()
        ),
        capability_profile=(
            gate.closure.profile if gate.closure is not None else None
        ),
        capability_fingerprint=(
            gate.closure.fingerprint if gate.closure is not None else None
        ),
    )


def unresolved_activated_mana_residual(
    ability: Any,
    span: SourceSpan,
    residuals: list[OracleResidual],
    *,
    source_line: str | None = None,
) -> str:
    reminder_text = str(source_line or ability.oracle_line).strip()
    reminder_only = (
        reminder_text.startswith("(") and reminder_text.endswith(")")
    )
    return append_residual(
        residuals,
        kind="mana_ability",
        text=ability.effect_text,
        span=span,
        reason=(
            "parenthesized mana reminder text requires the separate intrinsic "
            "basic-land-type ability owner"
            if reminder_only
            else "activated mana ability is outside the typed fixed-output grammar"
        ),
        blockers=(
            *(
                ("intrinsic basic-land-type mana capability",)
                if reminder_only
                else ()
            ),
            "dynamic or conditional mana output",
            "restricted mana or effect-clause side effects",
            "unrepresented activation-cost variant",
        ),
    )


def _activated_effect_residuals(
    *,
    ability: Any,
    template: str | None,
    line: str,
    span: SourceSpan,
    residuals: list[OracleResidual],
) -> list[str]:
    residual_ids: list[str] = []
    if not ability.compiled_cost:
        residual_ids.append(
            append_residual(
                residuals,
                kind="cost",
                text=ability.cost_text,
                span=span,
                reason="mandatory activated cost is not compiled",
                blockers=(
                    "complete alternate/additional-cost grammar",
                    "restricted payment predicates",
                ),
            )
        )
    if template is None and not ability.mana_ability:
        residual_ids.append(
            append_residual(
                residuals,
                kind="effect",
                text=ability.effect_text,
                span=span,
                reason="activated effect has no exact generic template",
            )
        )
    if ability.mana_ability:
        residual_ids.append(
            unresolved_activated_mana_residual(
                ability, span, residuals, source_line=line
            )
        )
    return residual_ids


def _activated_effect_dependency_gate(
    *,
    effects: tuple[Mapping[str, Any], ...],
    target_schema: Mapping[str, Any] | None,
    mechanics: tuple[str, ...],
    trusted_mechanics: frozenset[str],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
) -> DependencyGate:
    capability_shaped_effect = (
        len(effects) == 1
        and str(effects[0].get("op") or "")
        in {
            "amass",
            "bounce",
            "counter_stack_target",
            "damage",
            "damage_each_opponent",
            "draw",
            "draw_each_player",
            "draw_with_actions",
            "destroy",
            "destroy_all",
            "exile_permanent",
            "explore",
            "offer_draw",
            "proliferate",
            "place_counters",
            "place_counter_batch",
            "place_counters_on_set",
            "place_counters_on_targets",
            "place_player_counters",
            "remove_counters",
            "remove_all_counters",
            "return_graveyard_card_to_owner_hand",
            "fixed_self_counter_keyword_action",
            "fixed_bolster",
            "life",
            "lose_life",
            "lose_life_each_opponent",
            "scry",
            "tap",
            "untap",
        }
    )
    closed_target_sequence = (
        bool(
            {
                "fixed-target-effect-sequence",
                "fixed-source-effect-sequence",
                "fixed-controller-effect-sequence",
            }.intersection(mechanics)
        )
        or (
            len(effects) >= 1
            and all(
                str(effect.get("op") or "")
                in {
                    "grant_keyword_until_end_of_turn",
                    "modify_stats_until_end_of_turn",
                }
                for effect in effects
            )
            and {
                "cr-115-targets",
                "cr-611-continuous-effects",
            }.issubset(mechanics)
        )
    )
    if (
        capability_shaped_effect or closed_target_sequence
    ) and capability_registry is not None:
        return dependency_gate(
            mechanics=mechanics,
            effects=effects,
            target_schema=target_schema,
            trusted_mechanics=trusted_mechanics,
            capability_registry=capability_registry,
            capability_profile=capability_profile,
        )
    return DependencyGate(
        blockers=tuple(
            f"mechanic:{mechanic}"
            for mechanic in sorted(set(mechanics) - trusted_mechanics)
        )
    )


def _activated_cost_dependency_gate(
    ability: Any,
    gate: DependencyGate,
    *,
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
) -> DependencyGate:
    """Add closed typed cost ownership without weakening effect blockers."""

    additional: list[str] = []
    if ability.loyalty_delta is not None and ability.loyalty_delta > 0:
        additional.append("activation.loyalty.positive_counter_cost")
    if ability.activation_limit is ActivationLimit.EXHAUST_ONCE:
        additional.append("activation.exhaust.once_per_object")
    if not additional:
        return gate
    cost_gate = explicit_capabilities_gate(
        (*gate.capabilities, *additional),
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    return DependencyGate(
        blockers=tuple(sorted(set((*gate.blockers, *cost_gate.blockers)))),
        capabilities=cost_gate.capabilities,
        closure=cost_gate.closure,
    )


def _dependency_metadata(
    gate: DependencyGate,
) -> tuple[tuple[str, ...], str | None, str | None]:
    if gate.closure is None:
        return (), None, None
    return gate.closure.reachable, gate.closure.profile, gate.closure.fingerprint


def _activated_effect_material(ability: Any) -> str:
    material = ability.effect_text
    if not ability.sorcery_speed:
        return material
    return re.sub(
        r"\.?\s*activate only as a sorcery\.?$",
        "",
        material,
        flags=re.IGNORECASE,
    ).strip()


def activated_oracle_node(
    *,
    node_id: str,
    line: str,
    span: SourceSpan,
    card_name: str,
    keywords: Sequence[str],
    trusted_mechanics: frozenset[str],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
    effect_template: Callable[..., tuple[
        str | None,
        tuple[Mapping[str, Any], ...],
        Mapping[str, Any] | None,
        tuple[str, ...],
    ]],
) -> OracleNode | None:
    """Compile one complete colon-form activated-ability Oracle line."""

    reminder_line = line.strip()
    if (
        reminder_line.casefold().startswith("({t}: add ")
        and reminder_line.endswith(")")
    ):
        residual_id = append_residual(
            residuals,
            kind="mana_ability",
            text=line,
            span=span,
            reason=(
                "parenthesized mana reminder text is nonexecuting and "
                "requires the separate intrinsic basic-land-type ability "
                "owner"
            ),
            blockers=("intrinsic basic-land-type mana capability",),
        )
        return OracleNode(
            node_id=node_id,
            kind="reminder_text",
            text=line,
            span=span,
            active_zone="all",
            event="none",
            lowerable=False,
            exact=False,
            template_id="basic-land-mana-reminder-residual-v1",
            residual_ids=(residual_id,),
        )
    abilities = parse_activated_abilities(
        card_name=card_name,
        oracle_text=line,
        keywords=keywords,
    )
    if not abilities:
        return None
    ability, fixed_mana = fixed_activated_mana_node(
        abilities[0], node_id, line, span, capability_registry,
        capability_profile, residuals,
    )
    if fixed_mana is not None:
        return fixed_mana
    color_set_mana = color_set_activated_mana_node(
        ability,
        node_id,
        line,
        span,
        capability_registry,
        capability_profile,
        residuals,
    )
    if color_set_mana is not None:
        return color_set_mana
    template, effects, target_schema, mechanics = effect_template(
        _activated_effect_material(ability),
        card_name=card_name,
    )
    if ability.activation_limit is ActivationLimit.EXHAUST_ONCE:
        mechanics = tuple(dict.fromkeys((*mechanics, "exhaust")))
    residual_ids = _activated_effect_residuals(
        ability=ability,
        template=template,
        line=line,
        span=span,
        residuals=residuals,
    )
    lowerable = not residual_ids and (
        template is not None or ability.mana_ability
    )
    dependencies = mechanics if template is not None else ()
    gate = _activated_effect_dependency_gate(
        effects=effects,
        target_schema=target_schema,
        mechanics=dependencies,
        trusted_mechanics=trusted_mechanics,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    gate = _activated_cost_dependency_gate(
        ability,
        gate,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    if lowerable and gate.blockers:
        residual_ids.append(
            append_residual(
                residuals,
                kind="dependency_contract",
                text=line,
                span=span,
                reason=(
                    "lowerable ability depends on untrusted mechanic contracts"
                ),
                blockers=gate.blockers,
            )
        )
    closure, profile, fingerprint = _dependency_metadata(gate)
    return OracleNode(
        node_id=node_id,
        kind=(
            "mana_ability" if ability.mana_ability else "activated_ability"
        ),
        text=line,
        span=span,
        active_zone=ability.zones[0],
        event="activate",
        lowerable=lowerable,
        exact=lowerable and not gate.blockers,
        template_id=(
            "intrinsic-mana-ability-v1"
            if ability.mana_ability and template is None
            else template
        ),
        cost=activated_ability_cost(ability),
        effects=effects,
        target_schema=target_schema,
        mechanics=mechanics,
        residual_ids=tuple(residual_ids),
        capability_dependencies=gate.capabilities,
        capability_closure=closure,
        capability_profile=profile,
        capability_fingerprint=fingerprint,
    )


__all__ = [
    "activated_oracle_node",
    "fixed_activated_mana_node",
    "unresolved_activated_mana_residual",
]
