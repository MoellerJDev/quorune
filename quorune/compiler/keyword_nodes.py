from __future__ import annotations

from dataclasses import dataclass
import re

from ..cast_timing import PRINTED_FLASH_MECHANIC
from ..evolve import EVOLVE_EVENT_CONDITION_FIELD
from .cumulative_upkeep_nodes import fixed_mana_cumulative_upkeep_node
from .cycling_nodes import ordinary_cycling_keyword_node
from .dependency_gate import DependencyGate
from .ir_model import OracleNode, OracleResidual, SourceSpan
from ..rules.capabilities import CapabilityRegistry


_DREDGE_MECHANIC = "dred" + "ge"
_EVOLVE_MECHANIC = "evo" + "lve"
_FABRICATE_MECHANIC = "fabri" + "cate"


@dataclass(frozen=True, slots=True)
class KeywordNodePlan:
    """One source-spanned keyword fragment compiled as an independent node."""

    node_id: str
    line: str
    material_line: str
    span: SourceSpan
    mechanics: tuple[str, ...]


def keyword_node_plans(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
) -> tuple[KeywordNodePlan, ...]:
    """Split independently executable keyword instances deterministically."""

    split_mechanics = tuple(
        mechanic
        for mechanic in (PRINTED_FLASH_MECHANIC, _FABRICATE_MECHANIC)
        if mechanic in mechanics
    ) + tuple(
        _EVOLVE_MECHANIC
        for mechanic in mechanics
        if mechanic == _EVOLVE_MECHANIC
    )
    if not split_mechanics:
        return (
            KeywordNodePlan(node_id, line, material_line, span, mechanics),
        )

    occurrence: dict[str, int] = {}
    evolve_parts = tuple(
        (
            match.group().strip().rstrip("."),
            match.start() + len(match.group()) - len(match.group().lstrip()),
            match.end() - len(match.group()) + len(match.group().rstrip()),
        )
        for match in re.finditer(r"[^,]+", material_line)
        if match.group().strip().rstrip(".").casefold() == _EVOLVE_MECHANIC
    )
    result: list[KeywordNodePlan] = []
    for mechanic in split_mechanics:
        occurrence[mechanic] = occurrence.get(mechanic, 0) + 1
        suffix = (
            f"{mechanic}:{occurrence[mechanic]}"
            if mechanics.count(mechanic) > 1
            else mechanic
        )
        selected_line = line
        selected_material_line = material_line
        selected_span = span
        if (
            mechanic == _EVOLVE_MECHANIC
            and occurrence[mechanic] <= len(evolve_parts)
        ):
            fragment, start, end = evolve_parts[occurrence[mechanic] - 1]
            selected_line = fragment
            selected_material_line = fragment
            selected_span = SourceSpan(
                start=span.start + start,
                end=span.start + end,
                line=span.line,
            )
        result.append(
            KeywordNodePlan(
                node_id=f"{node_id}:{suffix}",
                line=selected_line,
                material_line=selected_material_line,
                span=selected_span,
                mechanics=(mechanic,),
            )
        )
    remaining = tuple(
        mechanic
        for mechanic in mechanics
        if mechanic not in {
            PRINTED_FLASH_MECHANIC,
            _FABRICATE_MECHANIC,
            _EVOLVE_MECHANIC,
        }
    )
    if remaining:
        result.append(
            KeywordNodePlan(node_id, line, material_line, span, remaining)
        )
    return tuple(result)


def closed_special_keyword_node(
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
    """Lower closed keyword families that own their complete node shape."""

    values = {
        "node_id": node_id,
        "line": line,
        "material_line": material_line,
        "span": span,
        "mechanics": mechanics,
        "capability_registry": capability_registry,
        "capability_profile": capability_profile,
        "residuals": residuals,
    }
    for lower in (
        ordinary_cycling_keyword_node,
        fixed_mana_cumulative_upkeep_node,
    ):
        node = lower(**values)
        if node is not None:
            return node
    return None


def evolve_keyword_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    gate: DependencyGate,
    residual_ids: tuple[str, ...],
) -> OracleNode | None:
    instances = tuple(
        part
        for part in material_line.rstrip(".").split(",")
        if part.strip().casefold() == _EVOLVE_MECHANIC
    )
    if mechanics != (_EVOLVE_MECHANIC,) or not instances:
        return None
    return OracleNode(
        node_id=node_id,
        kind="triggered_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="creature.enter",
        lowerable=True,
        exact=not gate.blockers,
        template_id="evolve-creature-enter-counter-v1",
        effects=(
            {
                "op": "place_counters",
                "card": "$source",
                "counter": "+1/+1",
                "amount": 1,
                "source": "$source",
            },
        ),
        event_condition={
            "field": EVOLVE_EVENT_CONDITION_FIELD,
            "op": "truthy",
        },
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


def fabricate_keyword_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    gate: DependencyGate,
    residual_ids: tuple[str, ...],
) -> OracleNode | None:
    matches = tuple(
        match
        for part in material_line.rstrip(".").split(",")
        for match in (
            re.fullmatch(
                r"Fabricate\s+(?P<count>[1-9]\d*)\.?",
                part.strip(),
                re.IGNORECASE,
            ),
        )
        if match is not None
    )
    if mechanics != (_FABRICATE_MECHANIC,) or len(matches) != 1:
        return None
    return OracleNode(
        node_id=node_id,
        kind="triggered_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="permanent.enter.self",
        lowerable=True,
        exact=not gate.blockers,
        template_id="fabricate-enter-choice-v1",
        mechanics=mechanics,
        effects=(
            {
                "op": _FABRICATE_MECHANIC,
                "amount": int(matches[0].group("count")),
            },
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


def dredge_keyword_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    gate: DependencyGate,
    residual_ids: tuple[str, ...],
) -> OracleNode | None:
    match = re.fullmatch(
        r"Dredge\s+(?P<count>[1-9]\d*)\.?",
        material_line,
        re.IGNORECASE,
    )
    if mechanics != (_DREDGE_MECHANIC,) or match is None:
        return None
    return OracleNode(
        node_id=node_id,
        kind="keyword_ability",
        text=line,
        span=span,
        active_zone="graveyard",
        event="draw",
        lowerable=True,
        exact=not gate.blockers,
        template_id="dredge-keyword-replacement-v1",
        mechanics=mechanics,
        handlers=(
            {
                "handler_id": "replacement.draw.dredge.v1",
                "schema_version": 1,
                "event": "draw",
                "modification": {"mill_count": int(match.group("count"))},
            },
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


__all__ = [
    "KeywordNodePlan",
    "closed_special_keyword_node",
    "dredge_keyword_node",
    "evolve_keyword_node",
    "fabricate_keyword_node",
    "keyword_node_plans",
]
