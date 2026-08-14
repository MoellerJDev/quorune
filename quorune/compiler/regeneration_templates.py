from __future__ import annotations

"""Closed Oracle lowering for self-regeneration activation effects."""

from dataclasses import dataclass
import re
from typing import Any, Mapping

from .fixed_source_effect_sequences import SOURCE_ZONE_OBJECT


@dataclass(frozen=True, slots=True)
class SelfRegenerationEffectTemplate:
    """One exact ``Regenerate this creature.`` instruction."""

    template_id: str = "regenerate-this-creature-v1"
    effects: tuple[Mapping[str, Any], ...] = (
        {"op": "regenerate", "card": SOURCE_ZONE_OBJECT},
    )
    target_schema: None = None
    mechanics: tuple[str, ...] = ("regenerate",)

    def compiled(
        self,
    ) -> tuple[
        str,
        tuple[Mapping[str, Any], ...],
        None,
        tuple[str, ...],
    ]:
        return (
            self.template_id,
            self.effects,
            self.target_schema,
            self.mechanics,
        )


def self_regeneration_effect_template(
    text: str,
) -> SelfRegenerationEffectTemplate | None:
    """Lower only the ordinary self-creature regeneration grammar."""

    normalized = " ".join(text.strip().split())
    if re.fullmatch(
        r"regenerate this creature\.",
        normalized,
        re.IGNORECASE,
    ) is None:
        return None
    return SelfRegenerationEffectTemplate()


__all__ = [
    "SelfRegenerationEffectTemplate",
    "self_regeneration_effect_template",
]
