from __future__ import annotations

"""Object-local state reset for CR 400.7 zone transitions."""

from .model import CardInstance


class ZoneObjectStateError(ValueError):
    """A zone-object reset request is malformed."""


def reset_card_after_zone_change(
    card: CardInstance,
    *,
    destination: str,
    stack_to_battlefield: bool,
) -> None:
    """Reset state that the new zone object cannot retain.

    Zone-list mutation, timestamps, attachment graph cleanup, and event
    dispatch remain with their existing owners.  This boundary owns only the
    state stored on one card object after the host has established that CR
    400.7 creates a new object or applies the spell-to-permanent exception.
    """

    if not isinstance(card, CardInstance):
        raise ZoneObjectStateError("Zone-object reset requires one card")
    if type(destination) is not str or not destination:
        raise ZoneObjectStateError(
            "Zone-object reset requires a destination"
        )
    if type(stack_to_battlefield) is not bool:
        raise ZoneObjectStateError(
            "Zone-object reset requires an exact transition kind"
        )

    card.tapped = False
    card.marked_damage = 0
    card.deathtouch_damage = False
    card.regeneration_shields = 0
    card.temporary_keywords.clear()
    card.goaded_by.clear()
    card.monstrous_value = None
    card.renowned = False
    card.attacking = None
    card.blocking = None
    card.attached_to = None
    card.attachments.clear()
    card.phased_out = False
    if not stack_to_battlefield:
        card.battle_protector = None

    # CR 400.7 gives the destination a new logical object. Retain only state
    # covered by an implemented exception or by initial copiable token data.
    retained_annotation_keys = {
        "object_characteristics",
        "token_characteristics",
    }
    if card.is_token or card.object_kind in {
        "spell_copy",
        "card_copy",
    }:
        retained_annotation_keys.update(
            {"copied_from", "copy_overrides"}
        )
    if stack_to_battlefield:
        retained_annotation_keys.update(
            {
                "bestowed",
                "chosen_creature_type",
                "chosen_creature_type_adds_subtype",
                "chosen_name",
                "copy_overrides",
                "evoked",
                "pending_aura_target",
                "pending_aura_zone",
            }
        )
    card.annotations = {
        key: value
        for key, value in card.annotations.items()
        if key in retained_annotation_keys
    }
    card.counters.clear()
    if not stack_to_battlefield:
        card.active_face = None
        card.face_down = False
    if destination != "battlefield":
        card.controller = card.owner


__all__ = [
    "ZoneObjectStateError",
    "reset_card_after_zone_change",
]
