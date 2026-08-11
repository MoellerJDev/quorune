from __future__ import annotations

"""Closed CardProgram capability shape for ordinary fixed Amass."""

from typing import Any, Iterable, Mapping, Sequence

from ..amass import AmassError, FixedAmassSpec


def fixed_amass_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Return ownership for one exact fixed positive Amass action."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if (
        target_schema is not None
        or len(effects) != 1
        or not {
            "amass",
            "cr-111-tokens",
            "cr-122-counters",
        }.issubset(mechanics)
    ):
        return ()
    effect = effects[0]
    if set(effect) != {"op", "subtype", "amount"} or effect.get("op") != "amass":
        return ()
    try:
        FixedAmassSpec(
            subtype=effect.get("subtype"),
            amount=effect.get("amount"),
        )
    except AmassError:
        return ()
    return ("keyword_action.amass.fixed",)


__all__ = ["fixed_amass_node_capabilities"]
