from __future__ import annotations

from typing import Any

from ..counter_keyword_abilities import (
    FIXED_COUNTER_KEYWORD_MECHANICS,
    compile_fixed_counter_keyword_ability,
    fixed_counter_keyword_handler_descriptor,
)
from ..rules.capabilities import CapabilityRegistry
from .activated_costs import activated_ability_cost
from .dependency_gate import explicit_capabilities_gate
from .ir_model import OracleNode, OracleResidual, SourceSpan, append_residual


def fixed_counter_keyword_activation_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    printed_power: str | None,
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> OracleNode | None:
    if len(mechanics) != 1 or mechanics[0] not in FIXED_COUNTER_KEYWORD_MECHANICS:
        return None
    spec = compile_fixed_counter_keyword_ability(
        material_line=material_line,
        oracle_line=line,
        line_index=span.line - 1,
        mechanic=mechanics[0],
        printed_power=printed_power,
    )
    if spec is None:
        residual_id = append_residual(
            residuals,
            kind="unsupported_fixed_counter_keyword_activation",
            text=line,
            span=span,
            reason=(
                "Counter-keyword activation is outside the closed fixed "
                "ordinary-mana and positive-integer grammar"
            ),
            blockers=(
                "variable, hybrid, Phyrexian, snow, or nonmana costs",
                "variable or nonpositive counter quantities",
                "Scavenge without fixed positive printed integral power",
                "granted, copied, face-changed, or text-changing abilities",
            ),
        )
        return OracleNode(
            node_id=node_id,
            kind="activated_ability",
            text=line,
            span=span,
            active_zone={
                "level up": "battlefield",
                "outlast": "battlefield",
                "reinforce": "hand",
                "scavenge": "graveyard",
            }[mechanics[0]],
            event="activate",
            lowerable=False,
            exact=False,
            template_id="fixed-counter-keyword-activation-residual-v1",
            mechanics=mechanics,
            residual_ids=(residual_id,),
        )
    capabilities = [
        "activation.counter_keyword.fixed",
        "counter.producer.fixed_effect",
    ]
    if spec.has_zone_change_source_cost:
        capabilities.append("activation.source_zone_change.fixed")
    if spec.targets_creature:
        capabilities.append("target.revalidate_resolution")
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
                    "fixed counter-keyword activation lacks a trusted "
                    "capability closure"
                ),
                blockers=gate.blockers,
            ),
        )
        if gate.blockers
        else ()
    )
    ability = spec.to_activated_ability()
    target_schema = (
        dict(ability.target_schema) if ability.target_schema is not None else None
    )
    effect = {
        "op": "place_counters",
        "card": "$target.0" if spec.targets_creature else "$source.zone_object",
        "counter": spec.counter_name,
        "amount": spec.amount,
        "source": "$source",
    }
    mechanic_coverage = (
        *mechanics,
        "cr-122-counters",
        *( ("cr-115-targets",) if spec.targets_creature else () ),
    )
    return OracleNode(
        node_id=node_id,
        kind="activated_ability",
        text=line,
        span=span,
        active_zone=spec.active_zone,
        event="activate",
        lowerable=True,
        exact=not residual_ids,
        template_id=f"fixed-{spec.mechanic.replace(' ', '-')}-activation-v1",
        cost=activated_ability_cost(ability),
        effects=(effect,),
        handlers=(fixed_counter_keyword_handler_descriptor(spec),),
        target_schema=target_schema,
        mechanics=mechanic_coverage,
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


__all__ = ["fixed_counter_keyword_activation_node"]
