from __future__ import annotations

import hashlib
import json
import re
from functools import partial
from typing import Any, Iterable, Mapping, Sequence

from .attachment_references import AttachmentReferenceKind
from .aura import keyword_target_schema
from .carddb import CardDatabase, CardRecord
from .cast_timing import (
    CAST_PERMISSION_ACTIVE_ZONE,
    CAST_PERMISSION_EVENT,
    PRINTED_FLASH_MECHANIC,
)
from .characteristic_evaluation import type_parts
from .compiler.corpus_reporting import (
    execute_oracle_operation,
    explain_oracle_ir,
    oracle_corpus_coverage,
)
from .compiler.continuous_templates import (
    controlled_creature_until_end_of_turn_effect,
)
from .cycling_abilities import CYCLING_MECHANIC_ID
from .compiler.activated_mana_nodes import (
    activated_oracle_node,
)
from .compiler.ability_keyword_fragments import (
    lower_ability_keyword_fragments,
)
from .compiler.dependency_gate import (
    dependency_gate as _dependency_gate,
    explicit_capability_gate as _explicit_capability_gate,
    keyword_dependency_gate,
)
from .compiler.draw_templates import (
    draw_reveal_or_trigger_nodes,
    fixed_draw_effect_template,
)
from .compiler.explore_templates import single_explore_effect_template
from .compiler.fixed_numbers import fixed_number as _number
from .compiler.keyword_templates import keyword_mechanics
from .compiler.keyword_nodes import (
    closed_special_keyword_node,
    death_return_keyword_node,
    dredge_keyword_node,
    evolve_keyword_node,
    fabricate_keyword_node,
    keyword_node_plans,
    riot_keyword_node,
    unleash_keyword_nodes,
)
from .compiler.ir_model import (
    append_residual as _residual,
    OracleCardIR,
    OracleFaceIR,
    OracleNode,
    OracleResidual,
    SourceSpan,
)
from .compiler.intrinsic_counter_nodes import (
    intrinsic_counter_prohibition_node,
)
from .compiler.prevention_templates import (
    fixed_prevention_effect_template,
    prevention_trigger_effect_template,
)
from .compiler.resolution_effect_templates import (
    typed_resolution_effect_template,
)
from .compiler.static_runtime_nodes import (
    runtime_handler_node,
    static_runtime_node,
)
from .compiler.spell_additional_cost_nodes import (
    typed_additional_cost_spell_node,
)
from .compiler.tap_state_templates import targeted_tap_state_effect_template
from .declaration_costs import parse_declaration_cost_line
from .declaration_restrictions import parse_declaration_restriction_line
from .rules.capabilities import CapabilityRegistry
from .rules.source_references import SourceReferenceSpec
from .riot import RIOT_MECHANIC
from .semantics import SemanticProgram, SemanticRegistry
from .unleash import UNLEASH_MECHANIC
from .util import stable_json


ORACLE_IR_SCHEMA_VERSION = 1
ORACLE_COMPILER_VERSION = "oracle-ir-v67"
ORACLE_OPERATIONS = {"parse", "explain", "residuals", "coverage"}
_TRIGGER_PREFIX = re.compile(
    r"^(when|whenever|at the beginning of)\b",
    re.IGNORECASE,
)
_REPLACEMENT_MARKERS = re.compile(
    r"\b(instead|as .+ enters|enters .+ with|skip)\b",
    re.IGNORECASE,
)
_ORDINARY_SAGA_RULES_REMINDER = re.compile(
    r"\(As this Saga enters and after your draw step, add a lore counter\. "
    r"Sacrifice after [IVXLCDM]+\.\)",
    re.IGNORECASE,
)
_ABILITY_WORD = re.compile(
    r"^(?P<word>[A-Za-z][A-Za-z ']+)\s+[—-]\s+(?P<body>.+)$"
)
_PERMANENT_CARD_TYPES = frozenset(
    {
        "artifact",
        "battle",
        "creature",
        "enchantment",
        "land",
        "planeswalker",
    }
)
_SPELL_CARD_TYPES = frozenset({"instant", "sorcery"})


def _source_lines(text: str) -> Iterable[tuple[str, SourceSpan]]:
    offset = 0
    for line_number, raw in enumerate(text.splitlines(keepends=True), 1):
        line = raw.rstrip("\r\n")
        stripped = line.strip()
        if stripped:
            left = len(line) - len(line.lstrip())
            yield stripped, SourceSpan(
                start=offset + left,
                end=offset + left + len(stripped),
                line=line_number,
            )
        offset += len(raw)
    if text and not text.splitlines(keepends=True):
        yield text, SourceSpan(0, len(text), 1)


def _without_parenthetical_reminder(text: str) -> str:
    result: list[str] = []
    depth = 0
    for character in text:
        if character == "(":
            depth += 1
            continue
        if character == ")" and depth:
            depth -= 1
            continue
        if depth == 0:
            result.append(character)
    return "".join(result).strip()


def _is_ordinary_saga_rules_reminder(
    type_line: str,
    line: str,
    material_line: str,
) -> bool:
    return (
        "saga" in type_parts(type_line)[1]
        and not material_line
        and _ORDINARY_SAGA_RULES_REMINDER.fullmatch(line) is not None
    )


def _material_source_lines(
    type_line: str,
    oracle_text: str,
) -> Iterable[tuple[str, str, SourceSpan]]:
    for line, span in _source_lines(oracle_text):
        material_line = _without_parenthetical_reminder(line)
        if _is_ordinary_saga_rules_reminder(type_line, line, material_line):
            continue
        yield line, material_line, span


def _face_type_context(
    type_line: str,
) -> tuple[
    frozenset[str],
    bool,
    bool,
    bool | None,
    AttachmentReferenceKind | None,
]:
    """Return exact card types and closed resolution-source context."""

    parsed_card_types, subtypes, _supertypes = type_parts(type_line)
    card_types = frozenset(parsed_card_types)
    permanent = bool(card_types.intersection(_PERMANENT_CARD_TYPES))
    spell = bool(card_types.intersection(_SPELL_CARD_TYPES))
    support_source = (
        True
        if permanent and not spell
        else False
        if spell and not permanent
        else None
    )
    attachment_relations = tuple(
        relation
        for subtype, relation in (
            ("aura", AttachmentReferenceKind.ENCHANTED),
            ("equipment", AttachmentReferenceKind.EQUIPPED),
            ("fortification", AttachmentReferenceKind.FORTIFIED),
        )
        if subtype in subtypes
    )
    attachment_relation = (
        attachment_relations[0] if len(attachment_relations) == 1 else None
    )
    return (
        card_types,
        permanent,
        spell,
        support_source,
        attachment_relation,
    )


def _effect_template(
    text: str,
    *,
    card_name: str,
    source_is_permanent: bool | None = None, source_attachment_relation: AttachmentReferenceKind | None = None,
) -> tuple[
    str | None,
    tuple[Mapping[str, Any], ...],
    Mapping[str, Any] | None,
    tuple[str, ...],
]:
    """Compile only whole, reviewed Oracle sentence templates."""

    normalized = text.strip()
    if re.fullmatch(
        r"you become the monarch\.?",
        normalized,
        re.IGNORECASE,
    ):
        return (
            "become-monarch-controller-v1",
            (
                {
                    "op": "become_monarch",
                    "player": "$controller",
                },
            ),
            None,
            ("cr-725-the-monarch",),
        )
    draw_template = fixed_draw_effect_template(normalized)
    if draw_template is not None:
        return draw_template
    match = re.fullmatch(
        r"you gain (?P<count>\d+) life\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        return (
            "gain-life-controller-v1",
            (
                {
                    "op": "life",
                    "player": "$controller",
                    "delta": int(match.group("count")),
                },
            ),
            None,
            ("cr-119-life",),
        )
    match = re.fullmatch(
        r"each opponent loses (?P<count>\d+) life\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        return (
            "lose-life-each-opponent-v1",
            (
                {
                    "op": "lose_life_each_opponent",
                    "amount": int(match.group("count")),
                },
            ),
            None,
            (
                "cr-119-life",
                "cr-101-the-magic-golden-rules",
            ),
        )
    typed = typed_resolution_effect_template(normalized, card_name=card_name, source_is_permanent=source_is_permanent, source_attachment_relation=source_attachment_relation)
    if typed is not None:
        return typed
    match = re.fullmatch(
        r"target player mills (?P<count>\d+) cards?\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        return (
            "mill-target-player-v1",
            (
                {
                    "op": "mill",
                    "player": "$target.0",
                    "count": int(match.group("count")),
                },
            ),
            {
                "zones": ["player"],
                "categories": ["player"],
                "count": 1,
            },
            ("mill", "cr-115-targets"),
        )
    tap_state = targeted_tap_state_effect_template(normalized)
    if tap_state is not None:
        return tap_state.compiled()
    explore = single_explore_effect_template(normalized)
    if explore is not None:
        return explore.compiled()
    match = re.fullmatch(
        r"goad target creature"
        r"(?P<relation> an opponent controls| you don't control)?\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        opponent = bool(match.group("relation"))
        schema: dict[str, Any] = {
            "zones": ["battlefield"],
            "categories": ["permanent"],
            "types_any": ["creature"],
            "count": 1,
        }
        if opponent:
            schema["controller_relation"] = "opponent"
        return (
            (
                "goad-target-opponent-creature-v1"
                if opponent
                else "goad-target-creature-v1"
            ),
            ({"op": "goad", "card": "$target.0"},),
            schema,
            ("goad", "cr-115-targets"),
        )
    match = re.fullmatch(
        r"this (?P<kind>artifact|creature|enchantment|permanent) gets "
        r"(?P<power>[+-]\d+)/(?P<toughness>[+-]\d+) until end of turn\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        return (
            f"modify-self-{match.group('kind').casefold()}-stats-eot-v1",
            (
                {
                    "op": "modify_stats_until_end_of_turn",
                    "card": "$source",
                    "power": int(match.group("power")),
                    "toughness": int(match.group("toughness")),
                },
            ),
            None,
            ("cr-611-continuous-effects",),
        )
    match = re.fullmatch(
        r"this (?P<kind>artifact|creature|enchantment|permanent) gains "
        r"(?P<keyword>deathtouch|double strike|first strike|flying|haste|"
        r"hexproof|indestructible|lifelink|menace|reach|trample|vigilance) "
        r"until end of turn\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        keyword = match.group("keyword").casefold()
        return (
            f"grant-self-{keyword.replace(' ', '-')}-eot-v1",
            (
                {
                    "op": "grant_keyword_until_end_of_turn",
                    "card": "$source",
                    "keyword": keyword.title(),
                },
            ),
            None,
            ("cr-611-continuous-effects", keyword),
        )
    match = re.fullmatch(
        r"return this (?P<kind>artifact|creature|enchantment|permanent) "
        r"to its owner'?s hand\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        return (
            f"bounce-self-{match.group('kind').casefold()}-v1",
            ({"op": "bounce", "card": "$source"},),
            None,
            ("cr-400-general",),
        )
    match = re.fullmatch(
        r"create (?P<count>a|one|two|three|four|five|six|seven|eight|"
        r"nine|ten|\d+) (?P<power>\d+)/(?P<toughness>\d+) "
        r"(?P<color>white|blue|black|red|green|colorless) "
        r"(?P<subtypes>[A-Za-z][A-Za-z -]*?) "
        r"(?P<artifact>artifact )?creature tokens?\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        colors = {
            "white": ["W"],
            "blue": ["U"],
            "black": ["B"],
            "red": ["R"],
            "green": ["G"],
            "colorless": [],
        }[match.group("color").casefold()]
        subtypes = " ".join(
            word.capitalize()
            for word in match.group("subtypes").split()
        )
        artifact = bool(match.group("artifact"))
        return (
            "create-basic-creature-token-v1",
            (
                {
                    "op": "create_token",
                    "controller": "$controller",
                    "name": subtypes,
                    "quantity": _number(match.group("count")),
                    "characteristics": {
                        "type_line": (
                            "Token "
                            + ("Artifact " if artifact else "")
                            + f"Creature — {subtypes}"
                        ),
                        "colors": colors,
                        "power": match.group("power"),
                        "toughness": match.group("toughness"),
                    },
                },
            ),
            None,
            ("cr-111-tokens",),
        )
    match = re.fullmatch(
        r"scry (?P<count>\d+)\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        return (
            "scry-controller-v1",
            (
                {
                    "op": "scry",
                    "player": "$controller",
                    "count": int(match.group("count")),
                },
            ),
            None,
            ("scry",),
        )
    return None, (), None, ()


def _reviewed_effect_template(
    text: str,
    *,
    card_name: str,
    source_is_permanent: bool | None = None,
    source_attachment_relation: AttachmentReferenceKind | None = None,
) -> tuple[
    str | None,
    tuple[Mapping[str, Any], ...],
    Mapping[str, Any] | None,
    tuple[str, ...],
]:
    temporary_modifier = controlled_creature_until_end_of_turn_effect(
        text.strip()
    )
    if temporary_modifier is not None:
        template, effects, mechanics = temporary_modifier
        return template, effects, None, mechanics
    prevention = fixed_prevention_effect_template(
        text.strip(),
        card_name=card_name,
    )
    return prevention or _effect_template(
        text,
        card_name=card_name,
        source_is_permanent=source_is_permanent,
        source_attachment_relation=source_attachment_relation,
    )


def _keyword_node_for_mechanics(
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
) -> OracleNode:
    closed_special = closed_special_keyword_node(
        node_id=node_id,
        line=line,
        material_line=material_line,
        span=span,
        mechanics=mechanics,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
        residuals=residuals,
    )
    if closed_special is not None:
        return closed_special
    gate = keyword_dependency_gate(
        material_line=material_line,
        mechanics=mechanics,
        trusted_mechanics=trusted_mechanics,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    enchant_target_schema = keyword_target_schema(material_line, mechanics)
    fragment_lowering = lower_ability_keyword_fragments(
        material_line,
        mechanics,
    )
    residual_id_values: list[str] = []
    if gate.blockers:
        residual_id_values.append(
            _residual(
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
            _residual(
                residuals,
                kind=fragment_lowering.residual_kind,
                text=line,
                span=span,
                reason=str(fragment_lowering.residual_reason),
                blockers=fragment_lowering.residual_blockers,
            )
        )
    residual_ids = tuple(residual_id_values)
    if fabricate := fabricate_keyword_node(
        node_id=node_id,
        line=line,
        material_line=material_line,
        span=span,
        mechanics=mechanics,
        gate=gate,
        residual_ids=residual_ids,
    ):
        return fabricate
    if evolve := evolve_keyword_node(
        node_id=node_id,
        line=line,
        material_line=material_line,
        span=span,
        mechanics=mechanics,
        gate=gate,
        residual_ids=residual_ids,
    ):
        return evolve
    if death_return := death_return_keyword_node(
        node_id=node_id,
        line=line,
        material_line=material_line,
        span=span,
        mechanics=mechanics,
        gate=gate,
        residual_ids=residual_ids,
    ):
        return death_return
    if dredge := dredge_keyword_node(
        node_id=node_id,
        line=line,
        material_line=material_line,
        span=span,
        mechanics=mechanics,
        gate=gate,
        residual_ids=residual_ids,
    ):
        return dredge
    flash = mechanics == (PRINTED_FLASH_MECHANIC,)
    return OracleNode(
        node_id=node_id,
        kind="keyword_ability",
        text=line,
        span=span,
        active_zone=(
            CAST_PERMISSION_ACTIVE_ZONE if flash else "battlefield"
        ),
        event=CAST_PERMISSION_EVENT if flash else "continuous",
        lowerable=True,
        exact=not residual_ids,
        template_id=(
            "printed-flash-cast-permission-v1"
            if flash
            else "printed-keyword-list-v1"
        ),
        handlers=fragment_lowering.handlers,
        target_schema=enchant_target_schema,
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


def _keyword_nodes(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    keywords: Sequence[str],
    trusted_mechanics: frozenset[str],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> tuple[OracleNode, ...]:
    """Compile one keyword line without conflating Flash's active zone."""

    mechanics = keyword_mechanics(material_line, keywords)
    if mechanics is None and re.match(
        r"^Cycling(?:\s+\{|[\-\u2013\u2014])",
        material_line,
        re.IGNORECASE,
    ):
        mechanics = (CYCLING_MECHANIC_ID,)
    if mechanics is None:
        return ()

    plans = keyword_node_plans(
        node_id=node_id,
        line=line,
        material_line=material_line,
        span=span,
        mechanics=mechanics,
    )
    nodes: list[OracleNode] = []
    for plan in plans:
        if plan.mechanics == (RIOT_MECHANIC,):
            nodes.append(
                riot_keyword_node(
                    node_id=plan.node_id,
                    line=plan.line,
                    material_line=plan.material_line,
                    span=plan.span,
                    capability_registry=capability_registry,
                    capability_profile=capability_profile,
                    residuals=residuals,
                )
            )
            continue
        if plan.mechanics == (UNLEASH_MECHANIC,):
            nodes.extend(
                unleash_keyword_nodes(
                    node_id=plan.node_id,
                    line=plan.line,
                    material_line=plan.material_line,
                    span=plan.span,
                    capability_registry=capability_registry,
                    capability_profile=capability_profile,
                    residuals=residuals,
                )
            )
            continue
        nodes.append(
            _keyword_node_for_mechanics(
            node_id=plan.node_id,
            line=plan.line,
            material_line=plan.material_line,
            span=plan.span,
            mechanics=plan.mechanics,
            trusted_mechanics=trusted_mechanics,
            capability_registry=capability_registry,
            capability_profile=capability_profile,
            residuals=residuals,
            )
        )
    return tuple(nodes)


def _trigger_node(
    *,
    node_id: str,
    line: str,
    span: SourceSpan,
    card_name: str,
    trusted_mechanics: frozenset[str],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
    effect_template: Any = _reviewed_effect_template,
) -> OracleNode | None:
    """Compile one closed ordinary or CR 615.13 triggered ability."""

    material_line = _without_parenthetical_reminder(line)
    if not _TRIGGER_PREFIX.match(material_line):
        return None
    source_name = SourceReferenceSpec(card_name).regex_pattern
    trigger = re.fullmatch(
        rf"(?:when|whenever) "
        rf"(?P<subject>this (?:artifact|aura|card|creature|"
        rf"enchantment|equipment|land|permanent)|{source_name}) "
        rf"(?P<event>enters|dies|leaves the battlefield), "
        rf"(?P<body>.+)",
        material_line,
        re.IGNORECASE,
    )
    prevention_trigger = prevention_trigger_effect_template(
        material_line,
        card_name=card_name,
    )
    template = None
    effects: tuple[Mapping[str, Any], ...] = ()
    target_schema = None
    mechanics: tuple[str, ...] = ()
    event_condition: Mapping[str, Any] | None = None
    event = "unresolved"
    recognized = False
    if prevention_trigger is not None:
        (
            template,
            effects,
            target_schema,
            mechanics,
            event_condition,
        ) = prevention_trigger
        event = "damage.prevented"
        recognized = True
    elif trigger:
        explored = single_explore_effect_template(
            trigger.group("body"),
            allow_source_pronoun=True,
        )
        template, effects, target_schema, mechanics = (
            explored.compiled()
            if explored is not None
            else effect_template(
                trigger.group("body"),
                card_name=card_name,
            )
        )
        event = {
            "enters": "permanent.enter.self",
            "dies": "creature.dies.self",
            "leaves the battlefield": "permanent.leave.self",
        }[trigger.group("event").casefold()]
        recognized = True
    dependencies = (
        "cr-603-handling-triggered-abilities",
        *(
            ("trigger-event-normalized-zone-change",)
            if trigger is not None
            else ()
        ),
        *mechanics,
    )
    gate = _dependency_gate(
        mechanics=dependencies,
        effects=effects,
        target_schema=target_schema,
        trusted_mechanics=trusted_mechanics,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )
    if recognized and template is not None:
        residual_ids = (
            (
                _residual(
                    residuals,
                    kind="dependency_contract",
                    text=line,
                    span=span,
                    reason=(
                        "lowerable trigger depends on untrusted mechanic contracts"
                    ),
                    blockers=gate.blockers,
                ),
            )
            if gate.blockers
            else ()
        )
    else:
        residual_ids = (
            _residual(
                residuals,
                kind="trigger",
                text=line,
                span=span,
                reason=(
                    "trigger effect has no exact generic template"
                    if recognized
                    else "trigger condition/event binding is not exact"
                ),
                blockers=(
                    "normalized event binding",
                    "intervening-if and reflexive-trigger grammar",
                ),
            ),
        )
    closure = gate.closure
    return OracleNode(
        node_id=node_id,
        kind="triggered_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event=event,
        lowerable=recognized and template is not None,
        exact=recognized and template is not None and not gate.blockers,
        template_id=template,
        effects=effects,
        target_schema=target_schema,
        event_condition=event_condition,
        mechanics=dependencies,
        residual_ids=residual_ids,
        capability_dependencies=gate.capabilities,
        capability_closure=closure.reachable if closure is not None else (),
        capability_profile=closure.profile if closure is not None else None,
        capability_fingerprint=(
            closure.fingerprint if closure is not None else None
        ),
    )


def _is_unconditional_enters_tapped(line: str, source_name: str) -> bool:
    source_pattern = SourceReferenceSpec(source_name).regex_pattern
    return (
        re.fullmatch(
            rf"(?:this (?:artifact|creature|enchantment|land|permanent)"
            rf"|{source_pattern}) enters tapped\.?",
            line,
            re.IGNORECASE,
        )
        is not None
    )


def _unconditional_enters_tapped_node(
    *,
    node_id: str,
    line: str,
    span: SourceSpan,
    source_name: str,
    trusted_mechanics: frozenset[str],
    residuals: list[OracleResidual],
) -> OracleNode | None:
    if not _is_unconditional_enters_tapped(line, source_name):
        return None
    dependencies = ("cr-614-replacement-effects",)
    missing = sorted(set(dependencies) - trusted_mechanics)
    residual_ids = (
        (
            _residual(
                residuals,
                kind="dependency_contract",
                text=line,
                span=span,
                reason=(
                    "lowerable entry replacement depends on an "
                    "untrusted mechanic contract"
                ),
                blockers=tuple(f"mechanic:{mechanic}" for mechanic in missing),
            ),
        )
        if missing
        else ()
    )
    return OracleNode(
        node_id=node_id,
        kind="replacement_effect",
        text=line,
        span=span,
        active_zone="all",
        event="permanent.enter.self",
        lowerable=True,
        exact=not missing,
        template_id="enters-tapped-self-v1",
        mechanics=dependencies,
        residual_ids=residual_ids,
    )


def _typed_additional_cost_face(
    record: CardRecord,
    face_id: str,
    face_name: str,
    oracle_text: str,
    material_rows: Sequence[tuple[str, str, SourceSpan]],
    effect_template: Any,
    trusted_mechanics: frozenset[str],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
) -> OracleFaceIR | None:
    node = typed_additional_cost_spell_node(
        node_id=f"{face_id}:n1",
        rows=material_rows,
        card_name=face_name or record.name,
        effect_template=effect_template,
        trusted_mechanics=trusted_mechanics,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
        residuals=residuals,
    )
    if node is None:
        return None
    return OracleFaceIR(
        face_id=face_id,
        face_name=face_name,
        oracle_text=oracle_text,
        nodes=(node,),
        residuals=tuple(residuals),
    )


def _compile_face(
    record: CardRecord,
    *,
    face_id: str,
    face_name: str,
    type_line: str,
    oracle_text: str,
    keywords: Sequence[str],
    trusted_mechanics: frozenset[str],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
) -> OracleFaceIR:
    nodes: list[OracleNode] = []
    residuals: list[OracleResidual] = []
    (
        card_types,
        permanent,
        spell,
        support_source_is_permanent,
        source_attachment_relation,
    ) = _face_type_context(type_line)
    contextual_effect_template = partial(
        _reviewed_effect_template, source_is_permanent=support_source_is_permanent,
        source_attachment_relation=source_attachment_relation,
    )
    contextual_trigger_node = partial(
        _trigger_node, effect_template=contextual_effect_template
    )
    material_rows = tuple(_material_source_lines(type_line, oracle_text))
    if spell:
        additional_cost_face = _typed_additional_cost_face(
            record, face_id, face_name, oracle_text, material_rows,
            contextual_effect_template, trusted_mechanics, capability_registry,
            capability_profile, residuals,
        )
        if additional_cost_face is not None:
            return additional_cost_face
    for index, row in enumerate(material_rows, 1):
        line, material_line, span = row
        node_id = f"{face_id}:n{index}"
        keyword_nodes = _keyword_nodes(
            node_id=node_id,
            line=line,
            material_line=material_line,
            span=span,
            keywords=keywords,
            trusted_mechanics=trusted_mechanics,
            capability_registry=capability_registry,
            capability_profile=capability_profile,
            residuals=residuals,
        )
        if keyword_nodes:
            nodes.extend(keyword_nodes)
            continue

        activated_node = activated_oracle_node(
            node_id=node_id, line=line, span=span,
            card_name=face_name or record.name, keywords=keywords,
            trusted_mechanics=trusted_mechanics,
            capability_registry=capability_registry,
            capability_profile=capability_profile, residuals=residuals,
            effect_template=contextual_effect_template,
        )
        if activated_node is not None:
            nodes.append(activated_node)
            continue

        event_nodes = draw_reveal_or_trigger_nodes(
            permanent=permanent, node_id=node_id,
            line=line, span=span,
            card_name=face_name or record.name,
            trusted_mechanics=trusted_mechanics,
            capability_registry=capability_registry, capability_profile=capability_profile,
            residuals=residuals,
            runtime_handler_node=runtime_handler_node,
            trigger_node=contextual_trigger_node,
            append_residual=_residual,
        )
        if event_nodes is not None:
            nodes.extend(event_nodes)
            continue

        counter_prohibition = intrinsic_counter_prohibition_node(
            node_id=node_id,
            line=line,
            material_line=material_line,
            span=span,
            capability_registry=capability_registry,
            capability_profile=capability_profile,
            residuals=residuals,
        )
        if counter_prohibition is not None:
            nodes.append(counter_prohibition)
            continue

        enters_tapped = _unconditional_enters_tapped_node(
            node_id=node_id, line=line, span=span,
            source_name=face_name or record.name,
            trusted_mechanics=trusted_mechanics, residuals=residuals,
        )
        if enters_tapped is not None:
            nodes.append(enters_tapped)
            continue

        declaration_cost = parse_declaration_cost_line(
            line,
            card_name=face_name or record.name,
        )
        if declaration_cost.recognized:
            template = declaration_cost.template
            if declaration_cost.exact and template is not None:
                dependencies = template.mechanics
                missing = sorted(
                    set(dependencies) - trusted_mechanics
                )
                residual_ids = (
                    (
                        _residual(
                            residuals,
                            kind="dependency_contract",
                            text=line,
                            span=span,
                            reason=(
                                "declaration cost depends on untrusted "
                                "mechanic contracts"
                            ),
                            blockers=tuple(
                                f"mechanic:{mechanic}"
                                for mechanic in missing
                            ),
                        ),
                    )
                    if missing
                    else ()
                )
                nodes.append(
                    OracleNode(
                        node_id=node_id,
                        kind="static_ability",
                        text=line,
                        span=span,
                        active_zone="battlefield",
                        event="continuous",
                        lowerable=True,
                        exact=not missing,
                        template_id=template.template_id,
                        cost={
                            "kind": "declaration_mana",
                            "declarations": list(
                                template.declarations
                            ),
                            "scope": template.scope,
                            "mana": dict(template.mana),
                            "printed": template.printed_cost,
                            "source_condition": (
                                template.source_condition
                            ),
                        },
                        mechanics=dependencies,
                        residual_ids=residual_ids,
                    )
                )
                continue
            residual_id = _residual(
                residuals,
                kind="declaration_cost",
                text=line,
                span=span,
                reason=(
                    declaration_cost.reason
                    or "declaration cost grammar is unresolved"
                ),
                blockers=(
                    "nonmana declaration costs",
                    "variable and alternative mana declaration costs",
                    "conditional declaration-cost grammar",
                ),
            )
            nodes.append(
                OracleNode(
                    node_id=node_id,
                    kind="static_ability",
                    text=line,
                    span=span,
                    active_zone="battlefield",
                    event="continuous",
                    lowerable=False,
                    exact=False,
                    mechanics=declaration_cost.declarations,
                    residual_ids=(residual_id,),
                )
            )
            continue

        declaration_restriction = parse_declaration_restriction_line(
            line,
            card_name=face_name or record.name,
        )
        if declaration_restriction.recognized:
            template = declaration_restriction.template
            if declaration_restriction.exact and template is not None:
                dependencies = template.mechanics
                missing = sorted(
                    set(dependencies) - trusted_mechanics
                )
                residual_ids = (
                    (
                        _residual(
                            residuals,
                            kind="dependency_contract",
                            text=line,
                            span=span,
                            reason=(
                                "declaration restriction depends on "
                                "untrusted mechanic contracts"
                            ),
                            blockers=tuple(
                                f"mechanic:{mechanic}"
                                for mechanic in missing
                            ),
                        ),
                    )
                    if missing
                    else ()
                )
                nodes.append(
                    OracleNode(
                        node_id=node_id,
                        kind="static_ability",
                        text=line,
                        span=span,
                        active_zone="battlefield",
                        event="continuous",
                        lowerable=True,
                        exact=not missing,
                        template_id=template.template_id,
                        effects=(template.effect(),),
                        mechanics=dependencies,
                        residual_ids=residual_ids,
                    )
                )
                continue
            dependencies = tuple(
                mechanic
                for declaration, mechanic in (
                    ("attack", "cr-508-declare-attackers-step"),
                    ("block", "cr-509-declare-blockers-step"),
                )
                if declaration in declaration_restriction.declarations
            )
            residual_id = _residual(
                residuals,
                kind="declaration_restriction",
                text=line,
                span=span,
                reason=(
                    declaration_restriction.reason
                    or "declaration restriction grammar is unresolved"
                ),
                blockers=(
                    "conditional declaration predicates",
                    "temporary declaration restrictions",
                    "broader evasion and group constraints",
                ),
            )
            nodes.append(
                OracleNode(
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
            )
            continue

        runtime_node = static_runtime_node(
            node_id=node_id,
            line=line,
            material_line=material_line,
            span=span,
            card_types=card_types,
            permanent_card_types=_PERMANENT_CARD_TYPES,
            source_is_class=("class" in type_parts(type_line)[1]),
            capability_registry=capability_registry,
            capability_profile=capability_profile,
            residuals=residuals,
        )
        if runtime_node is not None:
            nodes.append(runtime_node)
            continue

        if _REPLACEMENT_MARKERS.search(line):
            residual_id = _residual(
                residuals,
                kind="replacement_effect",
                text=line,
                span=span,
                reason="replacement/prevention ordering is not compiled",
                blockers=(
                    "replacement applicability",
                    "affected-player ordering",
                    "self-replacement and prevention ordering",
                ),
            )
            nodes.append(
                OracleNode(
                    node_id=node_id,
                    kind="replacement_effect",
                    text=line,
                    span=span,
                    active_zone="battlefield" if permanent else "stack",
                    event="replace",
                    lowerable=False,
                    exact=False,
                    residual_ids=(residual_id,),
                )
            )
            continue

        ability_word = _ABILITY_WORD.match(material_line)
        body = ability_word.group("body") if ability_word else material_line
        template, effects, target_schema, mechanics = contextual_effect_template(
            body,
            card_name=face_name or record.name,
        )
        if spell and template is not None:
            dependency_gate = _dependency_gate(
                mechanics=mechanics,
                effects=effects,
                target_schema=target_schema,
                trusted_mechanics=trusted_mechanics,
                capability_registry=capability_registry,
                capability_profile=capability_profile,
            )
            missing = dependency_gate.blockers
            residual_ids = (
                (
                    _residual(
                        residuals,
                        kind="dependency_contract",
                        text=line,
                        span=span,
                        reason=(
                            "lowerable spell depends on untrusted "
                            "rules dependencies"
                        ),
                        blockers=missing,
                    ),
                )
                if missing
                else ()
            )
            nodes.append(
                OracleNode(
                    node_id=node_id,
                    kind="spell_ability",
                    text=line,
                    span=span,
                    active_zone="stack",
                    event="resolve",
                    lowerable=True,
                    exact=not missing,
                    template_id=template,
                    effects=effects,
                    target_schema=target_schema,
                    mechanics=mechanics,
                    residual_ids=residual_ids,
                    capability_dependencies=(
                        dependency_gate.capabilities
                    ),
                    capability_closure=(
                        dependency_gate.closure.reachable
                        if dependency_gate.closure is not None
                        else ()
                    ),
                    capability_profile=(
                        dependency_gate.closure.profile
                        if dependency_gate.closure is not None
                        else None
                    ),
                    capability_fingerprint=(
                        dependency_gate.closure.fingerprint
                        if dependency_gate.closure is not None
                        else None
                    ),
                )
            )
            continue

        residual_id = _residual(
            residuals,
            kind="static_ability" if permanent else "spell_effect",
            text=line,
            span=span,
            reason=(
                "static/continuous text has no exact typed contract"
                if permanent
                else "spell effect has no exact generic template"
            ),
            blockers=(
                ("continuous-effect layers and dependencies",)
                if permanent
                else ()
            ),
        )
        nodes.append(
            OracleNode(
                node_id=node_id,
                kind="static_ability" if permanent else "spell_ability",
                text=line,
                span=span,
                active_zone="battlefield" if permanent else "stack",
                event="continuous" if permanent else "resolve",
                lowerable=False,
                exact=False,
                residual_ids=(residual_id,),
            )
        )
    return OracleFaceIR(
        face_id=face_id,
        face_name=face_name,
        oracle_text=oracle_text,
        nodes=tuple(nodes),
        residuals=tuple(residuals),
    )


def compile_oracle_card(
    record: CardRecord,
    *,
    trusted_mechanics: Iterable[str] = (),
    capability_registry: CapabilityRegistry | None = None,
    capability_profile: str = "traditional",
) -> OracleCardIR:
    if (
        capability_registry is not None
        and capability_profile not in capability_registry.profiles
    ):
        raise ValueError(
            f"Unknown capability profile: {capability_profile}"
        )
    trusted = frozenset(
        str(mechanic).casefold() for mechanic in trusted_mechanics
    )
    face_values: list[tuple[str, str, str, str, Sequence[str]]] = []
    if record.faces:
        for index, face in enumerate(record.faces):
            face_values.append(
                (
                    str(face.get("name") or f"face-{index + 1}"),
                    str(face.get("name") or record.name),
                    str(face.get("type_line") or record.type_line),
                    str(face.get("oracle_text") or ""),
                    tuple(face.get("keywords") or record.keywords),
                )
            )
    else:
        face_values.append(
            (
                "front",
                record.name,
                record.type_line,
                record.oracle_text,
                record.keywords,
            )
        )
    faces = tuple(
        _compile_face(
            record,
            face_id=face_id,
            face_name=face_name,
            type_line=type_line,
            oracle_text=oracle_text,
            keywords=keywords,
            trusted_mechanics=trusted,
            capability_registry=capability_registry,
            capability_profile=capability_profile,
        )
        for face_id, face_name, type_line, oracle_text, keywords in face_values
    )
    oracle_hash = hashlib.sha256(
        record.oracle_text.encode("utf-8")
    ).hexdigest()
    semantic_payload = {
        "oracle_id": record.oracle_id,
        "oracle_hash": oracle_hash,
        "schema_version": ORACLE_IR_SCHEMA_VERSION,
        "compiler_version": ORACLE_COMPILER_VERSION,
        "faces": [face.to_dict() for face in faces],
    }
    return OracleCardIR(
        oracle_id=record.oracle_id,
        card_name=record.name,
        schema_version=ORACLE_IR_SCHEMA_VERSION,
        compiler_version=ORACLE_COMPILER_VERSION,
        oracle_hash=oracle_hash,
        faces=faces,
        semantic_hash=hashlib.sha256(
            stable_json(semantic_payload).encode("utf-8")
        ).hexdigest(),
    )


def generated_programs(
    db: CardDatabase,
    record: CardRecord,
    *,
    trust_level: str = "provisional",
    trusted_mechanics: Iterable[str] = (),
    capability_registry: CapabilityRegistry | None = None,
    capability_profile: str = "traditional",
) -> list[SemanticProgram]:
    """Compatibility API for the extracted generated-program stage."""

    from .compiler.program_generation import generated_programs as generate

    return generate(
        db,
        record,
        trust_level=trust_level,
        trusted_mechanics=trusted_mechanics,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
    )


def register_generated_programs(
    db: CardDatabase,
    registry: SemanticRegistry,
    records: Iterable[CardRecord],
    *,
    trust_level: str = "provisional",
    trusted_mechanics: Iterable[str] = (),
    capability_registry: CapabilityRegistry | None = None,
    capability_profile: str = "traditional",
    promote_exact_runtime_handlers: bool = False,
    promote_exact_trigger_programs: bool = False,
    promote_exact_effect_programs: bool = False,
    promote_exact_capability_declarations: bool = False,
) -> dict[str, Any]:
    """Compatibility API for extracted generated-program registration."""

    from .compiler.program_generation import register_generated_programs as register

    return register(
        db,
        registry,
        records,
        trust_level=trust_level,
        trusted_mechanics=trusted_mechanics,
        capability_registry=capability_registry,
        capability_profile=capability_profile,
        promote_exact_runtime_handlers=promote_exact_runtime_handlers,
        promote_exact_trigger_programs=promote_exact_trigger_programs,
        promote_exact_effect_programs=(
            promote_exact_effect_programs
        ),
        promote_exact_capability_declarations=(
            promote_exact_capability_declarations
        ),
    )
