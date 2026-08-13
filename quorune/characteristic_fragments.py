from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class CharacteristicFragmentError(ValueError):
    """A typed dynamic-characteristic fragment is malformed."""


class CharacteristicCountKind(str, Enum):
    CONTROLLER_BATTLEFIELD_ARTIFACTS = (
        "controller_battlefield_artifacts"
    )
    OWNER_GRAVEYARD_CREATURE_CARDS = "owner_graveyard_creature_cards"
    OWNER_GRAVEYARD_LAND_CARDS = "owner_graveyard_land_cards"


class PowerToughnessCalculation(str, Enum):
    PER_MATCHING_OBJECT = "per_matching_object"
    FIXED_IF_THRESHOLD = "fixed_if_threshold"


@dataclass(frozen=True, slots=True)
class ConditionalKeywordSpec:
    """One closed keyword condition evaluated from public match state."""

    keyword: str
    opponent_life_at_most: int
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise CharacteristicFragmentError(
                "Unsupported conditional-keyword schema version"
            )
        if self.keyword != "Haste":
            raise CharacteristicFragmentError(
                "Conditional-keyword fragments currently support Haste"
            )
        if (
            type(self.opponent_life_at_most) is not int
            or self.opponent_life_at_most < 0
        ):
            raise CharacteristicFragmentError(
                "Conditional-keyword life thresholds must be nonnegative integers"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "keyword": self.keyword,
            "opponent_life_at_most": self.opponent_life_at_most,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ConditionalKeywordSpec":
        expected = {
            "schema_version",
            "keyword",
            "opponent_life_at_most",
        }
        if not isinstance(value, Mapping) or set(value) != expected:
            raise CharacteristicFragmentError(
                "Conditional-keyword fragments have a closed schema"
            )
        return cls(**dict(value))


@dataclass(frozen=True, slots=True)
class DynamicPowerToughnessSpec:
    """One closed count-derived layer-7 characteristic modifier."""

    count_kind: CharacteristicCountKind
    calculation: PowerToughnessCalculation
    power: int
    toughness: int
    minimum_count: int = 0
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise CharacteristicFragmentError(
                "Unsupported dynamic power/toughness schema version"
            )
        if not isinstance(self.count_kind, CharacteristicCountKind):
            raise CharacteristicFragmentError(
                "Unsupported dynamic characteristic count kind"
            )
        if not isinstance(self.calculation, PowerToughnessCalculation):
            raise CharacteristicFragmentError(
                "Unsupported dynamic power/toughness calculation"
            )
        if type(self.power) is not int or type(self.toughness) is not int:
            raise CharacteristicFragmentError(
                "Dynamic power/toughness modifiers must be integers"
            )
        if self.power == 0 and self.toughness == 0:
            raise CharacteristicFragmentError(
                "Dynamic power/toughness must modify at least one value"
            )
        if type(self.minimum_count) is not int or self.minimum_count < 0:
            raise CharacteristicFragmentError(
                "Dynamic power/toughness minimum_count must be nonnegative"
            )
        if (
            self.calculation is PowerToughnessCalculation.PER_MATCHING_OBJECT
            and self.minimum_count != 0
        ):
            raise CharacteristicFragmentError(
                "Per-object modifiers do not carry a threshold"
            )
        if (
            self.calculation is PowerToughnessCalculation.FIXED_IF_THRESHOLD
            and self.minimum_count <= 0
        ):
            raise CharacteristicFragmentError(
                "Threshold modifiers require a positive minimum_count"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "count_kind": self.count_kind.value,
            "calculation": self.calculation.value,
            "power": self.power,
            "toughness": self.toughness,
            "minimum_count": self.minimum_count,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "DynamicPowerToughnessSpec":
        expected = {
            "schema_version",
            "count_kind",
            "calculation",
            "power",
            "toughness",
            "minimum_count",
        }
        if not isinstance(value, Mapping) or set(value) != expected:
            raise CharacteristicFragmentError(
                "Dynamic power/toughness fragments have a closed schema"
            )
        try:
            count_kind = CharacteristicCountKind(value["count_kind"])
            calculation = PowerToughnessCalculation(value["calculation"])
        except (TypeError, ValueError) as exc:
            raise CharacteristicFragmentError(
                "Unsupported dynamic power/toughness vocabulary"
            ) from exc
        return cls(
            schema_version=value["schema_version"],
            count_kind=count_kind,
            calculation=calculation,
            power=value["power"],
            toughness=value["toughness"],
            minimum_count=value["minimum_count"],
        )


__all__ = [
    "CharacteristicCountKind",
    "CharacteristicFragmentError",
    "ConditionalKeywordSpec",
    "DynamicPowerToughnessSpec",
    "PowerToughnessCalculation",
]
