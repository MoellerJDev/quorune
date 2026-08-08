from __future__ import annotations

from dataclasses import dataclass


EVOLVE_EVENT_CONDITION_FIELD = "evolve_entered_creature_is_larger"


class EvolveError(ValueError):
    """A typed Evolve characteristic snapshot is malformed."""


@dataclass(frozen=True, slots=True)
class EvolveCharacteristics:
    """The current characteristics CR 702.100 compares at one check."""

    is_creature: bool
    power: int
    toughness: int

    def __post_init__(self) -> None:
        if type(self.is_creature) is not bool:
            raise EvolveError("Evolve creature status must be a boolean")
        for field in ("power", "toughness"):
            if type(getattr(self, field)) is not int:
                raise EvolveError(
                    f"Evolve {field} must be an exact integer"
                )


def evolve_condition_holds(
    source: EvolveCharacteristics,
    entered: EvolveCharacteristics,
) -> bool:
    """Return the intervening-if result for one Evolve instance."""

    if not isinstance(source, EvolveCharacteristics) or not isinstance(
        entered, EvolveCharacteristics
    ):
        raise EvolveError("Evolve comparisons require typed characteristics")
    if not source.is_creature or not entered.is_creature:
        return False
    return (
        entered.power > source.power
        or entered.toughness > source.toughness
    )


__all__ = [
    "EVOLVE_EVENT_CONDITION_FIELD",
    "EvolveCharacteristics",
    "EvolveError",
    "evolve_condition_holds",
]
