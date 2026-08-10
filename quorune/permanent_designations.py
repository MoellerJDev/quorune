from __future__ import annotations

"""Typed ownership for noncopiable designations of a permanent.

The first represented designation is CR 701.37b's monstrous marker.  It is
stored on the current logical object, is public, survives control changes and
phasing, and is cleared by the canonical zone-change owner.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence


class PermanentDesignationError(ValueError):
    """A permanent designation request is malformed or stale."""


class PermanentDesignationHost(Protocol):
    state: Any

    def _log(
        self,
        actor: str | None,
        code: str,
        summary: str,
        details: Mapping[str, Any] | None = None,
        *,
        importance: int = 1,
        changed_objects: Sequence[str] = (),
        changed_players: Sequence[str] = (),
    ) -> None: ...

    def _dispatch_semantic_event(
        self,
        event: str,
        context: Mapping[str, Any],
        **kwargs: Any,
    ) -> list[str]: ...


@dataclass(frozen=True, slots=True)
class BecomeMonstrousRequest:
    """One identity-pinned CR 701.37 designation transition."""

    object_id: str
    object_ref: str
    logical_object_id: str
    value: int
    actor: str
    reason: str

    def __post_init__(self) -> None:
        if any(
            type(value) is not str or not value
            for value in (
                self.object_id,
                self.object_ref,
                self.logical_object_id,
                self.actor,
                self.reason,
            )
        ):
            raise PermanentDesignationError(
                "Monstrous designation identity and provenance are required"
            )
        if type(self.value) is not int or self.value < 0:
            raise PermanentDesignationError(
                "Monstrosity requires an exact nonnegative value"
            )


@dataclass(frozen=True, slots=True)
class MonstrousDesignationResult:
    object_ref: str
    logical_object_id: str
    value: int | None
    changed: bool


def become_monstrous(
    host: PermanentDesignationHost,
    request: BecomeMonstrousRequest,
) -> MonstrousDesignationResult:
    """Apply one CR 701.37a-b transition without copying or rediscovery.

    A source that left the battlefield or became a new logical object cannot
    be affected by the old resolving ability.  That is an ordinary impossible
    instruction, so the request becomes a deterministic no-op rather than
    finding a new object through its public reference.
    """

    if not isinstance(request, BecomeMonstrousRequest):
        raise PermanentDesignationError(
            "Monstrous designation requires a typed request"
        )
    card = host.state.cards.get(request.object_id)
    if (
        card is None
        or card.ref != request.object_ref
        or card.logical_object_id != request.logical_object_id
        or card.zone != "battlefield"
        or card.phased_out
    ):
        return MonstrousDesignationResult(
            object_ref=request.object_ref,
            logical_object_id=request.logical_object_id,
            value=None,
            changed=False,
        )
    if card.monstrous_value is not None:
        if (
            type(card.monstrous_value) is not int
            or card.monstrous_value < 0
        ):
            raise PermanentDesignationError(
                "The permanent's monstrous designation is malformed"
            )
        return MonstrousDesignationResult(
            object_ref=card.ref,
            logical_object_id=card.logical_object_id,
            value=card.monstrous_value,
            changed=False,
        )

    card.monstrous_value = request.value
    details = {
        "object": card.ref,
        "logical_object_id": card.logical_object_id,
        "value": request.value,
        "controller": card.controller,
        "reason": request.reason,
    }
    host._log(
        request.actor,
        "permanent.monstrous",
        f"{card.ref} became monstrous.",
        details,
        importance=2,
        changed_objects=[card.object_id],
        changed_players=[card.controller],
    )
    host._dispatch_semantic_event(
        "permanent.becomes_monstrous",
        details,
        sources=(card,),
    )
    return MonstrousDesignationResult(
        object_ref=card.ref,
        logical_object_id=card.logical_object_id,
        value=request.value,
        changed=True,
    )


__all__ = [
    "BecomeMonstrousRequest",
    "MonstrousDesignationResult",
    "PermanentDesignationError",
    "PermanentDesignationHost",
    "become_monstrous",
]
