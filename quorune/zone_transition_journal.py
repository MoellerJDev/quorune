from __future__ import annotations

"""Privacy-preserving event journals for committed zone transitions."""

from .zone_transition_model import (
    HIDDEN_ZONES,
    JOURNAL_REASON_FIELD,
    ZoneDepartureSnapshot,
    ZoneMovePlan,
    ZoneTransitionHost,
)


def journal_zone_move(
    host: ZoneTransitionHost,
    plan: ZoneMovePlan,
    departure: ZoneDepartureSnapshot,
    *,
    reveal_to: tuple[str, ...],
    reason: str,
    log: bool,
) -> None:
    if not log:
        return
    card = plan.card
    identity_became_hidden = (
        card.zone in HIDDEN_ZONES and not plan.origin_identity_public
    )
    if identity_became_hidden:
        host._log(
            None,
            "zone.move",
            f"{card.owner} moved a card: {departure.origin} → {card.zone}.",
            {
                "from": departure.origin,
                "to": card.zone,
                JOURNAL_REASON_FIELD: reason,
            },
            changed_objects=[card.object_id],
            changed_players=[card.owner, card.controller],
        )
        host._log(
            None,
            "zone.move.private",
            f"{card.ref} {card.printed_name}: {departure.origin} → {card.zone}.",
            {
                "object": card.ref,
                "from": departure.origin,
                "to": card.zone,
                JOURNAL_REASON_FIELD: reason,
                "tapped": card.tapped,
            },
            visibility=sorted({card.owner, "analyst", *reveal_to}),
            changed_objects=[card.object_id],
            changed_players=[card.owner, card.controller],
        )
        return
    host._log(
        None,
        "zone.move",
        f"{card.ref} {card.printed_name}: {departure.origin} → {card.zone}.",
        {
            "object": card.ref,
            "from": departure.origin,
            "to": card.zone,
            JOURNAL_REASON_FIELD: reason,
            "tapped": card.tapped,
        },
        changed_objects=[card.object_id],
        changed_players=[card.owner, card.controller],
    )


__all__ = ["journal_zone_move"]
