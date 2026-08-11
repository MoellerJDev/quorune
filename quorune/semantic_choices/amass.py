from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..amass import (
    AMASS_COUNTER_NAME,
    AmassError,
    FixedAmassSpec,
    plural_amass_subtype,
)
from ..replacement.immutable import FrozenMap
from ..semantic_runtime.intents import (
    AddSubtypeIntent,
    CreateTokenIntent,
    PlaceCountersIntent,
    RecordChoiceIntent,
)
from ..semantic_runtime.context import SemanticSourceContext
from .context import (
    ChoiceObjectView,
    SemanticChoiceContext,
    SemanticChoiceQuery,
)
from .model import (
    AutoContinue,
    ObjectChoice,
    SemanticChoiceCompletion,
    SemanticChoiceContinuation,
    SemanticChoiceError,
    SemanticChoicePreparation,
    SemanticChoiceRequest,
)


_STAGE_FIELD = "_amass_stage"
_CHOOSE_STAGE = "choose_army"
_EXTERNAL_FIELDS = {"op", "subtype", "amount"}
_STAGED_FIELDS = _EXTERNAL_FIELDS | {_STAGE_FIELD}
_CONTINUATION_FIELDS = _STAGED_FIELDS | {
    "_actor",
    "_army_snapshot",
    "_legal_refs",
    "_source_ref",
    "_source_object_id",
    "_source_logical_object_id",
    "_stack_label",
}


def _spec(effect: Mapping[str, Any], *, staged: bool) -> FixedAmassSpec:
    expected = _STAGED_FIELDS if staged else _EXTERNAL_FIELDS
    if set(effect) != expected or effect.get("op") != "amass":
        raise SemanticChoiceError("Amass effect fields are malformed")
    if staged and effect.get(_STAGE_FIELD) != _CHOOSE_STAGE:
        raise SemanticChoiceError("Amass continuation stage is malformed")
    try:
        return FixedAmassSpec(
            subtype=effect.get("subtype"),
            amount=effect.get("amount"),
        )
    except AmassError as exc:
        raise SemanticChoiceError(str(exc)) from exc


def _armies(
    query: SemanticChoiceQuery,
    actor: str,
) -> tuple[ChoiceObjectView, ...]:
    return tuple(
        row
        for row in query.objects(zones=("battlefield",), controller=actor)
        if "creature" in row.types and "army" in row.subtypes
    )


def _strict_refs(value: Any, *, label: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise SemanticChoiceError(f"{label} must be a sequence")
    refs = tuple(value)
    if (
        any(type(ref) is not str or not ref for ref in refs)
        or len(refs) != len(set(refs))
    ):
        raise SemanticChoiceError(
            f"{label} must contain unique nonempty object references"
        )
    return refs


def _army_snapshot(armies: tuple[ChoiceObjectView, ...]) -> tuple[FrozenMap, ...]:
    return tuple(
        FrozenMap(
            {
                "ref": row.ref,
                "object_id": row.object_id,
                "logical_object_id": row.logical_object_id,
                "controller": row.controller,
            }
        )
        for row in armies
    )


def _completion_intents(
    *,
    actor: str,
    spec: FixedAmassSpec,
    army: ChoiceObjectView | None,
    source_ref: str | None,
    source: SemanticSourceContext,
    stack_ref: str,
    stack_label: str,
) -> tuple[Any, ...]:
    if army is None:
        return (
            RecordChoiceIntent(
                actor=actor,
                event_code="keyword_action.amass.completed",
                message=(
                    f"{actor} amassed {plural_amass_subtype(spec.subtype)} "
                    f"{spec.amount}."
                ),
                details=FrozenMap(
                    {
                        "stack": stack_ref,
                        "army": None,
                        "subtype": spec.subtype,
                        "amount": spec.amount,
                    }
                ),
                importance=2,
            ),
        )
    intents: list[Any] = []
    if spec.amount:
        intents.append(
            PlaceCountersIntent(
                actor=actor,
                object_refs=(army.ref,),
                counter_name=AMASS_COUNTER_NAME,
                amount=spec.amount,
                reason=stack_label,
                source_ref=source_ref,
            )
        )
    if spec.subtype.casefold() not in army.subtypes:
        intents.append(
            AddSubtypeIntent(
                actor=actor,
                object_ref=army.ref,
                subtype=spec.subtype,
                source=source,
                reason=stack_label,
            )
        )
    intents.append(
        RecordChoiceIntent(
            actor=actor,
            event_code="keyword_action.amass.completed",
            message=(
                f"{actor} amassed {plural_amass_subtype(spec.subtype)} "
                f"{spec.amount} onto "
                f"{army.ref}."
            ),
            details=FrozenMap(
                {
                    "stack": stack_ref,
                    "army": army.ref,
                    "subtype": spec.subtype,
                    "amount": spec.amount,
                }
            ),
            importance=2,
            changed_object_refs=(army.ref,),
        )
    )
    return tuple(intents)


@dataclass(frozen=True, slots=True)
class FixedAmassChoiceHandler:
    operation: str = "amass"
    handler_id: str = "choice.keyword-action.amass-fixed.v2"
    schema_version: int = 2
    rule_references: tuple[str, ...] = (
        "CR 701.47",
        "CR 701.47a",
        "CR 701.47b",
        "CR 701.47c",
        "CR 701.47d",
    )
    capability_dependencies: tuple[str, ...] = (
        "token.creation.additional_replacement",
        "counter.placement.quantity_replacement",
    )
    continuation_fields: tuple[str, ...] = (
        "subtype",
        "amount",
        _STAGE_FIELD,
        "_actor",
        "_army_snapshot",
        "_legal_refs",
        "_source_ref",
        "_source_object_id",
        "_source_logical_object_id",
        "_stack_label",
    )
    private_data: tuple[str, ...] = ()
    projected_fields: tuple[str, ...] = (
        "prompt",
        "objects",
        "legal_actions.choice_schema.legal_refs",
    )
    mutation_path: tuple[str, ...] = (
        "CreateTokenIntent",
        "PlaceCountersIntent",
        "AddSubtypeIntent",
    )
    replay_fixture: str = "fixed-amass-sequence"
    test_modules: tuple[str, ...] = ("tests.test_amass_rules",)

    def prepare(
        self,
        effect: Mapping[str, Any],
        context: SemanticChoiceContext,
    ) -> SemanticChoicePreparation:
        staged = _STAGE_FIELD in effect
        spec = _spec(effect, staged=staged)
        if not staged and not _armies(context.query, context.actor):
            return SemanticChoicePreparation(
                request=None,
                continuation_effect=FrozenMap(effect),
                preparation_intents=(
                    CreateTokenIntent(
                        actor=context.actor,
                        controller=context.actor,
                        name=f"{spec.subtype} Army",
                        quantity=1,
                        characteristics=FrozenMap(
                            {
                                "type_line": (
                                    f"Token Creature — {spec.subtype} Army"
                                ),
                                "colors": ("B",),
                                "power": "0",
                                "toughness": "0",
                            }
                        ),
                        reason=context.stack_label,
                    ),
                ),
                auto_continue=AutoContinue(
                    reason="create an Army before choosing one",
                    prepend_effects=(
                        FrozenMap(
                            {
                                "op": self.operation,
                                "subtype": spec.subtype,
                                "amount": spec.amount,
                                _STAGE_FIELD: _CHOOSE_STAGE,
                            }
                        ),
                    ),
                ),
            )
        armies = _armies(context.query, context.actor)
        staged_effect = FrozenMap(
            {
                "op": self.operation,
                "subtype": spec.subtype,
                "amount": spec.amount,
                _STAGE_FIELD: _CHOOSE_STAGE,
            }
        )
        if len(armies) <= 1:
            return SemanticChoicePreparation(
                request=None,
                continuation_effect=staged_effect,
                preparation_intents=_completion_intents(
                    actor=context.actor,
                    spec=spec,
                    army=armies[0] if armies else None,
                    source_ref=context.source_ref,
                    source=SemanticSourceContext(
                        stack_ref=context.stack_ref,
                        object_id=context.source_object_id,
                        logical_object_id=context.source_logical_object_id,
                        card_ref=context.source_ref,
                    ),
                    stack_ref=context.stack_ref,
                    stack_label=context.stack_label,
                ),
                auto_continue=AutoContinue(
                    reason=(
                        "Amass has one legal Army"
                        if armies
                        else "Amass has no possible Army choice"
                    )
                ),
            )
        continuation = FrozenMap(
            {
                "op": self.operation,
                "subtype": spec.subtype,
                "amount": spec.amount,
                _STAGE_FIELD: _CHOOSE_STAGE,
                "_actor": context.actor,
                "_army_snapshot": _army_snapshot(armies),
                "_legal_refs": tuple(row.ref for row in armies),
                "_source_ref": context.source_ref,
                "_source_object_id": context.source_object_id,
                "_source_logical_object_id": (
                    context.source_logical_object_id
                ),
                "_stack_label": context.stack_label,
            }
        )
        legal_refs = tuple(row.ref for row in armies)
        return SemanticChoicePreparation(
            request=SemanticChoiceRequest(
                prompt=(
                    "Choose an Army to amass "
                    f"{plural_amass_subtype(spec.subtype)} {spec.amount}."
                ),
                choice=ObjectChoice(
                    field_name="objects",
                    legal_refs=legal_refs,
                    zones=("battlefield",),
                    controller_relation="actor",
                    predicates=FrozenMap(
                        {"types": ("creature",), "subtypes": ("army",)}
                    ),
                ),
                public_context=FrozenMap(
                    {
                        "stack": context.stack_ref,
                        "operation": self.operation,
                        "objects": tuple(
                            {"id": row.ref, "name": row.printed_name}
                            for row in armies
                        ),
                    }
                ),
            ),
            continuation_effect=continuation,
        )

    def complete(
        self,
        continuation: SemanticChoiceContinuation,
        response: Mapping[str, Any],
        query: SemanticChoiceQuery,
    ) -> SemanticChoiceCompletion:
        effect = continuation.effect
        if set(effect) != _CONTINUATION_FIELDS:
            raise SemanticChoiceError("Amass continuation fields are malformed")
        spec = _spec(
            {
                "op": effect.get("op"),
                "subtype": effect.get("subtype"),
                "amount": effect.get("amount"),
                _STAGE_FIELD: effect.get(_STAGE_FIELD),
            },
            staged=True,
        )
        actor = effect.get("_actor")
        if type(actor) is not str or not actor:
            raise SemanticChoiceError("Amass continuation actor is malformed")
        raw_selected = response.get("objects", response.get("cards"))
        if not isinstance(raw_selected, (list, tuple)):
            raise SemanticChoiceError("Amass requires one Army choice")
        selected = _strict_refs(raw_selected, label="Amass selection")
        legal_refs = _strict_refs(
            effect.get("_legal_refs"), label="Amass legal references"
        )
        if (
            len(selected) != 1
            or selected[0] not in legal_refs
        ):
            raise SemanticChoiceError("Choose exactly one legal Army to amass")
        current_armies = _armies(query, actor)
        raw_snapshot = effect.get("_army_snapshot")
        if not isinstance(raw_snapshot, (list, tuple)) or any(
            not isinstance(value, Mapping) for value in raw_snapshot
        ):
            raise SemanticChoiceError("Amass Army snapshot is malformed")
        if _army_snapshot(current_armies) != tuple(raw_snapshot):
            raise SemanticChoiceError("Amass legal Army identity set changed")
        if tuple(row.ref for row in current_armies) != legal_refs:
            raise SemanticChoiceError("Amass legal Army reference set changed")
        army = next(row for row in current_armies if row.ref == selected[0])
        source_ref = effect.get("_source_ref")
        if source_ref is not None and (
            type(source_ref) is not str or not source_ref
        ):
            raise SemanticChoiceError("Amass source identity is malformed")
        source_object_id = effect.get("_source_object_id")
        source_logical_object_id = effect.get("_source_logical_object_id")
        if (source_object_id is None) != (source_logical_object_id is None):
            raise SemanticChoiceError("Amass source identity is incomplete")
        if any(
            value is not None and (type(value) is not str or not value)
            for value in (source_object_id, source_logical_object_id)
        ):
            raise SemanticChoiceError("Amass source identity is malformed")
        stack_label = effect.get("_stack_label")
        if type(stack_label) is not str or not stack_label:
            raise SemanticChoiceError("Amass stack label is malformed")
        return SemanticChoiceCompletion(
            intents=_completion_intents(
                actor=actor,
                spec=spec,
                army=army,
                source_ref=source_ref,
                source=SemanticSourceContext(
                    stack_ref=continuation.stack_ref,
                    object_id=source_object_id,
                    logical_object_id=source_logical_object_id,
                    card_ref=source_ref,
                ),
                stack_ref=continuation.stack_ref,
                stack_label=stack_label,
            )
        )


AMASS_CHOICE_HANDLERS = (FixedAmassChoiceHandler(),)


__all__ = ["AMASS_CHOICE_HANDLERS", "FixedAmassChoiceHandler"]
