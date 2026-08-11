from __future__ import annotations

"""Read-only target identity snapshots shared by proposal and revalidation."""

from typing import Any, Mapping, Protocol


class TargetIdentityQuery(Protocol):
    state: Any

    def _effective_card_data(self, card: Any) -> Mapping[str, Any]: ...


def target_snapshot(host: TargetIdentityQuery, ref: str) -> dict[str, Any]:
    if ref in host.state.players:
        return {
            "ref": ref,
            "category": "player",
            "controller": ref,
            "owner": ref,
            "colors": [],
            "mana_value": 0,
            "type_line": "Player",
        }
    item = next(
        (candidate for candidate in host.state.stack if candidate.ref == ref),
        None,
    )
    if item is not None:
        card = host.state.cards.get(item.card_object_id or "")
        data = host._effective_card_data(card) if card else {}
        return {
            "ref": ref,
            "stack_id": item.stack_id,
            "category": (
                "spell" if item.kind in {"spell", "spell_copy"} else "ability"
            ),
            "controller": item.controller,
            "owner": card.owner if card else item.controller,
            "colors": list(data.get("colors", [])),
            "mana_value": float(
                data.get("mana_value", data.get("cmc", 0)) or 0
            ),
            "type_line": str(data.get("type_line") or ""),
        }
    card = next(
        (
            candidate
            for candidate in host.state.cards.values()
            if candidate.ref == ref
        ),
        None,
    )
    if card is None:
        return {"ref": ref}
    data = host._effective_card_data(card)
    return {
        "ref": ref,
        "object_id": card.object_id,
        "zone_change_counter": card.zone_change_counter,
        "zone": card.zone,
        "category": "permanent" if card.zone == "battlefield" else "card",
        "controller": card.controller,
        "owner": card.owner,
        "colors": list(data.get("colors", [])),
        "mana_value": float(data.get("mana_value", data.get("cmc", 0)) or 0),
        "type_line": str(data.get("type_line") or ""),
    }


def target_identity_matches_snapshot(
    host: TargetIdentityQuery,
    ref: str,
    snapshot: Mapping[str, Any],
) -> bool:
    """Return whether ``ref`` is still the originally selected object."""

    stack_id = snapshot.get("stack_id")
    if stack_id is not None:
        return any(
            item.ref == ref and item.stack_id == stack_id
            for item in host.state.stack
        )
    object_id = snapshot.get("object_id")
    incarnation = snapshot.get("zone_change_counter")
    if object_id is None or incarnation is None:
        # Historical Game Record v3 decisions predate explicit incarnations.
        return True
    card = host.state.cards.get(str(object_id))
    return bool(
        card is not None
        and card.ref == ref
        and card.zone_change_counter == int(incarnation)
    )


__all__ = ["target_identity_matches_snapshot", "target_snapshot"]
