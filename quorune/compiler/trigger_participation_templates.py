from __future__ import annotations

import re
from typing import Any, Mapping

from ..ability_fragments import ability_fragment_to_dict
from ..trigger_participation import (
    TriggerMultiplierPredicate,
    TriggerMultiplierSpec,
)


_PANHARMONICON_PATTERN = re.compile(
    r"If an artifact or creature entering causes a triggered ability of a "
    r"permanent you control to trigger, that ability triggers an additional "
    r"time\.?",
    re.IGNORECASE,
)
_CHOSEN_TYPE_PATTERN = re.compile(
    r"If a triggered ability of another creature you control of the chosen "
    r"type triggers, it triggers an additional time\.?",
    re.IGNORECASE,
)


def static_trigger_multiplier_handler(
    text: str,
) -> tuple[str, Mapping[str, Any], str] | None:
    """Compile the closed represented CR 603.2d static wording families."""

    normalized = " ".join(str(text).strip().split())
    if _PANHARMONICON_PATTERN.fullmatch(normalized):
        spec = TriggerMultiplierSpec(
            predicate=TriggerMultiplierPredicate.ARTIFACT_OR_CREATURE_ENTERS,
            exclude_self=False,
        )
        template_id = "static-trigger-multiplier-artifact-creature-enters-v1"
    elif _CHOSEN_TYPE_PATTERN.fullmatch(normalized):
        spec = TriggerMultiplierSpec(
            predicate=(
                TriggerMultiplierPredicate.ANOTHER_CREATURE_OF_CHOSEN_TYPE
            ),
            exclude_self=True,
        )
        template_id = "static-trigger-multiplier-chosen-creature-type-v1"
    else:
        return None
    return (
        template_id,
        {
            "handler_id": "ability.static.trigger-multiplier.v1",
            "schema_version": 1,
            "event": "continuous",
            "fragment": ability_fragment_to_dict(spec),
        },
        spec.capability_id,
    )


__all__ = ["static_trigger_multiplier_handler"]
