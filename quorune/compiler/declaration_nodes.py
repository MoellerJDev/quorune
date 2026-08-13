from __future__ import annotations

"""Typed Oracle-IR lowering for combat declaration static abilities."""

from typing import Any

from ..ability_fragments import ability_fragment_to_dict
from ..declaration_costs import parse_declaration_cost_line
from ..declaration_fragments import (
    DECLARATION_COMPONENT_CAPABILITY_ID,
    DeclarationCostTemplate,
    DeclarationRequirementTemplate,
    DeclarationRestrictionTemplate,
)
from ..declaration_requirements import parse_declaration_requirement_line
from ..declaration_restrictions import parse_declaration_restriction_line
from ..rules.capabilities import CapabilityRegistry
from ..semantic_runtime.ability_fragments import (
    DECLARATION_COST_FRAGMENT_HANDLER_ID,
    DECLARATION_REQUIREMENT_FRAGMENT_HANDLER_ID,
    DECLARATION_RESTRICTION_FRAGMENT_HANDLER_ID,
)
from .dependency_gate import explicit_capability_gate
from .ir_model import append_residual, OracleNode, OracleResidual, SourceSpan


DeclarationTemplate = (
    DeclarationCostTemplate
    | DeclarationRequirementTemplate
    | DeclarationRestrictionTemplate
)


def _typed_declaration_node(
    *,
    node_id: str,
    line: str,
    span: SourceSpan,
    template: DeclarationTemplate,
    handler_id: str,
    residuals: list[OracleResidual],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    dependency_reason: str,
    cost: dict[str, Any] | None = None,
) -> OracleNode:
    dependencies = template.mechanics
    gate = explicit_capability_gate(
        DECLARATION_COMPONENT_CAPABILITY_ID,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    missing = gate.blockers
    residual_ids = (
        (
            append_residual(
                residuals,
                kind="dependency_contract",
                text=line,
                span=span,
                reason=dependency_reason,
                blockers=missing,
            ),
        )
        if missing
        else ()
    )
    closure = gate.closure
    return OracleNode(
        node_id=node_id,
        kind="static_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="combat.declaration",
        lowerable=True,
        exact=not missing,
        template_id=template.template_id,
        cost=cost,
        handlers=(
            {
                "handler_id": handler_id,
                "schema_version": 1,
                "event": "combat.declaration",
                "fragment": ability_fragment_to_dict(template),
            },
        ),
        mechanics=dependencies,
        residual_ids=residual_ids,
        capability_dependencies=gate.capabilities,
        capability_closure=closure.reachable if closure is not None else (),
        capability_profile=closure.profile if closure is not None else None,
        capability_fingerprint=(
            closure.fingerprint if closure is not None else None
        ),
    )


def declaration_static_node(
    *,
    node_id: str,
    line: str,
    card_name: str,
    span: SourceSpan,
    residuals: list[OracleResidual],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
) -> OracleNode | None:
    """Compile one bounded declaration line or return ``None``."""

    requirement = parse_declaration_requirement_line(line, card_name=card_name)
    if requirement is not None:
        return _typed_declaration_node(
            node_id=node_id,
            line=line,
            span=span,
            template=requirement,
            handler_id=DECLARATION_REQUIREMENT_FRAGMENT_HANDLER_ID,
            residuals=residuals,
            capability_registry=capability_registry,
            capability_profile=capability_profile,
            dependency_reason=(
                "declaration requirement depends on untrusted mechanic or "
                "capability contracts"
            ),
        )

    cost_parse = parse_declaration_cost_line(line, card_name=card_name)
    if cost_parse.recognized:
        template = cost_parse.template
        if cost_parse.exact and template is not None:
            return _typed_declaration_node(
                node_id=node_id,
                line=line,
                span=span,
                template=template,
                handler_id=DECLARATION_COST_FRAGMENT_HANDLER_ID,
                residuals=residuals,
                capability_registry=capability_registry,
                capability_profile=capability_profile,
                dependency_reason=(
                    "declaration cost depends on untrusted mechanic or "
                    "capability contracts"
                ),
                cost={
                    "kind": "declaration_mana",
                    "declarations": list(template.declarations),
                    "scope": template.scope,
                    "mana": dict(template.mana),
                    "printed": template.printed_cost,
                    "source_condition": template.source_condition,
                    "includes_planeswalkers": template.includes_planeswalkers,
                },
            )
        residual_id = append_residual(
            residuals,
            kind="declaration_cost",
            text=line,
            span=span,
            reason=cost_parse.reason or "declaration cost grammar is unresolved",
            blockers=(
                "nonmana declaration costs",
                "variable and alternative mana declaration costs",
                "conditional declaration-cost grammar",
            ),
        )
        return OracleNode(
            node_id=node_id,
            kind="static_ability",
            text=line,
            span=span,
            active_zone="battlefield",
            event="continuous",
            lowerable=False,
            exact=False,
            mechanics=cost_parse.declarations,
            residual_ids=(residual_id,),
        )

    restriction_parse = parse_declaration_restriction_line(
        line, card_name=card_name
    )
    if not restriction_parse.recognized:
        return None
    template = restriction_parse.template
    if restriction_parse.exact and template is not None:
        return _typed_declaration_node(
            node_id=node_id,
            line=line,
            span=span,
            template=template,
            handler_id=DECLARATION_RESTRICTION_FRAGMENT_HANDLER_ID,
            residuals=residuals,
            capability_registry=capability_registry,
            capability_profile=capability_profile,
            dependency_reason=(
                "declaration restriction depends on untrusted mechanic or "
                "capability contracts"
            ),
        )
    dependencies = tuple(
        mechanic
        for declaration, mechanic in (
            ("attack", "cr-508-declare-attackers-step"),
            ("block", "cr-509-declare-blockers-step"),
        )
        if declaration in restriction_parse.declarations
    )
    residual_id = append_residual(
        residuals,
        kind="declaration_restriction",
        text=line,
        span=span,
        reason=(
            restriction_parse.reason
            or "declaration restriction grammar is unresolved"
        ),
        blockers=(
            "conditional declaration predicates",
            "temporary declaration restrictions",
            "broader evasion and group constraints",
        ),
    )
    return OracleNode(
        node_id=node_id,
        kind="static_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="continuous",
        lowerable=False,
        exact=False,
        mechanics=dependencies,
        residual_ids=(residual_id,),
    )


__all__ = ["declaration_static_node"]
