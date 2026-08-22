from __future__ import annotations

from ..commander_pairing import (
    COMMANDER_PAIRING_COVERAGE,
    COMMANDER_PAIRING_EVENT,
    COMMANDER_PAIRING_TEMPLATE_ID,
    PAIRING_CAPABILITY_BY_KIND,
    pairing_kind_for_material_line,
)
from ..rules.capabilities import CapabilityRegistry
from .dependency_gate import explicit_capability_gate
from .ir_model import OracleNode, OracleResidual, SourceSpan, append_residual


def commander_pairing_keyword_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
    **_: object,
) -> OracleNode | None:
    """Lower the exact ordinary Commander pairing declarations."""

    kind = pairing_kind_for_material_line(material_line)
    if kind is None or mechanics != (kind.value,):
        return None
    gate = explicit_capability_gate(
        PAIRING_CAPABILITY_BY_KIND[kind],
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
                    "Commander pairing eligibility depends on a blocked "
                    "typed setup capability"
                ),
                blockers=gate.blockers,
            ),
        )
        if gate.blockers
        else ()
    )
    closure = gate.closure
    return OracleNode(
        node_id=node_id,
        kind="keyword_ability",
        text=line,
        span=span,
        active_zone="all",
        event=COMMANDER_PAIRING_EVENT,
        lowerable=True,
        exact=not residual_ids,
        template_id=COMMANDER_PAIRING_TEMPLATE_ID,
        mechanics=mechanics,
        residual_ids=residual_ids,
        runtime_coverage=(COMMANDER_PAIRING_COVERAGE,),
        capability_dependencies=gate.capabilities,
        capability_closure=(
            closure.reachable if closure is not None else ()
        ),
        capability_profile=(closure.profile if closure is not None else None),
        capability_fingerprint=(
            closure.fingerprint if closure is not None else None
        ),
    )


__all__ = ["commander_pairing_keyword_node"]
