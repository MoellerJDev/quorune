from __future__ import annotations

"""Typed structural helpers for independently owned direct-target grammars."""

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence

from .creature_subtypes import canonical_creature_subtype


CompiledDirectTarget = tuple[
    str,
    tuple[Mapping[str, Any], ...],
    Mapping[str, Any],
    tuple[str, ...],
]


_DIRECT_TYPE_ANY_SHAPES = frozenset(
    {
        ("artifact",),
        ("battle",),
        ("creature",),
        ("enchantment",),
        ("land",),
        ("planeswalker",),
        ("artifact", "creature"),
    }
)
_DIRECT_TYPE_ALL_SHAPES = frozenset(
    {("creature",), ("creature", "enchantment")}
)
DIRECT_NONCREATURE_SUBTYPES = frozenset({"vehicle"})
DIRECT_PERMANENT_TYPES = frozenset(
    {
        "artifact",
        "battle",
        "creature",
        "enchantment",
        "land",
        "permanent",
        "planeswalker",
    }
)
_DIRECT_KEYWORDS = frozenset({"flying"})


def _canonical_terms(
    values: Sequence[str],
    *,
    field: str,
) -> tuple[str, ...]:
    normalized = tuple(
        sorted(value.casefold() for value in _closed_values(values, field=field))
    )
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"Direct-target {field} values must be unique")
    return normalized


@dataclass(frozen=True, slots=True)
class DirectPermanentTargetSpec:
    """One closed, immutable direct-permanent target predicate.

    This is a compiler-owned semantic value.  Runtime target schemas are a
    deterministic serialization of it rather than a second Oracle-text
    interpretation.
    """

    types_any: tuple[str, ...] = ()
    types_all: tuple[str, ...] = ()
    subtypes_any: tuple[str, ...] = ()
    keywords_all: tuple[str, ...] = ()
    controller_relation: str = "any"
    source_exclusion: bool = False
    commander: bool | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "types_any",
            "types_all",
            "subtypes_any",
            "keywords_all",
        ):
            object.__setattr__(
                self,
                field_name,
                _canonical_terms(getattr(self, field_name), field=field_name),
            )
        if self.types_any and self.types_all:
            raise ValueError(
                "Direct permanent targets cannot mix any/all type predicates"
            )
        if self.types_any not in _DIRECT_TYPE_ANY_SHAPES and self.types_any:
            raise ValueError("Direct permanent target type disjunction is unsupported")
        if self.types_all not in _DIRECT_TYPE_ALL_SHAPES and self.types_all:
            raise ValueError("Direct permanent target type conjunction is unsupported")
        if self.types_all == ("creature",) and not self.keywords_all:
            raise ValueError(
                "Direct permanent creature conjunction requires a keyword predicate"
            )
        if self.subtypes_any:
            if self.types_any or self.types_all or len(self.subtypes_any) > 8:
                raise ValueError(
                    "Direct permanent subtype targets require one closed disjunction"
                )
            for subtype in self.subtypes_any:
                if (
                    canonical_creature_subtype(subtype) != subtype
                    and subtype not in DIRECT_NONCREATURE_SUBTYPES
                ):
                    raise ValueError(
                        f"Direct permanent target subtype {subtype!r} is unsupported"
                    )
        if self.keywords_all:
            if (
                self.types_all != ("creature",)
                or self.types_any
                or self.subtypes_any
                or not set(self.keywords_all).issubset(_DIRECT_KEYWORDS)
            ):
                raise ValueError(
                    "Direct permanent keyword targets require a closed creature predicate"
                )
        if self.controller_relation not in {"any", "you", "opponent"}:
            raise ValueError("Direct permanent target controller relation is unsupported")
        if type(self.source_exclusion) is not bool:
            raise ValueError("Direct permanent target source exclusion must be boolean")
        if self.commander is not None and (
            self.commander is not True or self.types_any != ("creature",)
        ):
            raise ValueError(
                "Direct permanent commander targets require a creature predicate"
            )

    @property
    def characteristic_slug(self) -> str:
        """Return the canonical characteristic-only predicate identity."""

        if self.types_any:
            predicate = "-or-".join(self.types_any)
        elif self.types_all:
            predicate = "-".join(self.types_all)
        elif self.subtypes_any:
            predicate = "-or-".join(self.subtypes_any)
        else:
            predicate = "permanent"
        if self.keywords_all:
            predicate += "-with-" + "-and-".join(self.keywords_all)
        if self.commander:
            predicate = f"commander-{predicate}"
        return predicate

    @property
    def slug(self) -> str:
        predicate = self.characteristic_slug
        if self.controller_relation != "any":
            predicate += f"-{self.controller_relation}"
        if self.source_exclusion:
            predicate += "-another"
        return predicate

    @property
    def uses_compound_characteristics(self) -> bool:
        """Whether this spec exceeds the historical single type/subtype grammar."""

        return bool(
            self.types_all
            or self.keywords_all
            or len(self.types_any) > 1
            or len(self.subtypes_any) > 1
        )

    def to_target_schema(self) -> dict[str, Any]:
        schema: dict[str, Any] = {
            "zones": ["battlefield"],
            "categories": ["permanent"],
            "count": 1,
        }
        for field_name in (
            "types_any",
            "types_all",
            "subtypes_any",
            "keywords_all",
        ):
            values = getattr(self, field_name)
            if values:
                schema[field_name] = list(values)
        if self.controller_relation != "any":
            schema["controller_relation"] = self.controller_relation
        if self.source_exclusion:
            schema["source_exclusion"] = True
        if self.commander is not None:
            schema["commander"] = self.commander
        return schema

    @classmethod
    def from_target_schema(
        cls,
        value: Mapping[str, Any],
        *,
        allow_commander: bool = False,
    ) -> "DirectPermanentTargetSpec":
        if not isinstance(value, Mapping):
            raise ValueError("Direct permanent target schema must be an object")
        schema = dict(value)
        allowed = {
            "zones",
            "categories",
            "count",
            "types_any",
            "types_all",
            "subtypes_any",
            "keywords_all",
            "controller_relation",
            "source_exclusion",
            *(('commander',) if allow_commander else ()),
        }
        if set(schema) - allowed:
            raise ValueError("Direct permanent target schema has unknown fields")
        if (
            schema.get("zones") != ["battlefield"]
            or schema.get("categories") != ["permanent"]
            or type(schema.get("count")) is not int
            or schema.get("count") != 1
        ):
            raise ValueError("Direct permanent target schema header is unsupported")
        source_exclusion = schema.get("source_exclusion", False)
        if type(source_exclusion) is not bool:
            raise ValueError("Direct permanent target source exclusion must be boolean")
        spec = cls(
            types_any=tuple(schema.get("types_any", ())),
            types_all=tuple(schema.get("types_all", ())),
            subtypes_any=tuple(schema.get("subtypes_any", ())),
            keywords_all=tuple(schema.get("keywords_all", ())),
            controller_relation=schema.get("controller_relation", "any"),
            source_exclusion=source_exclusion,
            commander=schema.get("commander"),
        )
        if spec.to_target_schema() != schema:
            raise ValueError("Direct permanent target schema is not canonical")
        return spec


def direct_permanent_target_spec(
    subject: str,
) -> DirectPermanentTargetSpec | None:
    """Parse one closed direct-permanent target predicate.

    Effect-family compilers share this grammar so counter placement, counter
    removal, and other direct-target clauses cannot disagree about the same
    Oracle subject.
    """

    if type(subject) is not str:
        return None
    phrase = " ".join(subject.casefold().split())
    exclude_source = phrase.startswith("another target ")
    if exclude_source:
        phrase = phrase[len("another target ") :]
    elif phrase.startswith("target "):
        phrase = phrase[len("target ") :]
    else:
        return None

    relation = "any"
    for suffix, candidate in (
        (" an opponent controls", "opponent"),
        (" you don't control", "opponent"),
        (" you control", "you"),
    ):
        if phrase.endswith(suffix):
            phrase = phrase[: -len(suffix)]
            relation = candidate
            break

    kwargs: dict[str, Any] = {
        "controller_relation": relation,
        "source_exclusion": exclude_source,
    }
    if phrase == "artifact or creature":
        kwargs["types_any"] = ("artifact", "creature")
    elif phrase == "enchantment creature":
        kwargs["types_all"] = ("enchantment", "creature")
    elif phrase == "creature with flying":
        kwargs["types_all"] = ("creature",)
        kwargs["keywords_all"] = ("flying",)
    elif phrase in DIRECT_PERMANENT_TYPES:
        if phrase != "permanent":
            kwargs["types_any"] = (phrase,)
    else:
        if phrase.endswith(" creature"):
            phrase = phrase[: -len(" creature")]
        raw_subtypes = tuple(
            value.strip()
            for value in re.split(r",\s*(?:or\s+)?|\s+or\s+", phrase)
            if value.strip()
        )
        if not raw_subtypes:
            return None
        subtypes: list[str] = []
        for value in raw_subtypes:
            subtype = canonical_creature_subtype(value)
            if subtype is None and value not in DIRECT_NONCREATURE_SUBTYPES:
                return None
            subtypes.append(subtype or value)
        kwargs["subtypes_any"] = tuple(subtypes)
    try:
        return DirectPermanentTargetSpec(**kwargs)
    except ValueError:
        return None


def _closed_values(
    values: Sequence[str],
    *,
    field: str,
    required: bool = False,
) -> list[str]:
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"Direct-target {field} must be an array")
    normalized = list(values)
    if required and not normalized:
        raise ValueError(f"Direct-target {field} must not be empty")
    if any(type(value) is not str or not value for value in normalized):
        raise ValueError(
            f"Direct-target {field} values must be nonempty strings"
        )
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"Direct-target {field} values must be unique")
    return normalized


def direct_target_slug(value: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError("Direct-target slugs require a nonempty value")
    return (
        value.casefold().replace(",", "").replace(" or ", "-or-").replace(" ", "-")
    )


def direct_target_effect(
    operation: str,
    *,
    reference_field: str,
) -> tuple[Mapping[str, Any], ...]:
    if type(operation) is not str or not operation:
        raise ValueError("Direct-target operations must be nonempty")
    if type(reference_field) is not str or not reference_field:
        raise ValueError("Direct-target reference fields must be nonempty")
    return ({"op": operation, reference_field: "$target.0"},)


def permanent_target_schema(
    *,
    types_any: Sequence[str] = (),
    types_none: Sequence[str] = (),
) -> Mapping[str, Any]:
    any_values = _closed_values(types_any, field="types_any")
    none_values = _closed_values(types_none, field="types_none")
    if types_any and types_none:
        raise ValueError("Direct permanent targets require one type predicate")
    schema: dict[str, Any] = {
        "zones": ["battlefield"],
        "categories": ["permanent"],
        "count": 1,
    }
    if any_values:
        schema["types_any"] = any_values
    if none_values:
        schema["types_none"] = none_values
    return schema


def stack_target_schema(
    *,
    categories: Sequence[str],
    types_any: Sequence[str] = (),
    types_none: Sequence[str] = (),
    colors_any: Sequence[str] = (),
    predicate: str | None = None,
    colorless: bool | None = None,
) -> Mapping[str, Any]:
    category_values = _closed_values(
        categories,
        field="categories",
        required=True,
    )
    any_values = _closed_values(types_any, field="types_any")
    none_values = _closed_values(types_none, field="types_none")
    color_values = _closed_values(colors_any, field="colors_any")
    predicates = sum(
        bool(value)
        for value in (
            any_values,
            none_values,
            color_values,
            predicate,
            colorless,
        )
    )
    if predicates > 1:
        raise ValueError("Direct stack targets require one optional predicate")
    schema: dict[str, Any] = {
        "zones": ["stack"],
        "categories": category_values,
        "source_exclusion": True,
        "count": 1,
    }
    if any_values:
        schema["types_any"] = any_values
    elif none_values:
        schema["types_none"] = none_values
    elif color_values:
        schema["colors_any"] = color_values
    elif predicate is not None:
        if type(predicate) is not str or not predicate:
            raise ValueError("Direct stack predicates must be nonempty")
        schema["predicate"] = predicate
    elif colorless is not None:
        if type(colorless) is not bool:
            raise ValueError("Direct stack colorless predicates must be boolean")
        schema["colorless"] = colorless
    return schema


def compiled_direct_target(
    *,
    template_id: str,
    effects: tuple[Mapping[str, Any], ...],
    target_schema: Mapping[str, Any],
    mechanics: tuple[str, ...],
) -> CompiledDirectTarget:
    if type(template_id) is not str or not template_id:
        raise ValueError("Direct-target templates require an identity")
    if len(effects) != 1 or not isinstance(effects[0], Mapping):
        raise ValueError("Direct-target templates require one effect")
    if not isinstance(target_schema, Mapping):
        raise ValueError("Direct-target templates require a target schema")
    mechanic_values = _closed_values(
        mechanics,
        field="mechanics",
        required=True,
    )
    return template_id, effects, target_schema, tuple(mechanic_values)


__all__ = [
    "CompiledDirectTarget",
    "DIRECT_NONCREATURE_SUBTYPES",
    "DIRECT_PERMANENT_TYPES",
    "DirectPermanentTargetSpec",
    "compiled_direct_target",
    "direct_permanent_target_spec",
    "direct_target_effect",
    "direct_target_slug",
    "permanent_target_schema",
    "stack_target_schema",
]
