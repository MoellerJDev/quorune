from __future__ import annotations

"""Typed immutable Scry arrangements and their authoritative mutation owner."""

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


class ScryError(ValueError):
    """A Scry instruction, arrangement, or current library is malformed."""


_LIBRARY_ZONE = "library"


def _refs(value: Any, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ScryError(f"{field} must be a list of object references")
    result = tuple(value)
    if any(type(ref) is not str or not ref for ref in result):
        raise ScryError(f"{field} must contain nonempty object references")
    if len(result) != len(set(result)):
        raise ScryError(f"{field} must not contain duplicate references")
    return result


@dataclass(frozen=True, slots=True)
class ScryArrangement:
    """One exact partition and ordering of the cards looked at for Scry."""

    looked_top_first: tuple[str, ...]
    top_top_first: tuple[str, ...]
    bottom_bottom_first: tuple[str, ...]
    legacy_subset_response: bool = False

    def __post_init__(self) -> None:
        looked = _refs(self.looked_top_first, field="looked_top_first")
        if not looked:
            raise ScryError("A Scry arrangement requires looked-at cards")
        top = _refs(self.top_top_first, field="top_top_first")
        bottom = _refs(
            self.bottom_bottom_first,
            field="bottom_bottom_first",
        )
        if set(top).intersection(bottom):
            raise ScryError("Scry top and bottom groups must be disjoint")
        if len(top) + len(bottom) != len(looked) or set((*top, *bottom)) != set(
            looked
        ):
            raise ScryError(
                "Scry top and bottom groups must partition every looked-at card"
            )
        if type(self.legacy_subset_response) is not bool:
            raise ScryError("Scry legacy-response state must be boolean")
        object.__setattr__(self, "looked_top_first", looked)
        object.__setattr__(self, "top_top_first", top)
        object.__setattr__(self, "bottom_bottom_first", bottom)

    @classmethod
    def from_response(
        cls,
        looked_top_first: tuple[str, ...],
        response: Mapping[str, Any],
    ) -> "ScryArrangement":
        cards = response.get("cards")
        if isinstance(cards, (list, tuple)):
            bottom = _refs(cards, field="cards")
            if any(ref not in looked_top_first for ref in bottom):
                raise ScryError(
                    "Legacy Scry bottom choices must be looked-at cards"
                )
            selected = set(bottom)
            return cls(
                looked_top_first=looked_top_first,
                top_top_first=tuple(
                    ref for ref in looked_top_first if ref not in selected
                ),
                bottom_bottom_first=bottom,
                legacy_subset_response=True,
            )
        if not isinstance(cards, Mapping) or set(cards) != {"top", "bottom"}:
            raise ScryError(
                "Scry cards must contain exactly top and bottom orderings"
            )
        return cls(
            looked_top_first=looked_top_first,
            top_top_first=_refs(cards["top"], field="cards.top"),
            bottom_bottom_first=_refs(
                cards["bottom"],
                field="cards.bottom",
            ),
        )


class ScryCommitHost(Protocol):
    state: Any

    def _resolve_object(
        self,
        actor: str,
        ref: str,
        *,
        zones: set[str],
        owned_only: bool = False,
    ) -> Any: ...

    def _log(
        self,
        actor: str,
        code: str,
        message: str,
        details: Mapping[str, Any],
        **kwargs: Any,
    ) -> Any: ...


def commit_scry_arrangement(
    host: ScryCommitHost,
    *,
    actor: str,
    player: str,
    arrangement: ScryArrangement,
    reason: str,
) -> tuple[str, ...]:
    """Atomically apply one previously prepared Scry arrangement."""

    library = host.state.players[player].zones[_LIBRARY_ZONE]
    looked_ids = tuple(
        host._resolve_object(
            actor,
            ref,
            zones={_LIBRARY_ZONE},
            owned_only=(actor == player),
        ).object_id
        for ref in arrangement.looked_top_first
    )
    current_top = tuple(reversed(library[-len(looked_ids) :]))
    if current_top != looked_ids:
        raise ScryError("The looked-at library top changed before Scry completed")
    by_ref = dict(zip(arrangement.looked_top_first, looked_ids, strict=True))
    untouched = library[: len(library) - len(looked_ids)]
    bottom_ids = [by_ref[ref] for ref in arrangement.bottom_bottom_first]
    top_ids = [by_ref[ref] for ref in arrangement.top_top_first]
    library[:] = [*bottom_ids, *untouched, *reversed(top_ids)]
    changed_ids = (
        bottom_ids
        if arrangement.legacy_subset_response
        else [*bottom_ids, *top_ids]
    )
    host._log(
        actor,
        "library.scry",
        f"{actor} put {len(bottom_ids)} card(s) on the bottom.",
        {
            "count": len(looked_ids),
            "bottom_count": len(bottom_ids),
        },
        visibility=[actor, "analyst"],
        importance=1,
        changed_objects=changed_ids,
    )
    return arrangement.looked_top_first


__all__ = [
    "ScryArrangement",
    "ScryCommitHost",
    "ScryError",
    "commit_scry_arrangement",
]
