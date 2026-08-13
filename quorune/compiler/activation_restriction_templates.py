from __future__ import annotations

"""Closed Oracle grammar for static activation restrictions."""

import re
from typing import Any, Mapping

from ..semantic_runtime.activation_restrictions import (
    ACTIVATION_PERMISSION_EVENT,
    CHOSEN_NAME_NONMANA_PROHIBITION_HANDLER_ID,
)


ActivationRestrictionHandlerTemplate = tuple[str, Mapping[str, Any], str]


_CHOSEN_NAME_NONMANA_PROHIBITION = re.compile(
    r"^Activated abilities of sources with the chosen name can['’]t be "
    r"activated unless they['’]re mana abilities\.?$",
    re.IGNORECASE,
)


def static_activation_restriction_handler(
    text: str,
) -> ActivationRestrictionHandlerTemplate | None:
    """Lower only the exact chosen-name nonmana prohibition sentence."""

    if _CHOSEN_NAME_NONMANA_PROHIBITION.fullmatch(text.strip()) is None:
        return None
    return (
        "chosen-name-nonmana-activation-prohibition-v1",
        {
            "handler_id": CHOSEN_NAME_NONMANA_PROHIBITION_HANDLER_ID,
            "schema_version": 1,
            "event": ACTIVATION_PERMISSION_EVENT,
            "source_name_relation": "chosen_name",
            "ability_scope": "nonmana",
        },
        "activation.restriction.chosen_name_nonmana",
    )


__all__ = [
    "ActivationRestrictionHandlerTemplate",
    "static_activation_restriction_handler",
]
