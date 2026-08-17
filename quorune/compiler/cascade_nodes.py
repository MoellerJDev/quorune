from __future__ import annotations

from ..rules.capabilities import CapabilityRegistry
from .ability_keyword_fragments import lower_ability_keyword_fragments
from .dependency_gate import explicit_capability_gate
from .ir_model import OracleNode, OracleResidual, SourceSpan, append_residual


CASCADE_MECHANIC_ID = "cascade"


def cascade_keyword_node(
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
    if mechanics != (CASCADE_MECHANIC_ID,):
        return None
    ordinary = (
        material_line.strip().rstrip(".").casefold() == CASCADE_MECHANIC_ID
    )
    gate = explicit_capability_gate(
        "trigger.keyword.cascade",
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    blockers = (
        gate.blockers
        if ordinary
        else ("mechanic:cascade-unsupported-wording",)
    )
    residual_ids = (
        (
            append_residual(
                residuals,
                kind="dependency_contract" if ordinary else "keyword_grammar",
                text=line,
                span=span,
                reason=(
                    "Cascade depends on a blocked typed resolution capability"
                    if ordinary
                    else "Cascade wording is outside the ordinary keyword grammar"
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
                reason="Cascade lowering omitted its typed trigger descriptor",
                blockers=("ability.trigger.cascade.v1",),
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
        template_id="cascade-stack-cast-trigger-v1" if ordinary else None,
        handlers=lowering.handlers if ordinary else (),
        runtime_coverage=("typed_cascade_resolution",) if ordinary else (),
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
    "CASCADE_MECHANIC_ID",
    "cascade_keyword_node",
]
