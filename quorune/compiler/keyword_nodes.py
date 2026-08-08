from __future__ import annotations

from dataclasses import dataclass
import re

from ..cast_timing import PRINTED_FLASH_MECHANIC
from ..death_return import (
    DeathReturnSpec,
    PERSIST_KEYWORD,
    UNDYING_KEYWORD,
)
from ..evolve import EVOLVE_EVENT_CONDITION_FIELD
from ..unleash import (
    UNLEASH_MECHANIC,
    unleash_block_handler_descriptor,
    unleash_entry_handler_descriptor,
)
from .cumulative_upkeep_nodes import fixed_mana_cumulative_upkeep_node
from .cycling_nodes import ordinary_cycling_keyword_node
from .dependency_gate import DependencyGate, explicit_capability_gate
from .ir_model import (
    OracleNode,
    OracleResidual,
    SourceSpan,
    append_residual,
)
from ..rules.capabilities import CapabilityRegistry


_DREDGE_MECHANIC = "dred" + "ge"
_EVOLVE_MECHANIC = "evo" + "lve"
_FABRICATE_MECHANIC = "fabri" + "cate"
_PERSIST_MECHANIC = PERSIST_KEYWORD
_UNDYING_MECHANIC = UNDYING_KEYWORD
_UNLEASH_MECHANIC = UNLEASH_MECHANIC


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
    ) + tuple(
        mechanic
        for mechanic in mechanics
        if mechanic
        in {_PERSIST_MECHANIC, _UNDYING_MECHANIC, _UNLEASH_MECHANIC}
    )
    if not split_mechanics:
        return (
            KeywordNodePlan(node_id, line, material_line, span, mechanics),
        )

    occurrence: dict[str, int] = {}
    instance_parts = {
        mechanic: tuple(
            (
                match.group().strip().rstrip("."),
                match.start()
                + len(match.group())
                - len(match.group().lstrip()),
                match.end()
                - len(match.group())
                + len(match.group().rstrip()),
            )
            for match in re.finditer(r"[^,]+", material_line)
            if match.group().strip().rstrip(".").casefold() == mechanic
        )
        for mechanic in (
            _EVOLVE_MECHANIC,
            _PERSIST_MECHANIC,
            _UNDYING_MECHANIC,
            _UNLEASH_MECHANIC,
        )
    }
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
        parts = instance_parts.get(mechanic, ())
        if occurrence[mechanic] <= len(parts):
            fragment, start, end = parts[occurrence[mechanic] - 1]
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
            _PERSIST_MECHANIC,
            _UNDYING_MECHANIC,
            _UNLEASH_MECHANIC,
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


def death_return_keyword_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    gate: DependencyGate,
    residual_ids: tuple[str, ...],
) -> OracleNode | None:
    if mechanics not in {(_PERSIST_MECHANIC,), (_UNDYING_MECHANIC,)}:
        return None
    mechanic = mechanics[0]
    if material_line.strip().rstrip(".").casefold() != mechanic:
        return None
    spec = DeathReturnSpec.for_keyword(mechanic)
    return OracleNode(
        node_id=node_id,
        kind="triggered_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="creature.dies.self",
        lowerable=True,
        exact=not gate.blockers,
        template_id=f"{mechanic}-death-return-counter-v1",
        effects=(spec.effect_descriptor(),),
        event_condition=spec.event_condition(),
        runtime_coverage=("departure_intervening_condition",),
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


def unleash_keyword_nodes(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> tuple[OracleNode, ...]:
    """Lower the two static abilities represented by ordinary Unleash."""

    if material_line.strip().rstrip(".").casefold() != UNLEASH_MECHANIC:
        residual_id = append_residual(
            residuals,
            kind="keyword_grammar",
            text=line,
            span=span,
            reason="Unleash wording is outside the ordinary keyword grammar",
            blockers=("mechanic:unleash-unsupported-wording",),
        )
        return (
            OracleNode(
                node_id=node_id,
                kind="keyword_ability",
                text=line,
                span=span,
                active_zone="battlefield",
                event="continuous",
                lowerable=False,
                exact=False,
                mechanics=(UNLEASH_MECHANIC,),
                residual_ids=(residual_id,),
            ),
        )

    specifications = (
        (
            "unleash-entry",
            "all",
            "zone.change",
            "counter.producer.optional_self_entry",
            "unleash-optional-entry-counter-v1",
            unleash_entry_handler_descriptor(),
            "optional_entry_counter",
        ),
        (
            "unleash-block",
            "battlefield",
            "combat.block",
            "combat.block.self_counter_prohibition",
            "unleash-self-counter-block-prohibition-v1",
            unleash_block_handler_descriptor(),
            "counter_conditional_block_restriction",
        ),
    )
    result: list[OracleNode] = []
    for (
        suffix,
        active_zone,
        event,
        capability,
        template_id,
        handler,
        runtime_coverage,
    ) in specifications:
        gate = explicit_capability_gate(
            capability,
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
                    reason="Unleash depends on a blocked typed capability",
                    blockers=gate.blockers,
                ),
            )
            if gate.blockers
            else ()
        )
        result.append(
            OracleNode(
                node_id=f"{node_id}:{suffix}",
                kind="static_ability",
                text=line,
                span=span,
                active_zone=active_zone,
                event=event,
                lowerable=True,
                exact=not gate.blockers,
                template_id=template_id,
                handlers=(handler,),
                runtime_coverage=(runtime_coverage,),
                mechanics=(UNLEASH_MECHANIC,),
                residual_ids=residual_ids,
                capability_dependencies=gate.capabilities,
                capability_closure=(
                    gate.closure.reachable if gate.closure is not None else ()
                ),
                capability_profile=(
                    gate.closure.profile if gate.closure is not None else None
                ),
                capability_fingerprint=(
                    gate.closure.fingerprint
                    if gate.closure is not None
                    else None
                ),
            )
        )
    return tuple(result)


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
    "death_return_keyword_node",
    "evolve_keyword_node",
    "fabricate_keyword_node",
    "keyword_node_plans",
    "unleash_keyword_nodes",
]
