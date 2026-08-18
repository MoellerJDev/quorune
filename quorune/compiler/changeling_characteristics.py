from __future__ import annotations

from ..ability_fragments import (
    AllCreatureTypesCharacteristicDefinitionSpec,
    ability_fragment_to_dict,
)
from .ability_keyword_fragment_model import AbilityKeywordFragmentLowering


CHANGELING_MECHANIC_ID = "changeling"
CHANGELING_FRAGMENT_HANDLER_ID = (
    "ability.static.all-creature-types-characteristic-definition.v1"
)


def lower_changeling_characteristic_fragment(
    material_line: str,
    mechanics: tuple[str, ...],
) -> AbilityKeywordFragmentLowering | None:
    """Lower ordinary Changeling to one copied layer-4 CDA fragment."""

    if mechanics != (CHANGELING_MECHANIC_ID,):
        return None
    if material_line.strip().rstrip(".").casefold() != CHANGELING_MECHANIC_ID:
        return AbilityKeywordFragmentLowering(
            residual_kind="unsupported_changeling_wording",
            residual_reason=(
                "Changeling requires one ordinary printed keyword instance"
            ),
            residual_blockers=("ordinary printed Changeling",),
        )
    return AbilityKeywordFragmentLowering(
        handlers=(
            {
                "handler_id": CHANGELING_FRAGMENT_HANDLER_ID,
                "schema_version": 1,
                "event": "continuous",
                "fragment": ability_fragment_to_dict(
                    AllCreatureTypesCharacteristicDefinitionSpec()
                ),
            },
        )
    )


__all__ = [
    "CHANGELING_FRAGMENT_HANDLER_ID",
    "CHANGELING_MECHANIC_ID",
    "lower_changeling_characteristic_fragment",
]
