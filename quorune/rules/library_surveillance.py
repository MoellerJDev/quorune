from __future__ import annotations

"""Typed fixed-count Surveil arrangement and authoritative commit owner."""

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from ..model import CardInstance
from .library_partition import (
    LibraryPartitionError,
    OrderedLibraryPartition,
    commit_ordered_library_partition,
    partition_refs,
)


class SurveilError(ValueError):
    """A Surveil instruction, arrangement, or current library is malformed."""


@dataclass(frozen=True, slots=True)
class SurveilObjectIdentity:
    object_id: str
    logical_object_id: str
    ref: str

    def __post_init__(self) -> None:
        if any(
            type(value) is not str or not value
            for value in (self.object_id, self.logical_object_id, self.ref)
        ):
            raise SurveilError("Surveil object identities must be complete")

    def to_dict(self) -> dict[str, str]:
        return {
            "object_id": self.object_id,
            "logical_object_id": self.logical_object_id,
            "ref": self.ref,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SurveilObjectIdentity":
        if not isinstance(value, Mapping) or set(value) != {
            "object_id",
            "logical_object_id",
            "ref",
        }:
            raise SurveilError("Surveil object identity fields are malformed")
        return cls(
            object_id=value["object_id"],
            logical_object_id=value["logical_object_id"],
            ref=value["ref"],
        )


@dataclass(frozen=True, slots=True)
class SurveilArrangement:
    """One exact private partition of the cards looked at for Surveil."""

    looked: tuple[SurveilObjectIdentity, ...]
    top_top_first: tuple[str, ...]
    graveyard_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        looked = tuple(self.looked)
        if (
            any(
                not isinstance(value, SurveilObjectIdentity)
                for value in looked
            )
            or len({value.object_id for value in looked}) != len(looked)
            or len({value.logical_object_id for value in looked}) != len(looked)
            or len({value.ref for value in looked}) != len(looked)
        ):
            raise SurveilError(
                "Surveil arrangements require unique looked-at identities"
            )
        try:
            top = partition_refs(
                self.top_top_first,
                field="top_top_first",
            )
            graveyard = partition_refs(
                self.graveyard_refs,
                field="graveyard_refs",
            )
        except LibraryPartitionError as exc:
            raise SurveilError(str(exc)) from exc
        if not looked:
            if top or graveyard:
                raise SurveilError(
                    "An empty Surveil arrangement cannot contain cards"
                )
            object.__setattr__(self, "looked", looked)
            object.__setattr__(self, "top_top_first", top)
            object.__setattr__(self, "graveyard_refs", graveyard)
            return
        try:
            partition = OrderedLibraryPartition(
                looked_top_first=tuple(value.ref for value in looked),
                top_top_first=top,
                destination_refs=graveyard,
                destination="graveyard",
            )
        except LibraryPartitionError as exc:
            raise SurveilError(str(exc)) from exc
        object.__setattr__(self, "looked", looked)
        object.__setattr__(self, "top_top_first", partition.top_top_first)
        object.__setattr__(self, "graveyard_refs", partition.destination_refs)

    @classmethod
    def from_response(
        cls,
        looked: tuple[SurveilObjectIdentity, ...],
        response: Mapping[str, Any],
    ) -> "SurveilArrangement":
        cards = response.get("cards")
        if not isinstance(cards, Mapping) or set(cards) != {
            "top",
            "graveyard",
        }:
            raise SurveilError(
                "Surveil cards must contain exactly top and graveyard groups"
            )
        try:
            top = partition_refs(cards["top"], field="cards.top")
            graveyard = partition_refs(
                cards["graveyard"],
                field="cards.graveyard",
            )
        except LibraryPartitionError as exc:
            raise SurveilError(str(exc)) from exc
        return cls(
            looked=looked,
            top_top_first=top,
            graveyard_refs=graveyard,
        )


@dataclass(frozen=True, slots=True)
class SurveilledCardResult:
    identity: SurveilObjectIdentity
    destination: str
    destination_logical_object_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.identity, SurveilObjectIdentity) or any(
            type(value) is not str or not value
            for value in (self.destination, self.destination_logical_object_id)
        ):
            raise SurveilError(
                "Surveilled-card results require typed destinations"
            )


@dataclass(frozen=True, slots=True)
class SurveilResult:
    player: str
    requested_count: int
    looked_count: int
    cards: tuple[SurveilledCardResult, ...]

    def __post_init__(self) -> None:
        cards = tuple(self.cards)
        if (
            type(self.player) is not str
            or not self.player
            or type(self.requested_count) is not int
            or self.requested_count <= 0
            or type(self.looked_count) is not int
            or self.looked_count < 0
            or self.looked_count > self.requested_count
            or len(cards) > self.looked_count
            or any(
                not isinstance(card, SurveilledCardResult)
                for card in cards
            )
        ):
            raise SurveilError("Surveil results require bounded typed cards")
        object.__setattr__(self, "cards", cards)


class SurveilCommitHost(Protocol):
    state: Any

    def _require_seat(self, seat: str, *, in_game: bool = False) -> None: ...

    def _resolve_object(
        self,
        actor: str,
        ref: str,
        *,
        zones: set[str],
        owned_only: bool = False,
    ) -> CardInstance: ...

    def _log(self, *args: Any, **kwargs: Any) -> None: ...

    def _dispatch_semantic_event(
        self,
        event: str,
        context: Mapping[str, Any],
        **kwargs: Any,
    ) -> Any: ...


def _validated_looked_ids(
    host: SurveilCommitHost,
    *,
    actor: str,
    player: str,
    arrangement: SurveilArrangement,
) -> dict[str, str]:
    host._require_seat(actor, in_game=True)
    host._require_seat(player, in_game=True)
    resolved: dict[str, str] = {}
    for identity in arrangement.looked:
        card = host._resolve_object(
            actor,
            identity.ref,
            zones={"library"},
            owned_only=(actor == player),
        )
        if (
            card.owner != player
            or card.object_id != identity.object_id
            or card.logical_object_id != identity.logical_object_id
        ):
            raise SurveilError(
                "A looked-at Surveil card changed identity before completion"
            )
        resolved[identity.ref] = identity.object_id
    library = host.state.players[player].zones["library"]
    looked_ids = tuple(identity.object_id for identity in arrangement.looked)
    current_top = tuple(reversed(library[-len(looked_ids) :]))
    if current_top != looked_ids:
        raise SurveilError(
            "The looked-at library top changed before Surveil completed"
        )
    return resolved


def commit_surveil_arrangement(
    host: SurveilCommitHost,
    *,
    actor: str,
    player: str,
    arrangement: SurveilArrangement,
    requested_count: int,
    reason: str,
    replacement_selections: Sequence[
        str | None | Mapping[str, Any]
    ] = (),
) -> SurveilResult:
    """Atomically commit one identity-pinned Surveil partition."""

    from ..zone_transition_model import PUBLIC_ZONES
    from ..zone_transitions import ZoneTransitionOwner

    if (
        type(requested_count) is not int
        or requested_count <= 0
        or type(reason) is not str
        or not reason
    ):
        raise SurveilError(
            "Surveil commits require a positive count and reason"
        )
    by_ref = _validated_looked_ids(
        host,
        actor=actor,
        player=player,
        arrangement=arrangement,
    )
    graveyard_ids = [by_ref[ref] for ref in arrangement.graveyard_refs]
    moved: Sequence[CardInstance] = (
        ZoneTransitionOwner(host).move_cards_simultaneously(
            [
                (object_id, "graveyard")
                for object_id in reversed(graveyard_ids)
            ],
            reason=reason,
            log=False,
            replacement_selections=replacement_selections,
        )
        if graveyard_ids
        else ()
    )
    library = host.state.players[player].zones["library"]
    top_ids = [by_ref[ref] for ref in arrangement.top_top_first]
    try:
        commit_ordered_library_partition(
            library,
            top_top_first=top_ids,
        )
    except LibraryPartitionError as exc:
        raise SurveilError(str(exc)) from exc
    identities = {identity.ref: identity for identity in arrangement.looked}
    moved_by_id = {card.object_id: card for card in moved}
    cards = tuple(
        SurveilledCardResult(
            identity=identities[ref],
            destination=card.zone,
            destination_logical_object_id=card.logical_object_id,
        )
        for ref in arrangement.graveyard_refs
        for card in (moved_by_id[by_ref[ref]],)
    )
    public_refs = [
        card.identity.ref
        for card in cards
        if card.destination in PUBLIC_ZONES
        and not host.state.cards[card.identity.object_id].face_down
    ]
    host._log(
        actor,
        "library.surveil",
        f"{player} surveilled {requested_count}.",
        {
            "player": player,
            "count": requested_count,
            "looked_count": len(arrangement.looked),
            "graveyard_count": len(cards),
            "objects": public_refs,
            "reason": reason,
        },
        importance=1,
        changed_objects=[identity.object_id for identity in arrangement.looked],
        changed_players=[player],
    )
    host._dispatch_semantic_event(
        "player.surveilled",
        {
            "player": player,
            "count": requested_count,
            "looked_count": len(arrangement.looked),
            "graveyard_count": len(cards),
        },
    )
    return SurveilResult(
        player=player,
        requested_count=requested_count,
        looked_count=len(arrangement.looked),
        cards=cards,
    )


__all__ = [
    "commit_surveil_arrangement",
    "SurveilArrangement",
    "SurveilCommitHost",
    "SurveilError",
    "SurveilObjectIdentity",
    "SurveilResult",
    "SurveilledCardResult",
]
