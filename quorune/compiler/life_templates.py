from __future__ import annotations

"""Closed Oracle lowering for fixed life-gain and life-loss effects."""

from dataclasses import dataclass
import re
from typing import Any, Mapping

from .fixed_numbers import FIXED_COUNT_PATTERN, fixed_number


LIFE_MECHANIC = "cr-119-life"
_LIFE_OPERATION = "life"

_DOUBLE_CONTROLLER_LIFE_GAIN = re.compile(
    r"^If you would gain life, you gain twice that much life instead\.?$",
    re.IGNORECASE,
)


def static_life_handler(
    text: str,
) -> tuple[str, Mapping[str, Any], str] | None:
    """Lower one closed static life-change replacement wording family."""

    if _DOUBLE_CONTROLLER_LIFE_GAIN.fullmatch(text) is None:
        return None
    return (
        "life-gain-double-controller-static-v1",
        {
            "handler_id": "replacement.life.gain.multiplier.v1",
            "schema_version": 1,
            "event": "life.change",
            "condition": {
                "affected_player_relation": "source_controller",
            },
            "modification": {"multiplier": 2},
        },
        "life.gain.replacement.static_multiplier",
    )


@dataclass(frozen=True, slots=True)
class FixedLifeEffectTemplate:
    template_id: str
    effect: Mapping[str, Any]
    mechanic_ids: tuple[str, ...] = (LIFE_MECHANIC,)

    def compiled(
        self,
    ) -> tuple[
        str,
        tuple[Mapping[str, Any], ...],
        None,
        tuple[str, ...],
    ]:
        return self.template_id, (self.effect,), None, self.mechanic_ids


def fixed_life_effect_template(
    text: str,
) -> FixedLifeEffectTemplate | None:
    """Lower only positive fixed controller gain/loss and table loss."""

    normalized = " ".join(text.strip().split())
    match = re.fullmatch(
        rf"(?:you )?gain (?P<count>{FIXED_COUNT_PATTERN}) life\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        count = fixed_number(match.group("count"))
        if count <= 0:
            return None
        return FixedLifeEffectTemplate(
            template_id="gain-life-controller-v1",
            effect={
                "op": _LIFE_OPERATION,
                "player": "$controller",
                "delta": count,
            },
        )
    match = re.fullmatch(
        rf"(?:you )?lose (?P<count>{FIXED_COUNT_PATTERN}) life\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        count = fixed_number(match.group("count"))
        if count <= 0:
            return None
        return FixedLifeEffectTemplate(
            template_id="lose-life-controller-v1",
            effect={
                "op": "lose_life",
                "player": "$controller",
                "amount": count,
            },
        )
    match = re.fullmatch(
        rf"each opponent loses (?P<count>{FIXED_COUNT_PATTERN}) life\.?",
        normalized,
        re.IGNORECASE,
    )
    if match:
        count = fixed_number(match.group("count"))
        if count <= 0:
            return None
        return FixedLifeEffectTemplate(
            template_id="lose-life-each-opponent-v1",
            effect={
                "op": "lose_life_each_opponent",
                "amount": count,
            },
            mechanic_ids=(
                LIFE_MECHANIC,
                "cr-101-the-magic-golden-rules",
            ),
        )
    return None


__all__ = [
    "LIFE_MECHANIC",
    "FixedLifeEffectTemplate",
    "fixed_life_effect_template",
    "static_life_handler",
]
