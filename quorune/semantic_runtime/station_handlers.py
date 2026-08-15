from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..station import STATION_CAPABILITY_ID
from .context import ReadOnlyHandlerContext, SemanticNodeError
from .intents import IntentPlan, PlaceCountersIntent


@dataclass(frozen=True, slots=True)
class StationCounterPlacementHandler:
    handler_id: str = "generic.station-counter-placement.v1"
    schema_version: int = 1
    family: str = "effect.counter-placement.station"
    operation: str = "station"
    rule_references: tuple[str, ...] = (
        "107.1b",
        "122.1",
        "122.1a",
        "122.6",
        "608.2h",
        "614.16",
        "616.1",
        "702.184a",
    )
    capability_dependencies: tuple[str, ...] = (STATION_CAPABILITY_ID,)

    def lower(
        self,
        effect: Mapping[str, Any],
        context: ReadOnlyHandlerContext,
    ) -> IntentPlan:
        allowed = {
            "op",
            "card",
            "amount",
            "source",
            "reason",
            "_replacement_selections",
        }
        unknown = sorted(set(effect) - allowed)
        if unknown:
            raise SemanticNodeError(
                "Station effect has unknown fields: " + ", ".join(unknown)
            )
        missing = sorted({"op", "card", "amount", "source"} - set(effect))
        if missing:
            raise SemanticNodeError(
                "Station effect is missing required fields: "
                + ", ".join(missing)
            )
        if effect.get("op") != self.operation:
            raise SemanticNodeError("Station operation is unsupported")
        object_ref = effect.get("card")
        if object_ref is not None and (
            type(object_ref) is not str or not object_ref
        ):
            raise SemanticNodeError(
                "Station source must be a public reference or unavailable"
            )
        amount = effect.get("amount")
        if type(amount) is not int or amount < 0:
            raise SemanticNodeError(
                "Station amount must be a nonnegative exact integer"
            )
        source_ref = effect.get("source")
        if type(source_ref) is not str or not source_ref:
            raise SemanticNodeError(
                "Station effect requires one nonempty source reference"
            )
        reason = effect.get("reason", context.default_reason)
        if type(reason) is not str or not reason:
            raise SemanticNodeError("Station reason must be nonempty")
        raw_selections = effect.get("_replacement_selections", ())
        if raw_selections is None:
            raw_selections = ()
        if not isinstance(raw_selections, (list, tuple)):
            raise SemanticNodeError(
                "Station replacement selections must be an array"
            )
        if object_ref is None:
            raise SemanticNodeError(
                "Station source became unavailable before typed lowering"
            )
        return IntentPlan(
            operation=self.operation,
            handler_id=self.handler_id,
            intents=(
                PlaceCountersIntent(
                    actor=context.actor,
                    object_refs=(object_ref,),
                    counter_name="charge",
                    amount=amount,
                    reason=reason,
                    source_ref=source_ref,
                    replacement_selections=tuple(raw_selections),
                ),
            ),
        )


STATION_HANDLERS = (StationCounterPlacementHandler(),)


__all__ = ["STATION_HANDLERS", "StationCounterPlacementHandler"]
