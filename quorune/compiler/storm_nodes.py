from __future__ import annotations

"""Closed compiler owner for ordinary printed Storm."""

from ..rules.capabilities import CapabilityRegistry
from .ability_keyword_fragments import lower_ability_keyword_fragments
from .dependency_gate import explicit_capability_gate
from .ir_model import OracleNode, OracleResidual, SourceSpan, append_residual


STORM_MECHANIC_ID = "storm"
STORM_CAPABILITY_ID = "trigger.keyword.storm"
STORM_TEMPLATE_ID = "storm-stack-cast-trigger-v1"


def storm_keyword_node(
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
    """Lower one complete ordinary printed Storm instance."""

    if mechanics != (STORM_MECHANIC_ID,):
        return None
    ordinary = (
        material_line.strip().rstrip(".").casefold() == STORM_MECHANIC_ID
    )
    gate = explicit_capability_gate(
        STORM_CAPABILITY_ID,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    blockers = (
        gate.blockers
        if ordinary
        else ("mechanic:storm-unsupported-wording",)
    )
    residual_ids = (
        (
            append_residual(
                residuals,
                kind="dependency_contract" if ordinary else "keyword_grammar",
                text=line,
                span=span,
                reason=(
                    "Storm depends on a blocked typed copy capability"
                    if ordinary
                    else "Storm wording is outside the ordinary keyword grammar"
                ),
                blockers=blockers,
            ),
        )
        if blockers
        else ()
    )
    lowering = lower_ability_keyword_fragments(material_line, mechanics)
    if ordinary and not lowering.handlers:
        residual_ids += (
            append_residual(
                residuals,
                kind="dependency_contract",
                text=line,
                span=span,
                reason="Storm lowering omitted its typed trigger descriptor",
                blockers=("ability.trigger.storm.v1",),
            ),
        )
    return OracleNode(
        node_id=node_id,
        kind="triggered_ability",
        text=line,
        span=span,
        active_zone="stack",
        event="spell.cast",
        lowerable=ordinary,
        exact=ordinary and not residual_ids,
        template_id=STORM_TEMPLATE_ID if ordinary else None,
        handlers=lowering.handlers if ordinary else (),
        runtime_coverage=("typed_storm_resolution",) if ordinary else (),
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


__all__ = [
    "STORM_CAPABILITY_ID",
    "STORM_MECHANIC_ID",
    "STORM_TEMPLATE_ID",
    "storm_keyword_node",
]
