from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping

from ..ability_fragments import CURRENT_ABILITY_FRAGMENT_COVERAGE
from ..bloodthirst import BLOODTHIRST_MECHANIC, BloodthirstSpec
from ..cast_timing import PRINTED_FLASH_MECHANIC
from ..semantic_runtime.cast_costs import convoke_handler_descriptor
from ..death_return import (
    DeathReturnSpec,
    PERSIST_KEYWORD,
    UNDYING_KEYWORD,
)
from ..evolve import EVOLVE_EVENT_CONDITION_FIELD
from ..echo import ECHO_MECHANIC_ID
from ..unleash import (
    UNLEASH_MECHANIC,
    unleash_block_handler_descriptor,
    unleash_entry_handler_descriptor,
)
from ..riot import RIOT_MECHANIC, riot_entry_handler_descriptor
from ..renown import RENOWN_MECHANIC_ID, RenownSpec
from ..modular import MODULAR_MECHANIC_ID, ModularSpec
from .cumulative_upkeep_nodes import fixed_mana_cumulative_upkeep_node
from .echo_nodes import fixed_mana_echo_node
from .crew_nodes import ordinary_crew_keyword_node
from .cycling_nodes import ordinary_cycling_keyword_node
from .ability_keyword_fragments import lower_ability_keyword_fragments
from .dependency_gate import (
    DependencyGate,
    explicit_capability_gate,
    keyword_dependency_gate,
)
from .ir_model import (
    OracleNode,
    OracleResidual,
    SourceSpan,
    append_residual,
)
from ..rules.capabilities import CapabilityRegistry


_DREDGE_MECHANIC = "dredge"
_EVOLVE_MECHANIC = "evolve"
_FABRICATE_MECHANIC = "fabricate"
_PERSIST_MECHANIC = PERSIST_KEYWORD
_UNDYING_MECHANIC = UNDYING_KEYWORD
_UNLEASH_MECHANIC = UNLEASH_MECHANIC
_RIOT_MECHANIC = RIOT_MECHANIC
_MENTOR_MECHANIC = "mentor"
_PROWESS_MECHANIC = "prowess"
_CONVOKE_MECHANIC = "convoke"
_BLOODTHIRST_MECHANIC = BLOODTHIRST_MECHANIC
_RENOWN_MECHANIC = RENOWN_MECHANIC_ID
_MODULAR_MECHANIC = MODULAR_MECHANIC_ID
_ECHO_MECHANIC = ECHO_MECHANIC_ID
_TOXIC_MECHANIC = "toxic"
_GROUPED_SPLIT_MECHANICS = (
    _BLOODTHIRST_MECHANIC,
    _TOXIC_MECHANIC,
    _EVOLVE_MECHANIC,
)
_PARAMETERIZED_SPLIT_MECHANICS = frozenset(
    {
        _BLOODTHIRST_MECHANIC,
        _RENOWN_MECHANIC,
        _MODULAR_MECHANIC,
        _ECHO_MECHANIC,
        _TOXIC_MECHANIC,
    }
)
_INSTANCE_PART_MECHANICS = (
    _BLOODTHIRST_MECHANIC,
    _EVOLVE_MECHANIC,
    _PERSIST_MECHANIC,
    _RIOT_MECHANIC,
    _UNDYING_MECHANIC,
    _UNLEASH_MECHANIC,
    _MENTOR_MECHANIC,
    _PROWESS_MECHANIC,
    _RENOWN_MECHANIC,
    _MODULAR_MECHANIC,
    _ECHO_MECHANIC,
    _TOXIC_MECHANIC,
    _CONVOKE_MECHANIC,
)
_SPLIT_MECHANICS = frozenset(
    {
        PRINTED_FLASH_MECHANIC,
        _FABRICATE_MECHANIC,
        *_INSTANCE_PART_MECHANICS,
    }
)


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
        for mechanic in (
            PRINTED_FLASH_MECHANIC,
            _FABRICATE_MECHANIC,
            _CONVOKE_MECHANIC,
        )
        if mechanic in mechanics
    ) + tuple(
        grouped
        for grouped in _GROUPED_SPLIT_MECHANICS
        for mechanic in mechanics
        if mechanic == grouped
    ) + tuple(
        mechanic
        for mechanic in mechanics
        if mechanic
        in {
            _PERSIST_MECHANIC,
            _RIOT_MECHANIC,
            _UNDYING_MECHANIC,
            _UNLEASH_MECHANIC,
            _MENTOR_MECHANIC,
            _PROWESS_MECHANIC,
            _RENOWN_MECHANIC,
            _MODULAR_MECHANIC,
            _ECHO_MECHANIC,
        }
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
            if (
                match.group().strip().rstrip(".").casefold() == mechanic
                or (
                    mechanic in _PARAMETERIZED_SPLIT_MECHANICS
                    and re.fullmatch(
                        rf"{re.escape(mechanic)}\s+.+",
                        match.group().strip().rstrip("."),
                        re.IGNORECASE,
                    )
                )
            )
        )
        for mechanic in _INSTANCE_PART_MECHANICS
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
        if mechanic not in _SPLIT_MECHANICS
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
    trusted_mechanics: frozenset[str],
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
    renown = renown_keyword_node(
        **values,
        trusted_mechanics=trusted_mechanics,
    )
    if renown is not None:
        return renown
    for lower in (
        ordinary_convoke_keyword_node,
        ordinary_crew_keyword_node,
        ordinary_cycling_keyword_node,
        fixed_mana_cumulative_upkeep_node,
        fixed_mana_echo_node,
    ):
        node = lower(**values)
        if node is not None:
            return node
    return None


def ordinary_convoke_keyword_node(
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
    if mechanics != (_CONVOKE_MECHANIC,):
        return None
    ordinary = material_line.strip().rstrip(".").casefold() == _CONVOKE_MECHANIC
    gate = explicit_capability_gate(
        "casting.payment.convoke",
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    blockers = gate.blockers if ordinary else ("mechanic:convoke-unsupported-wording",)
    residual_ids = (
        (
            append_residual(
                residuals,
                kind="dependency_contract" if ordinary else "keyword_grammar",
                text=line,
                span=span,
                reason=(
                    "Convoke depends on a blocked typed casting-cost capability"
                    if ordinary
                    else "Convoke wording is outside the ordinary keyword grammar"
                ),
                blockers=blockers,
            ),
        )
        if blockers
        else ()
    )
    return OracleNode(
        node_id=node_id,
        kind="keyword_ability",
        text=line,
        span=span,
        active_zone="stack",
        event="cast.cost",
        lowerable=ordinary,
        exact=ordinary and not blockers,
        template_id="ordinary-convoke-payment-v1" if ordinary else None,
        handlers=(convoke_handler_descriptor(),) if ordinary else (),
        runtime_coverage=("typed_convoke_payment",) if ordinary else (),
        mechanics=(_CONVOKE_MECHANIC,),
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


def bloodthirst_keyword_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    gate: DependencyGate,
    residual_ids: tuple[str, ...],
) -> OracleNode | None:
    """Lower one ordinary fixed CR 702.54a keyword instance."""

    if mechanics != (_BLOODTHIRST_MECHANIC,):
        return None
    match = re.fullmatch(
        rf"{re.escape(_BLOODTHIRST_MECHANIC)}\s+(?P<amount>[1-9]\d*)\.?",
        material_line.strip(),
        re.IGNORECASE,
    )
    if match is None:
        return OracleNode(
            node_id=node_id,
            kind="static_ability",
            text=line,
            span=span,
            active_zone="all",
            event="zone.change",
            lowerable=False,
            exact=False,
            mechanics=mechanics,
            residual_ids=residual_ids,
            capability_dependencies=gate.capabilities,
        )
    spec = BloodthirstSpec(int(match.group("amount")))
    return OracleNode(
        node_id=node_id,
        kind="static_ability",
        text=line,
        span=span,
        active_zone="all",
        event="zone.change",
        lowerable=True,
        exact=not residual_ids,
        template_id="bloodthirst-opponent-damage-entry-counter-v1",
        handlers=(spec.handler_descriptor(),),
        runtime_coverage=("conditional_self_entry_counter",),
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


def prowess_keyword_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    gate: DependencyGate,
    residual_ids: tuple[str, ...],
    handlers: tuple[Mapping[str, Any], ...],
) -> OracleNode | None:
    if (
        mechanics != (_PROWESS_MECHANIC,)
        or material_line.strip().rstrip(".").casefold() != _PROWESS_MECHANIC
    ):
        return None
    return OracleNode(
        node_id=node_id,
        kind="triggered_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="spell.cast",
        lowerable=True,
        exact=not residual_ids,
        template_id="prowess-noncreature-spell-trigger-v1",
        effects=(
            {
                "op": "modify_stats_until_end_of_turn",
                "card": "$source.zone_object",
                "power": 1,
                "toughness": 1,
            },
        ),
        handlers=handlers,
        event_condition={
            "all": [
                {
                    "field": "controller",
                    "op": "eq",
                    "value": "$source.controller",
                },
                {
                    "not": {
                        "field": "types",
                        "op": "contains_any",
                        "value": ["creature"],
                    }
                },
            ]
        },
        runtime_coverage=(CURRENT_ABILITY_FRAGMENT_COVERAGE,),
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


def renown_keyword_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    trusted_mechanics: frozenset[str],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> OracleNode | None:
    match = re.fullmatch(
        r"Renown\s+(?P<amount>[1-9]\d*)\.?",
        material_line.strip(),
        re.IGNORECASE,
    )
    if mechanics != (_RENOWN_MECHANIC,) or match is None:
        return None
    gate = keyword_dependency_gate(
        material_line=material_line,
        mechanics=mechanics,
        trusted_mechanics=trusted_mechanics,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    fragment_lowering = lower_ability_keyword_fragments(
        material_line,
        mechanics,
    )
    residual_id_values: list[str] = []
    if gate.blockers:
        residual_id_values.append(
            append_residual(
                residuals,
                kind="dependency_contract",
                text=line,
                span=span,
                reason="recognized keyword lacks a trusted mechanic contract",
                blockers=gate.blockers,
            )
        )
    if fragment_lowering.residual_kind is not None:
        residual_id_values.append(
            append_residual(
                residuals,
                kind=fragment_lowering.residual_kind,
                text=line,
                span=span,
                reason=str(fragment_lowering.residual_reason),
                blockers=fragment_lowering.residual_blockers,
            )
        )
    residual_ids = tuple(residual_id_values)
    spec = RenownSpec(amount=int(match.group("amount")))
    return OracleNode(
        node_id=node_id,
        kind="triggered_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event="damage.dealt.self",
        lowerable=True,
        exact=not residual_ids,
        template_id="renown-combat-damage-counter-designation-v1",
        effects=(spec.effect_descriptor(),),
        handlers=fragment_lowering.handlers,
        event_condition=spec.event_condition(),
        runtime_coverage=(
            CURRENT_ABILITY_FRAGMENT_COVERAGE,
            "intervening_condition",
            "cr-122-counters",
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


def modular_keyword_nodes(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    mechanics: tuple[str, ...],
    trusted_mechanics: frozenset[str],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> tuple[OracleNode, ...]:
    """Lower one fixed positive ``Modular N`` into both CR 702.43a abilities."""

    if mechanics != (_MODULAR_MECHANIC,):
        return ()
    match = re.fullmatch(
        r"Modular\s+(?P<amount>[1-9]\d*)\.?",
        material_line.strip(),
        re.IGNORECASE,
    )
    if match is None:
        residual_id = append_residual(
            residuals,
            kind="unsupported_modular_value",
            text=line,
            span=span,
            reason=(
                "Modular requires one printed positive integer; "
                "Modular—Sunburst remains a separate residual"
            ),
            blockers=("positive integer Modular value",),
        )
        return (
            OracleNode(
                node_id=node_id,
                kind="keyword_ability",
                text=line,
                span=span,
                active_zone="all",
                event="unresolved",
                lowerable=False,
                exact=False,
                mechanics=mechanics,
                residual_ids=(residual_id,),
            ),
        )

    gate = keyword_dependency_gate(
        material_line=material_line,
        mechanics=mechanics,
        trusted_mechanics=trusted_mechanics,
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
                reason="Modular depends on a blocked typed lifecycle capability",
                blockers=gate.blockers,
            ),
        )
        if gate.blockers
        else ()
    )
    spec = ModularSpec(amount=int(match.group("amount")))
    common = {
        "text": line,
        "span": span,
        "lowerable": True,
        "exact": not residual_ids,
        "mechanics": mechanics,
        "residual_ids": residual_ids,
        "capability_dependencies": gate.capabilities,
        "capability_closure": (
            gate.closure.reachable if gate.closure is not None else ()
        ),
        "capability_profile": (
            gate.closure.profile if gate.closure is not None else None
        ),
        "capability_fingerprint": (
            gate.closure.fingerprint if gate.closure is not None else None
        ),
    }
    return (
        OracleNode(
            node_id=f"{node_id}:entry",
            kind="static_ability",
            active_zone="all",
            event="zone.change",
            template_id="modular-fixed-entry-counter-v1",
            handlers=(spec.entry_handler_descriptor(),),
            runtime_coverage=("replacement_aware_self_entry_counter",),
            **common,
        ),
        OracleNode(
            node_id=f"{node_id}:departure",
            kind="triggered_ability",
            active_zone="battlefield",
            event="permanent.graveyard.self",
            template_id="modular-lki-counter-transfer-v1",
            effects=(spec.departure_effect_descriptor(),),
            target_schema=spec.target_schema(),
            runtime_coverage=(
                "departure_counter_lki",
                "optional_targeted_counter_placement",
            ),
            **common,
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


def riot_keyword_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> OracleNode:
    """Lower ordinary Riot as one linked entry-result choice."""

    ordinary = material_line.strip().rstrip(".").casefold() == RIOT_MECHANIC
    gate = explicit_capability_gate(
        "counter.producer.riot",
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    blockers = (
        gate.blockers
        if ordinary
        else ("mechanic:riot-unsupported-wording",)
    )
    residual_ids = (
        (
            append_residual(
                residuals,
                kind=(
                    "dependency_contract" if ordinary else "keyword_grammar"
                ),
                text=line,
                span=span,
                reason=(
                    "Riot depends on a blocked typed capability"
                    if ordinary
                    else "Riot wording is outside the ordinary keyword grammar"
                ),
                blockers=blockers,
            ),
        )
        if blockers
        else ()
    )
    return OracleNode(
        node_id=node_id,
        kind="static_ability",
        text=line,
        span=span,
        active_zone="all",
        event="zone.change",
        lowerable=ordinary,
        exact=ordinary and not blockers,
        template_id="riot-linked-entry-choice-v1" if ordinary else None,
        handlers=(riot_entry_handler_descriptor(),) if ordinary else (),
        runtime_coverage=("linked_entry_counter_or_haste",) if ordinary else (),
        mechanics=(RIOT_MECHANIC,),
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
    "bloodthirst_keyword_node",
    "closed_special_keyword_node",
    "dredge_keyword_node",
    "death_return_keyword_node",
    "evolve_keyword_node",
    "fabricate_keyword_node",
    "keyword_node_plans",
    "modular_keyword_nodes",
    "ordinary_convoke_keyword_node",
    "prowess_keyword_node",
    "renown_keyword_node",
    "riot_keyword_node",
    "unleash_keyword_nodes",
]
