from __future__ import annotations

"""Closed typed targets for one card in the acting player's graveyard."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence


class GraveyardCardTargetError(ValueError):
    """A graveyard-card target descriptor is outside the represented grammar."""


class GraveyardCardTargetKind(str, Enum):
    CARD = "card"
    ARTIFACT_CARD = "artifact card"
    CREATURE_CARD = "creature card"
    ENCHANTMENT_CARD = "enchantment card"
    INSTANT_CARD = "instant card"
    LAND_CARD = "land card"
    PERMANENT_CARD = "permanent card"
    SORCERY_CARD = "sorcery card"
    ARTIFACT_OR_ENCHANTMENT_CARD = "artifact or enchantment card"
    INSTANT_OR_SORCERY_CARD = "instant or sorcery card"
    NONLAND_PERMANENT_CARD = "nonland permanent card"

    @property
    def types_any(self) -> tuple[str, ...]:
        return {
            GraveyardCardTargetKind.CARD: (),
            GraveyardCardTargetKind.ARTIFACT_CARD: ("artifact",),
            GraveyardCardTargetKind.CREATURE_CARD: ("creature",),
            GraveyardCardTargetKind.ENCHANTMENT_CARD: ("enchantment",),
            GraveyardCardTargetKind.INSTANT_CARD: ("instant",),
            GraveyardCardTargetKind.LAND_CARD: ("land",),
            GraveyardCardTargetKind.PERMANENT_CARD: (
                "artifact",
                "battle",
                "creature",
                "enchantment",
                "land",
                "planeswalker",
            ),
            GraveyardCardTargetKind.SORCERY_CARD: ("sorcery",),
            GraveyardCardTargetKind.ARTIFACT_OR_ENCHANTMENT_CARD: (
                "artifact",
                "enchantment",
            ),
            GraveyardCardTargetKind.INSTANT_OR_SORCERY_CARD: (
                "instant",
                "sorcery",
            ),
            GraveyardCardTargetKind.NONLAND_PERMANENT_CARD: (
                "artifact",
                "battle",
                "creature",
                "enchantment",
                "planeswalker",
            ),
        }[self]

    @property
    def types_none(self) -> tuple[str, ...]:
        if self is GraveyardCardTargetKind.NONLAND_PERMANENT_CARD:
            return ("land",)
        return ()


class PublicGraveyardCardTargetKind(str, Enum):
    """Closed type predicates for a card in any public graveyard."""

    CARD = "card"
    ARTIFACT_CARD = "artifact card"
    CREATURE_CARD = "creature card"
    INSTANT_CARD = "instant card"
    LAND_CARD = "land card"
    PERMANENT_CARD = "permanent card"
    SORCERY_CARD = "sorcery card"
    ARTIFACT_OR_ENCHANTMENT_CARD = "artifact or enchantment card"
    INSTANT_OR_SORCERY_CARD = "instant or sorcery card"
    NONCREATURE_CARD = "noncreature card"
    NONLAND_CARD = "nonland card"

    @property
    def types_any(self) -> tuple[str, ...]:
        return {
            PublicGraveyardCardTargetKind.CARD: (),
            PublicGraveyardCardTargetKind.ARTIFACT_CARD: ("artifact",),
            PublicGraveyardCardTargetKind.CREATURE_CARD: ("creature",),
            PublicGraveyardCardTargetKind.INSTANT_CARD: ("instant",),
            PublicGraveyardCardTargetKind.LAND_CARD: ("land",),
            PublicGraveyardCardTargetKind.PERMANENT_CARD: (
                "artifact",
                "battle",
                "creature",
                "enchantment",
                "land",
                "planeswalker",
            ),
            PublicGraveyardCardTargetKind.SORCERY_CARD: ("sorcery",),
            PublicGraveyardCardTargetKind.ARTIFACT_OR_ENCHANTMENT_CARD: (
                "artifact",
                "enchantment",
            ),
            PublicGraveyardCardTargetKind.INSTANT_OR_SORCERY_CARD: (
                "instant",
                "sorcery",
            ),
            PublicGraveyardCardTargetKind.NONCREATURE_CARD: (),
            PublicGraveyardCardTargetKind.NONLAND_CARD: (),
        }[self]

    @property
    def types_none(self) -> tuple[str, ...]:
        return {
            PublicGraveyardCardTargetKind.NONCREATURE_CARD: ("creature",),
            PublicGraveyardCardTargetKind.NONLAND_CARD: ("land",),
        }.get(self, ())


@dataclass(frozen=True, slots=True)
class PublicGraveyardCardTargetSpec:
    """One immutable target predicate for a card in any graveyard."""

    kind: PublicGraveyardCardTargetKind

    def __post_init__(self) -> None:
        if not isinstance(self.kind, PublicGraveyardCardTargetKind):
            raise GraveyardCardTargetError(
                "Public graveyard target kind must be a supported typed value"
            )

    @property
    def slug(self) -> str:
        return self.kind.value.replace(" or ", "-or-").replace(" ", "-")

    def to_target_schema(self) -> dict[str, Any]:
        schema: dict[str, Any] = {
            "zones": ["graveyard"],
            "categories": ["card"],
            "owner_relation": "any",
            "count": 1,
        }
        if self.kind.types_any:
            schema["types_any"] = list(self.kind.types_any)
        if self.kind.types_none:
            schema["types_none"] = list(self.kind.types_none)
        return schema

    @classmethod
    def from_target_schema(
        cls,
        value: Mapping[str, Any],
    ) -> "PublicGraveyardCardTargetSpec":
        if not isinstance(value, Mapping):
            raise GraveyardCardTargetError(
                "Public graveyard target schema must be an object"
            )
        schema = dict(value)
        allowed = {
            "zones",
            "categories",
            "owner_relation",
            "count",
            "types_any",
            "types_none",
        }
        if set(schema) - allowed:
            raise GraveyardCardTargetError(
                "Public graveyard target schema has unknown fields"
            )
        if (
            schema.get("zones") != ["graveyard"]
            or schema.get("categories") != ["card"]
            or schema.get("owner_relation") != "any"
            or type(schema.get("count")) is not int
            or schema.get("count") != 1
        ):
            raise GraveyardCardTargetError(
                "Public graveyard target schema header is unsupported"
            )
        types_any = _canonical_types(
            schema.get("types_any", ()), field="types_any"
        )
        types_none = _canonical_types(
            schema.get("types_none", ()), field="types_none"
        )
        matches = tuple(
            kind
            for kind in PublicGraveyardCardTargetKind
            if kind.types_any == types_any and kind.types_none == types_none
        )
        if len(matches) != 1:
            raise GraveyardCardTargetError(
                "Public graveyard target type predicate is unsupported"
            )
        spec = cls(matches[0])
        if spec.to_target_schema() != schema:
            raise GraveyardCardTargetError(
                "Public graveyard target schema is not canonical"
            )
        return spec


def _canonical_types(values: Sequence[str], *, field: str) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)):
        raise GraveyardCardTargetError(f"Graveyard target {field} must be an array")
    if any(type(value) is not str or not value for value in values):
        raise GraveyardCardTargetError(
            f"Graveyard target {field} values must be nonempty strings"
        )
    normalized = tuple(sorted(value.casefold() for value in values))
    if len(normalized) != len(set(normalized)):
        raise GraveyardCardTargetError(
            f"Graveyard target {field} values must be unique"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class OwnGraveyardCardTargetSpec:
    """One immutable target predicate for a card in the actor's graveyard."""

    kind: GraveyardCardTargetKind

    def __post_init__(self) -> None:
        if not isinstance(self.kind, GraveyardCardTargetKind):
            raise GraveyardCardTargetError(
                "Graveyard target kind must be a supported typed value"
            )

    @property
    def slug(self) -> str:
        return self.kind.value.replace(" or ", "-or-").replace(" ", "-")

    def to_target_schema(self) -> dict[str, Any]:
        schema: dict[str, Any] = {
            "zones": ["graveyard"],
            "categories": ["card"],
            "owner_relation": "you",
            "count": 1,
        }
        if self.kind.types_any:
            schema["types_any"] = list(self.kind.types_any)
        if self.kind.types_none:
            schema["types_none"] = list(self.kind.types_none)
        return schema

    @classmethod
    def from_target_schema(
        cls,
        value: Mapping[str, Any],
    ) -> "OwnGraveyardCardTargetSpec":
        if not isinstance(value, Mapping):
            raise GraveyardCardTargetError(
                "Graveyard target schema must be an object"
            )
        schema = dict(value)
        allowed = {
            "zones",
            "categories",
            "owner_relation",
            "count",
            "types_any",
            "types_none",
        }
        if set(schema) - allowed:
            raise GraveyardCardTargetError(
                "Graveyard target schema has unknown fields"
            )
        if (
            schema.get("zones") != ["graveyard"]
            or schema.get("categories") != ["card"]
            or schema.get("owner_relation") != "you"
            or type(schema.get("count")) is not int
            or schema.get("count") != 1
        ):
            raise GraveyardCardTargetError(
                "Graveyard target schema header is unsupported"
            )
        types_any = _canonical_types(schema.get("types_any", ()), field="types_any")
        types_none = _canonical_types(
            schema.get("types_none", ()), field="types_none"
        )
        matches = tuple(
            kind
            for kind in GraveyardCardTargetKind
            if kind.types_any == types_any and kind.types_none == types_none
        )
        if len(matches) != 1:
            raise GraveyardCardTargetError(
                "Graveyard target type predicate is unsupported"
            )
        spec = cls(matches[0])
        if spec.to_target_schema() != schema:
            raise GraveyardCardTargetError(
                "Graveyard target schema is not canonical"
            )
        return spec


def targeted_own_graveyard_return_node_capabilities(
    *,
    effects: Sequence[Mapping[str, Any]],
    target_schema: Mapping[str, Any] | None,
    mechanic_ids: Iterable[str],
) -> tuple[str, ...]:
    """Return capabilities only for the closed own-graveyard card grammar."""

    mechanics = {str(value).casefold() for value in mechanic_ids}
    if (
        not {"return-to-owner-hand", "cr-115-targets"}.issubset(mechanics)
        or len(effects) != 1
        or not isinstance(target_schema, Mapping)
    ):
        return ()
    try:
        OwnGraveyardCardTargetSpec.from_target_schema(target_schema)
    except (GraveyardCardTargetError, TypeError):
        return ()
    effect = effects[0]
    if (
        set(effect) != {"op", "card"}
        or effect.get("op") != "return_graveyard_card_to_owner_hand"
        or effect.get("card") != "$target.0"
    ):
        return ()
    return (
        "card.return.own_graveyard_to_owner_hand",
        "target.revalidate_resolution",
    )


__all__ = [
    "GraveyardCardTargetError",
    "GraveyardCardTargetKind",
    "OwnGraveyardCardTargetSpec",
    "PublicGraveyardCardTargetKind",
    "PublicGraveyardCardTargetSpec",
    "targeted_own_graveyard_return_node_capabilities",
]
