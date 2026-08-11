from __future__ import annotations

from ..echo import (
    ECHO_CONTROL_CONDITION_FIELD,
    ECHO_MECHANIC_ID,
    compile_fixed_mana_echo,
)
from ..rules.capabilities import CapabilityRegistry
from .dependency_gate import explicit_capability_gate
from .ir_model import append_residual, OracleNode, OracleResidual, SourceSpan


def fixed_mana_echo_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> OracleNode | None:
    """Lower the closed ordinary fixed-mana Echo family."""

    if mechanics != (ECHO_MECHANIC_ID,):
        return None
    spec = compile_fixed_mana_echo(material_line)
    if spec is None:
        residual_id = append_residual(
            residuals,
            kind="unsupported_echo_cost",
            text=line,
            span=span,
            reason="Echo cost is outside the closed fixed ordinary mana grammar",
            blockers=(
                "alternative, snow, hybrid, Phyrexian, and variable costs",
                "nonmana costs, modifiers, and compound keyword wording",
            ),
        )
        return OracleNode(
            node_id=node_id,
            kind="triggered_ability",
            text=line,
            span=span,
            active_zone="battlefield",
            event="step.begin",
            lowerable=False,
            exact=False,
            template_id="fixed-mana-echo-residual-v1",
            mechanics=mechanics,
            residual_ids=(residual_id,),
        )
    gate = explicit_capability_gate(
        "trigger.keyword.echo.fixed_mana",
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
                reason="fixed-mana Echo lacks a trusted capability closure",
                blockers=gate.blockers,
            ),
        )
        if gate.blockers
        else ()
    )
    return OracleNode(
        node_id=node_id,
        kind="triggered_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="step.begin",
        event_condition={
            "all": [
                {"field": "step", "op": "eq", "value": "upkeep"},
                {
                    "field": ECHO_CONTROL_CONDITION_FIELD,
                    "op": "truthy",
                },
            ]
        },
        lowerable=True,
        exact=not residual_ids,
        template_id="fixed-mana-echo-v1",
        effects=(spec.effect_descriptor(),),
        runtime_coverage=("intervening_condition",),
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


__all__ = ["fixed_mana_echo_node"]
