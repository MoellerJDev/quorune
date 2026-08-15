from __future__ import annotations

"""Typed CR 702.184 Station activation and resolution references."""

from dataclasses import dataclass, replace
import re
from typing import Any, Mapping, Protocol, Sequence

from .abilities import ActivatedAbility, CostChoice
from .object_query import exact_numeric_characteristic
from .tap_state import set_permanent_tapped
from .util import normalize_mana_bundle


STATION_HANDLER_ID = "ability.activated.station.v1"
STATION_MECHANIC_ID = "station"
STATION_CAPABILITY_ID = "counter.producer.station"
STATION_COST_KIND = "station"
STATION_CONTEXT_KEY = "station"
_ABILITY_ID = re.compile(r"^ab[1-9][0-9]*$")


class StationAbilityError(ValueError):
    """A Station descriptor, cost, or characteristic reference is invalid."""


def _exact_fields(
    value: Mapping[str, Any], expected: set[str], *, field: str
) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing:
        raise StationAbilityError(
            f"{field} is missing required fields: {', '.join(missing)}"
        )
    if unknown:
        raise StationAbilityError(
            f"{field} has unknown fields: {', '.join(unknown)}"
        )


@dataclass(frozen=True, slots=True)
class OrdinaryStationAbilitySpec:
    ability_id: str
    line_index: int
    oracle_line: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.ability_id, str)
            or _ABILITY_ID.fullmatch(self.ability_id) is None
        ):
            raise StationAbilityError("Station ability ID must be abN")
        if type(self.line_index) is not int or self.line_index < 0:
            raise StationAbilityError(
                "Station ability line_index must be nonnegative"
            )
        if not isinstance(self.oracle_line, str) or not self.oracle_line:
            raise StationAbilityError("Station oracle_line must be nonempty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ability_id": self.ability_id,
            "line_index": self.line_index,
            "oracle_line": self.oracle_line,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "OrdinaryStationAbilitySpec":
        _exact_fields(
            value,
            {"ability_id", "line_index", "oracle_line"},
            field="ordinary Station ability",
        )
        return cls(**dict(value))

    def to_activated_ability(self) -> ActivatedAbility:
        return ActivatedAbility(
            ability_id=self.ability_id,
            line_index=self.line_index,
            oracle_line=self.oracle_line,
            cost_text="Tap another untapped creature you control",
            effect_text=(
                "Put charge counters on this permanent equal to the tapped "
                "creature's power."
            ),
            zones=("battlefield",),
            mana=normalize_mana_bundle(None),
            choices=(
                CostChoice(
                    kind=STATION_COST_KIND,
                    zone="battlefield",
                    card_type="creature",
                    another=True,
                ),
            ),
            sorcery_speed=True,
        )


def compile_ordinary_station_ability(
    *,
    material_line: str,
    oracle_line: str,
    line_index: int,
) -> OrdinaryStationAbilitySpec | None:
    """Compile exactly one ordinary printed Station keyword instance."""

    if material_line.strip().rstrip(".").casefold() != STATION_MECHANIC_ID:
        return None
    return OrdinaryStationAbilitySpec(
        ability_id=f"ab{line_index + 1}",
        line_index=line_index,
        oracle_line=oracle_line,
    )


def ordinary_station_handler_descriptor(
    spec: OrdinaryStationAbilitySpec,
) -> dict[str, Any]:
    return {
        "handler_id": STATION_HANDLER_ID,
        "schema_version": 1,
        "event": "activate",
        "ability": spec.to_dict(),
    }


def station_cost_choice(ability: ActivatedAbility) -> CostChoice | None:
    """Return the one closed Station cost choice carried by an ability."""

    matches = tuple(
        choice
        for choice in ability.choices
        if choice.kind == STATION_COST_KIND
    )
    if not matches:
        return None
    expected = CostChoice(
        kind=STATION_COST_KIND,
        zone="battlefield",
        card_type="creature",
        another=True,
    )
    if len(ability.choices) != 1 or matches != (expected,):
        raise StationAbilityError(
            "Station requires exactly one other battlefield creature cost"
        )
    return matches[0]


class StationHost(Protocol):
    state: Any

    def _effective_card_data(self, card: Any) -> Mapping[str, Any]: ...

    def _type_parts(
        self, type_line: str
    ) -> tuple[set[str], set[str], set[str]]: ...

    def _log(
        self,
        actor: str | None,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        *,
        importance: int = 1,
        changed_objects: list[str] | None = None,
        changed_players: list[str] | None = None,
    ) -> Any: ...


def _current_power(host: StationHost, card: Any) -> int:
    effective = host._effective_card_data(card)
    if not isinstance(effective, Mapping):
        raise StationAbilityError(
            "Station effective characteristics must be an object"
        )
    type_line = effective.get("type_line")
    if not isinstance(type_line, str) or not type_line.strip():
        raise StationAbilityError(
            "Station effective characteristics require a type line"
        )
    card_types = host._type_parts(type_line)[0]
    if "creature" not in {value.casefold() for value in card_types}:
        raise StationAbilityError(
            "Station cost-creature type changes before resolution are outside "
            "the trusted slice"
        )
    power = exact_numeric_characteristic(card, effective, "power")
    if power is None:
        raise StationAbilityError("Station creature power is unresolved")
    return power


@dataclass(frozen=True, slots=True)
class StationCandidate:
    object_id: str
    object_ref: str
    logical_object_id: str
    activation_power: int

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value
            for value in (
                self.object_id,
                self.object_ref,
                self.logical_object_id,
            )
        ):
            raise StationAbilityError("Station candidate identity is required")
        if type(self.activation_power) is not int:
            raise StationAbilityError(
                "Station candidate power must be an exact integer"
            )

    @property
    def ref(self) -> str:
        return self.object_ref


@dataclass(frozen=True, slots=True)
class StationPowerReference:
    object_id: str
    logical_object_id: str
    reference: str
    last_known_power: int | None = None
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise StationAbilityError(
                "Unsupported Station power-reference schema version"
            )
        if not all(
            isinstance(value, str) and value
            for value in (
                self.object_id,
                self.logical_object_id,
                self.reference,
            )
        ):
            raise StationAbilityError(
                "Station power-reference identity is required"
            )
        if self.last_known_power is not None and type(
            self.last_known_power
        ) is not int:
            raise StationAbilityError(
                "Station last-known power must be an exact integer or null"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "object_id": self.object_id,
            "logical_object_id": self.logical_object_id,
            "reference": self.reference,
            "last_known_power": self.last_known_power,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "StationPowerReference":
        _exact_fields(
            value,
            {
                "schema_version",
                "object_id",
                "logical_object_id",
                "reference",
                "last_known_power",
            },
            field="Station power reference",
        )
        return cls(**dict(value))


@dataclass(frozen=True, slots=True)
class StationCostPlan:
    seat: str
    source_object_id: str
    source_logical_object_id: str
    selected: StationCandidate

    def __post_init__(self) -> None:
        if not isinstance(self.seat, str) or not self.seat:
            raise StationAbilityError("Station cost seat is required")
        if not isinstance(self.source_object_id, str) or not self.source_object_id:
            raise StationAbilityError("Station source identity is required")
        if (
            not isinstance(self.source_logical_object_id, str)
            or not self.source_logical_object_id
        ):
            raise StationAbilityError(
                "Station source logical identity is required"
            )
        if not isinstance(self.selected, StationCandidate):
            raise StationAbilityError(
                "Station cost requires one typed creature candidate"
            )

    def context_dict(self) -> dict[str, Any]:
        return StationPowerReference(
            object_id=self.selected.object_id,
            logical_object_id=self.selected.logical_object_id,
            reference=self.selected.object_ref,
        ).to_dict()


def station_candidates(
    host: StationHost,
    seat: str,
    source: Any,
) -> tuple[StationCandidate, ...]:
    """Return exact payable Station cost creatures in battlefield order."""

    if not isinstance(seat, str) or seat not in host.state.players:
        raise StationAbilityError("Station seat is unavailable")
    if (
        getattr(source, "zone", None) != "battlefield"
        or bool(getattr(source, "phased_out", False))
    ):
        return ()
    result: list[StationCandidate] = []
    for object_id in host.state.players[seat].zones["battlefield"]:
        card = host.state.cards[object_id]
        if (
            object_id == source.object_id
            or card.controller != seat
            or card.phased_out
            or card.tapped
        ):
            continue
        effective = host._effective_card_data(card)
        card_types = host._type_parts(
            str(effective.get("type_line") or "")
        )[0]
        if "creature" not in card_types:
            continue
        power = exact_numeric_characteristic(card, effective, "power")
        if power is None:
            raise StationAbilityError("Station creature power is unresolved")
        result.append(
            StationCandidate(
                object_id=card.object_id,
                object_ref=card.ref,
                logical_object_id=card.logical_object_id,
                activation_power=power,
            )
        )
    return tuple(result)


def _submitted_ref(response: Mapping[str, Any]) -> str:
    has_cards = "cost_cards" in response
    has_objects = "cost_objects" in response
    if has_cards and has_objects:
        raise StationAbilityError(
            "Submit only one Station cost-object field"
        )
    raw = (
        response.get("cost_cards")
        if has_cards
        else response.get("cost_objects") if has_objects else ()
    )
    if (
        not isinstance(raw, (list, tuple))
        or len(raw) != 1
        or type(raw[0]) is not str
        or not raw[0]
    ):
        raise StationAbilityError(
            "Station requires exactly one cost creature reference"
        )
    return raw[0]


def prepare_station_cost(
    host: StationHost,
    *,
    seat: str,
    source: Any,
    response: Mapping[str, Any],
) -> StationCostPlan:
    """Validate one Station tap cost completely before mutation."""

    if (
        source.zone != "battlefield"
        or source.controller != seat
        or source.phased_out
    ):
        raise StationAbilityError("Station source is no longer available")
    selected_ref = _submitted_ref(response)
    available = {
        candidate.object_ref: candidate
        for candidate in station_candidates(host, seat, source)
    }
    selected = available.get(selected_ref)
    if selected is None:
        raise StationAbilityError(
            "Station cost must be another untapped creature you control"
        )
    return StationCostPlan(
        seat=seat,
        source_object_id=source.object_id,
        source_logical_object_id=source.logical_object_id,
        selected=selected,
    )


def commit_station_cost(
    host: StationHost,
    plan: StationCostPlan,
) -> tuple[list[str], dict[str, Any]]:
    """Revalidate and commit one Station cost through the tap-state owner."""

    source = host.state.cards.get(plan.source_object_id)
    if (
        source is None
        or source.zone != "battlefield"
        or source.controller != plan.seat
        or source.phased_out
        or source.logical_object_id != plan.source_logical_object_id
    ):
        raise StationAbilityError("Station source changed before commitment")
    current = {
        candidate.object_id: candidate
        for candidate in station_candidates(host, plan.seat, source)
    }.get(plan.selected.object_id)
    if current != plan.selected:
        raise StationAbilityError(
            "Station cost creature changed before commitment"
        )
    set_permanent_tapped(
        host,
        plan.selected.object_ref,
        actor=plan.seat,
        tapped=True,
        reason="Station activation cost",
        logical_object_id=plan.selected.logical_object_id,
        log=False,
    )
    host._log(
        plan.seat,
        "cost.station",
        (
            f"{plan.seat} tapped {plan.selected.object_ref} to station "
            f"{source.ref}."
        ),
        {
            "source": source.ref,
            "creature": plan.selected.object_ref,
            "activation_power": plan.selected.activation_power,
        },
        importance=1,
        changed_objects=[plan.selected.object_id],
        changed_players=[plan.seat],
    )
    return [plan.selected.object_id], plan.context_dict()


def pay_station_cost(
    host: StationHost,
    *,
    seat: str,
    source: Any,
    response: Mapping[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    return commit_station_cost(
        host,
        prepare_station_cost(
            host,
            seat=seat,
            source=source,
            response=response,
        ),
    )


def station_reference_identities(
    stack_items: Sequence[Any],
) -> frozenset[tuple[str, str]]:
    identities: set[tuple[str, str]] = set()
    for item in stack_items:
        context = getattr(item, "context", None)
        if not isinstance(context, Mapping):
            continue
        raw = context.get(STATION_CONTEXT_KEY)
        if not isinstance(raw, Mapping):
            continue
        reference = StationPowerReference.from_dict(raw)
        identities.add((reference.object_id, reference.logical_object_id))
    return frozenset(identities)


def pin_station_departures(
    stack_items: Sequence[Any],
    departures: Sequence[tuple[str, str, int]],
) -> int:
    """Pin predeparture power for every matching pending Station ability."""

    by_identity = {
        (object_id, logical_object_id): power
        for object_id, logical_object_id, power in departures
    }
    if len(by_identity) != len(tuple(departures)):
        raise StationAbilityError(
            "Station departure identities must be unique"
        )
    prepared: list[tuple[Any, dict[str, Any]]] = []
    for item in stack_items:
        context = getattr(item, "context", None)
        if not isinstance(context, Mapping):
            continue
        raw = context.get(STATION_CONTEXT_KEY)
        if not isinstance(raw, Mapping):
            continue
        reference = StationPowerReference.from_dict(raw)
        power = by_identity.get(
            (reference.object_id, reference.logical_object_id)
        )
        if power is None:
            continue
        prepared.append(
            (
                item,
                {
                    **dict(context),
                    STATION_CONTEXT_KEY: replace(
                        reference,
                        last_known_power=power,
                    ).to_dict(),
                },
            )
        )
    for item, context in prepared:
        item.context = context
    return len(prepared)


def pin_host_station_departures(
    host: StationHost,
    cards: Sequence[Any],
    *,
    error_type: type[Exception] = StationAbilityError,
) -> int:
    """Capture all needed Station LKI before a battlefield mutation."""

    try:
        identities = station_reference_identities(host.state.stack)
        departures = tuple(
            (
                card.object_id,
                card.logical_object_id,
                _current_power(host, card),
            )
            for card in cards
            if getattr(card, "zone", None) == "battlefield"
            and (card.object_id, card.logical_object_id) in identities
        )
        return pin_station_departures(host.state.stack, departures)
    except StationAbilityError as exc:
        if error_type is StationAbilityError:
            raise
        raise error_type(str(exc)) from exc


def station_resolution_power(host: StationHost, item: Any) -> int:
    """Return current or predeparture Station power, clamped at zero."""

    context = getattr(item, "context", None)
    if not isinstance(context, Mapping):
        raise StationAbilityError("Station stack context is malformed")
    raw = context.get(STATION_CONTEXT_KEY)
    if not isinstance(raw, Mapping):
        raise StationAbilityError("Station stack context is missing")
    reference = StationPowerReference.from_dict(raw)
    card = host.state.cards.get(reference.object_id)
    if (
        card is not None
        and card.zone == "battlefield"
        and card.logical_object_id == reference.logical_object_id
    ):
        if card.phased_out:
            raise StationAbilityError(
                "Station cost-creature phasing is outside the trusted slice"
            )
        return max(0, _current_power(host, card))
    if reference.last_known_power is None:
        raise StationAbilityError(
            "Station departed creature lacks last-known power"
        )
    return max(0, reference.last_known_power)


__all__ = [
    "OrdinaryStationAbilitySpec",
    "STATION_CAPABILITY_ID",
    "STATION_CONTEXT_KEY",
    "STATION_COST_KIND",
    "STATION_HANDLER_ID",
    "STATION_MECHANIC_ID",
    "StationAbilityError",
    "StationCandidate",
    "StationCostPlan",
    "StationPowerReference",
    "commit_station_cost",
    "compile_ordinary_station_ability",
    "ordinary_station_handler_descriptor",
    "pay_station_cost",
    "pin_host_station_departures",
    "pin_station_departures",
    "prepare_station_cost",
    "station_candidates",
    "station_cost_choice",
    "station_reference_identities",
    "station_resolution_power",
]
