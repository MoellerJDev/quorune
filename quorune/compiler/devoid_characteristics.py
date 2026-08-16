from __future__ import annotations

from ..ability_fragments import (
    ColorlessCharacteristicDefinitionSpec,
    ability_fragment_to_dict,
)
from .ability_keyword_fragment_model import AbilityKeywordFragmentLowering


DEVOID_MECHANIC_ID = "devoid"
DEVOID_FRAGMENT_HANDLER_ID = (
    "ability.static.colorless-characteristic-definition.v1"
)


def lower_devoid_characteristic_fragment(
    material_line: str,
    mechanics: tuple[str, ...],
) -> AbilityKeywordFragmentLowering | None:
    """Lower the closed ordinary Devoid grammar to one copied fragment."""

    if mechanics != (DEVOID_MECHANIC_ID,):
        return None
    if material_line.strip().rstrip(".").casefold() != DEVOID_MECHANIC_ID:
        return AbilityKeywordFragmentLowering(
            residual_kind="unsupported_devoid_wording",
            residual_reason=(
                "Devoid requires one ordinary printed keyword instance"
            ),
            residual_blockers=("ordinary printed Devoid",),
        )
    return AbilityKeywordFragmentLowering(
        handlers=(
            {
                "handler_id": DEVOID_FRAGMENT_HANDLER_ID,
                "schema_version": 1,
                "event": "continuous",
                "fragment": ability_fragment_to_dict(
                    ColorlessCharacteristicDefinitionSpec()
                ),
            },
        )
    )


__all__ = [
    "DEVOID_FRAGMENT_HANDLER_ID",
    "DEVOID_MECHANIC_ID",
    "lower_devoid_characteristic_fragment",
]
