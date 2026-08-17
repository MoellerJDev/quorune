from __future__ import annotations

from typing import Any

from ..rules.capabilities import CapabilityRegistry
from ..unearth import (
    compile_ordinary_unearth_ability,
    ordinary_unearth_handler_descriptor,
    UNEARTH_CAPABILITY_ID,
    UNEARTH_EFFECT_OPERATION,
    UNEARTH_MECHANIC_ID,
)
from .activated_costs import activated_ability_cost
from .dependency_gate import explicit_capability_gate
from .ir_model import append_residual, OracleNode, OracleResidual, SourceSpan


def ordinary_unearth_keyword_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
    **_unused: Any,
) -> OracleNode | None:
    """Lower one fixed ordinary-mana Unearth ability or fail closed."""

    if mechanics != (UNEARTH_MECHANIC_ID,):
        return None
    spec = compile_ordinary_unearth_ability(
        material_line=material_line,
        oracle_line=line,
        line_index=span.line - 1,
    )
    if spec is None:
        residual_id = append_residual(
            residuals,
            kind="unsupported_unearth_cost",
            text=line,
            span=span,
            reason="Unearth cost is outside the fixed ordinary-mana grammar",
            blockers=(
                "variable, hybrid, Phyrexian, snow, and nonmana Unearth costs",
                "copied, granted, modified, and multiple Unearth instances",
            ),
        )
        return OracleNode(
            node_id=node_id,
            kind="activated_ability",
            text=line,
            span=span,
            active_zone="graveyard",
            event="activate",
            lowerable=False,
            exact=False,
            template_id="ordinary-unearth-residual-v1",
            mechanics=mechanics,
            residual_ids=(residual_id,),
        )
    gate = explicit_capability_gate(
        UNEARTH_CAPABILITY_ID,
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
                reason="ordinary Unearth lacks a trusted capability closure",
                blockers=gate.blockers,
            ),
        )
        if gate.blockers
        else ()
    )
    return OracleNode(
        node_id=node_id,
        kind="activated_ability",
        text=line,
        span=span,
        active_zone="graveyard",
        event="activate",
        lowerable=True,
        exact=not residual_ids,
        template_id="ordinary-fixed-mana-unearth-v1",
        cost=activated_ability_cost(spec.to_activated_ability()),
        effects=({"op": UNEARTH_EFFECT_OPERATION, "action": "return"},),
        handlers=(ordinary_unearth_handler_descriptor(spec),),
        runtime_coverage=(
            "graveyard_activation",
            "zone_object_haste",
            "unearth_leave_replacement",
            "delayed_end_step_exile",
        ),
        mechanics=mechanics,
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


__all__ = ["ordinary_unearth_keyword_node"]
