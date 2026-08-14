from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any, Callable, Mapping, Sequence

from ..rules.capabilities import CapabilityRegistry
from .dependency_gate import dependency_gate
from .ir_model import OracleNode, OracleResidual, SourceSpan, append_residual


FIXED_COUNTER_EVENT_TRIGGER_MECHANIC = "fixed-counter-event-trigger"

_COUNTER_PLACEMENT_OPERATIONS = frozenset(
    {
        "place_counter_batch",
        "place_counters",
        "place_counters_on_set",
        "place_counters_on_targets",
        "place_player_counters",
    }
)
_SCHEDULED_TRIGGER = re.compile(
    r"^At the beginning of "
    r"(?P<schedule>your upkeep|each upkeep|your end step|each end step|"
    r"combat on your turn), (?P<body>.+)$",
    re.IGNORECASE,
)
_CONTROLLED_LAND_ENTRY_TRIGGER = re.compile(
    r"^(?:Landfall\s+[—-]\s+)?Whenever a land you control enters, "
    r"(?P<body>.+)$",
    re.IGNORECASE,
)
_CONTROLLER_SPELL_CAST_TRIGGER = re.compile(
    r"^Whenever you cast (?P<quality>a noncreature|an instant or sorcery) "
    r"spell, (?P<body>.+)$",
    re.IGNORECASE,
)


class FixedCounterTriggerEvent(str, Enum):
    """Closed normalized event families accepted by this compiler slice."""

    STEP_BEGIN = "step.begin"
    CONTROLLED_LAND_ENTER = "land.enter"
    CONTROLLER_SPELL_CAST = "spell.cast"


@dataclass(frozen=True, slots=True)
class FixedCounterTriggerBinding:
    """Immutable event subscription for one fixed counter-effect trigger."""

    event: FixedCounterTriggerEvent
    variant: str
    body: str

    def __post_init__(self) -> None:
        if not isinstance(self.event, FixedCounterTriggerEvent):
            raise ValueError("Fixed counter triggers require a closed event")
        if type(self.variant) is not str or not self.variant:
            raise ValueError("Fixed counter trigger variants must be nonempty")
        if type(self.body) is not str or not self.body:
            raise ValueError("Fixed counter trigger bodies must be nonempty")

    @property
    def template_id(self) -> str:
        return {
            FixedCounterTriggerEvent.STEP_BEGIN:
                "fixed-counter-step-trigger-v1",
            FixedCounterTriggerEvent.CONTROLLED_LAND_ENTER:
                "fixed-counter-controlled-land-entry-trigger-v1",
            FixedCounterTriggerEvent.CONTROLLER_SPELL_CAST:
                "fixed-counter-controller-spell-cast-trigger-v1",
        }[self.event]

    @property
    def event_mechanics(self) -> tuple[str, ...]:
        """Return only the normalized-event owners this binding consumes."""

        return {
            FixedCounterTriggerEvent.STEP_BEGIN: (),
            FixedCounterTriggerEvent.CONTROLLED_LAND_ENTER: (
                "trigger-event-normalized-zone-change",
            ),
            FixedCounterTriggerEvent.CONTROLLER_SPELL_CAST: (
                "trigger-event-normalized-spell-cast",
            ),
        }[self.event]

    @property
    def event_condition(self) -> Mapping[str, Any]:
        if self.event is FixedCounterTriggerEvent.CONTROLLED_LAND_ENTER:
            return {
                "field": "controller",
                "op": "eq",
                "value": "$source.controller",
            }
        if self.event is FixedCounterTriggerEvent.CONTROLLER_SPELL_CAST:
            type_condition: Mapping[str, Any] = (
                {
                    "not": {
                        "field": "types",
                        "op": "contains_any",
                        "value": ["creature"],
                    }
                }
                if self.variant == "noncreature"
                else {
                    "field": "types",
                    "op": "contains_any",
                    "value": ["instant", "sorcery"],
                }
            )
            return {
                "all": [
                    {
                        "field": "controller",
                        "op": "eq",
                        "value": "$source.controller",
                    },
                    type_condition,
                ]
            }
        step, controller_only = {
            "your upkeep": ("upkeep", True),
            "each upkeep": ("upkeep", False),
            "your end step": ("end_step", True),
            "each end step": ("end_step", False),
            "combat on your turn": ("beginning_combat", True),
        }[self.variant]
        conditions: list[Mapping[str, Any]] = [
            {"field": "step", "op": "eq", "value": step}
        ]
        if controller_only:
            conditions.insert(
                0,
                {
                    "field": "player",
                    "op": "eq",
                    "value": "$source.controller",
                },
            )
        return {"all": conditions}


def fixed_counter_trigger_binding(
    material_line: str,
) -> FixedCounterTriggerBinding | None:
    scheduled = _SCHEDULED_TRIGGER.fullmatch(material_line)
    if scheduled is not None:
        return FixedCounterTriggerBinding(
            event=FixedCounterTriggerEvent.STEP_BEGIN,
            variant=scheduled.group("schedule").casefold(),
            body=scheduled.group("body"),
        )
    land_entry = _CONTROLLED_LAND_ENTRY_TRIGGER.fullmatch(material_line)
    if land_entry is not None:
        return FixedCounterTriggerBinding(
            event=FixedCounterTriggerEvent.CONTROLLED_LAND_ENTER,
            variant="controlled_land",
            body=land_entry.group("body"),
        )
    spell_cast = _CONTROLLER_SPELL_CAST_TRIGGER.fullmatch(material_line)
    if spell_cast is not None:
        quality = spell_cast.group("quality").casefold()
        return FixedCounterTriggerBinding(
            event=FixedCounterTriggerEvent.CONTROLLER_SPELL_CAST,
            variant=(
                "noncreature"
                if quality == "a noncreature"
                else "instant_or_sorcery"
            ),
            body=spell_cast.group("body"),
        )
    return None


def _nested_operations(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, Mapping):
        operation = value.get("op")
        if isinstance(operation, str) and operation:
            result.add(operation)
        for child in value.values():
            result.update(_nested_operations(child))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            result.update(_nested_operations(child))
    return result


def fixed_counter_event_trigger_node(
    *,
    node_id: str,
    line: str,
    material_line: str,
    span: SourceSpan,
    card_name: str,
    trusted_mechanics: frozenset[str],
    capability_registry: CapabilityRegistry | None,
    capability_profile: str,
    residuals: list[OracleResidual],
    effect_template: Callable[..., tuple[
        str | None,
        tuple[Mapping[str, Any], ...],
        Mapping[str, Any] | None,
        tuple[str, ...],
    ]],
) -> OracleNode | None:
    """Lower one exact fixed counter effect over a normalized event."""

    binding = fixed_counter_trigger_binding(material_line)
    if binding is None:
        return None
    template, effects, target_schema, body_mechanics = effect_template(
        binding.body,
        card_name=card_name,
    )
    if (
        template is None
        or not _COUNTER_PLACEMENT_OPERATIONS.intersection(
            _nested_operations(effects)
        )
    ):
        return None
    mechanics = (
        "cr-603-handling-triggered-abilities",
        FIXED_COUNTER_EVENT_TRIGGER_MECHANIC,
        *binding.event_mechanics,
        *body_mechanics,
    )
    gate = dependency_gate(
        mechanics=mechanics,
        effects=effects,
        target_schema=target_schema,
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
                reason=(
                    "fixed counter event trigger lacks a trusted capability "
                    "closure"
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
        kind="triggered_ability",
        text=line,
        span=span,
        active_zone="battlefield",
        event=binding.event.value,
        event_condition=binding.event_condition,
        lowerable=True,
        exact=not residual_ids,
        template_id=binding.template_id,
        effects=effects,
        target_schema=target_schema,
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


__all__ = [
    "FIXED_COUNTER_EVENT_TRIGGER_MECHANIC",
    "FixedCounterTriggerBinding",
    "FixedCounterTriggerEvent",
    "fixed_counter_event_trigger_node",
    "fixed_counter_trigger_binding",
]
