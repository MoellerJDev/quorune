from __future__ import annotations

"""Closed values for one resolution-created indefinite keyword grant."""


class ZoneObjectKeywordGrantError(ValueError):
    """A zone-object keyword descriptor is outside the represented family."""


# This is the exact reviewed indefinite-grant family, not the broader keyword-
# counter vocabulary. Each addition requires its own executable keyword
# capability and interaction evidence before compiler or runtime acceptance.
ZONE_OBJECT_KEYWORDS = frozenset(
    {
        "first strike",
        "flying",
        "trample",
        "vigilance",
    }
)


def normalized_zone_object_keyword(value: object) -> str:
    """Return one closed executable keyword or fail before mutation."""

    if type(value) is not str:
        raise ZoneObjectKeywordGrantError(
            "Zone-object keyword grants require one string keyword"
        )
    keyword = " ".join(value.casefold().split())
    if keyword not in ZONE_OBJECT_KEYWORDS:
        raise ZoneObjectKeywordGrantError(
            "Zone-object keyword grant is outside the represented vocabulary"
        )
    return keyword


__all__ = [
    "ZONE_OBJECT_KEYWORDS",
    "ZoneObjectKeywordGrantError",
    "normalized_zone_object_keyword",
]
