from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..rules.capabilities import CapabilityRegistry
from .ability_keyword_fragment_model import AbilityKeywordFragmentLowering
from .changeling_characteristics import (
    CHANGELING_FRAGMENT_HANDLER_ID,
    CHANGELING_MECHANIC_ID,
    lower_changeling_characteristic_fragment,
)
from .dependency_gate import explicit_capability_gate
from .devoid_characteristics import (
    DEVOID_FRAGMENT_HANDLER_ID,
    DEVOID_MECHANIC_ID,
    lower_devoid_characteristic_fragment,
)
from .ir_model import (
    OracleNode,
    OracleResidual,
    SourceSpan,
    append_residual,
)


@dataclass(frozen=True, slots=True)
class _CharacteristicDefinitionFamily:
    mechanic_id: str
    capability_id: str
    handler_id: str
    template_id: str
    runtime_coverage: str
    layer_label: str
    lowerer: Callable[
        [str, tuple[str, ...]],
        AbilityKeywordFragmentLowering | None,
    ]


_FAMILIES = {
    family.mechanic_id: family
    for family in (
        _CharacteristicDefinitionFamily(
            mechanic_id=DEVOID_MECHANIC_ID,
            capability_id="continuous.characteristics.devoid",
            handler_id=DEVOID_FRAGMENT_HANDLER_ID,
            template_id="devoid-colorless-characteristic-definition-v1",
            runtime_coverage="layer_5_colorless_characteristic",
            layer_label="layer-5 colorless",
            lowerer=lower_devoid_characteristic_fragment,
        ),
        _CharacteristicDefinitionFamily(
            mechanic_id=CHANGELING_MECHANIC_ID,
            capability_id="continuous.characteristics.changeling",
            handler_id=CHANGELING_FRAGMENT_HANDLER_ID,
            template_id="changeling-all-creature-types-characteristic-definition-v1",
            runtime_coverage="layer_4_all_creature_types_characteristic",
            layer_label="layer-4 all-creature-types",
            lowerer=lower_changeling_characteristic_fragment,
        ),
    )
}


def characteristic_definition_keyword_node(
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
    """Lower one ordinary all-zone characteristic-defining keyword."""

    if len(mechanics) != 1 or mechanics[0] not in _FAMILIES:
        return None
    family = _FAMILIES[mechanics[0]]
    ordinary = (
        material_line.strip().rstrip(".").casefold() == family.mechanic_id
    )
    gate = explicit_capability_gate(
        family.capability_id,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    blockers = (
        gate.blockers
        if ordinary
        else (f"mechanic:{family.mechanic_id}-unsupported-wording",)
    )
    residual_ids = (
        (
            append_residual(
                residuals,
                kind="dependency_contract" if ordinary else "keyword_grammar",
                text=line,
                span=span,
                reason=(
                    f"{family.mechanic_id.title()} depends on a blocked typed "
                    f"{family.layer_label} capability"
                    if ordinary
                    else (
                        f"{family.mechanic_id.title()} wording is outside the "
                        "ordinary keyword grammar"
                    )
                ),
                blockers=blockers,
            ),
        )
        if blockers
        else ()
    )
    lowering = family.lowerer(material_line, mechanics)
    if lowering is None:
        raise RuntimeError(
            f"Missing {family.mechanic_id} characteristic lowering"
        )
    if ordinary and not lowering.handlers:
        residual_ids += (
            append_residual(
                residuals,
                kind="dependency_contract",
                text=line,
                span=span,
                reason=(
                    f"{family.mechanic_id.title()} lowering did not produce "
                    "its required typed characteristic descriptor"
                ),
                blockers=(family.handler_id,),
            ),
        )
    closure = gate.closure
    return OracleNode(
        node_id=node_id,
        kind="static_ability",
        text=line,
        span=span,
        active_zone="all",
        event="continuous",
        lowerable=ordinary,
        exact=ordinary and not residual_ids,
        template_id=family.template_id if ordinary else None,
        handlers=lowering.handlers if ordinary else (),
        runtime_coverage=(family.runtime_coverage,) if ordinary else (),
        mechanics=mechanics,
        residual_ids=residual_ids,
        capability_dependencies=gate.capabilities,
        capability_closure=(
            closure.reachable if closure is not None else ()
        ),
        capability_profile=(closure.profile if closure is not None else None),
        capability_fingerprint=(
            closure.fingerprint if closure is not None else None
        ),
    )


__all__ = ["characteristic_definition_keyword_node"]
