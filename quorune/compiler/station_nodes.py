from __future__ import annotations

from ..rules.capabilities import CapabilityRegistry
from ..station import (
    STATION_CAPABILITY_ID,
    STATION_MECHANIC_ID,
    compile_ordinary_station_ability,
    ordinary_station_handler_descriptor,
)
from .activated_costs import activated_ability_cost
from .dependency_gate import explicit_capability_gate
from .ir_model import append_residual, OracleNode, OracleResidual, SourceSpan


def ordinary_station_keyword_node(
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
    """Lower one source-spanned ordinary printed Station activation."""

    if mechanics != (STATION_MECHANIC_ID,):
        return None
    spec = compile_ordinary_station_ability(
        material_line=material_line,
        oracle_line=line,
        line_index=span.line - 1,
    )
    if spec is None:
        residual_id = append_residual(
            residuals,
            kind="unsupported_station_ability",
            text=line,
            span=span,
            reason="Station is outside the ordinary printed keyword grammar",
            blockers=(
                "modified or alternate Station activation costs",
                "toughness-substitution and other Station result modifiers",
                "granted, copied, removed, or text-changing Station",
                "cost-creature phasing before resolution",
            ),
        )
        return OracleNode(
            node_id=node_id,
            kind="activated_ability",
            text=line,
            span=span,
            active_zone="battlefield",
            event="activate",
            lowerable=False,
            exact=False,
            template_id="ordinary-station-residual-v1",
            mechanics=mechanics,
            residual_ids=(residual_id,),
        )
    gate = explicit_capability_gate(
        STATION_CAPABILITY_ID,
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
                reason="ordinary Station lacks trusted capability closure",
                blockers=gate.blockers,
            ),
        )
        if gate.blockers
        else ()
    )
    ability = spec.to_activated_ability()
    return OracleNode(
        node_id=node_id,
        kind="activated_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="activate",
        lowerable=True,
        exact=not residual_ids,
        template_id="ordinary-station-activation-v1",
        cost=activated_ability_cost(ability),
        effects=(
            {
                "op": "station",
                "card": "$source.zone_object",
                "amount": "$station.power",
                "source": "$source",
            },
        ),
        handlers=(ordinary_station_handler_descriptor(spec),),
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


__all__ = ["ordinary_station_keyword_node"]
