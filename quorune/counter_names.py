from __future__ import annotations

"""Low-level canonical counter-name values without state-model dependencies."""


class CounterStateError(ValueError):
    """A typed counter change cannot be planned or committed exactly."""


def normalized_counter_name(value: str) -> str:
    result = " ".join(str(value).casefold().split())
    if not result:
        raise CounterStateError("Counter changes require a counter name")
    return result


__all__ = ["CounterStateError", "normalized_counter_name"]
