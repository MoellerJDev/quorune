from __future__ import annotations

"""Closed target-threaded sequences of fixed resolution effects."""

from dataclasses import dataclass
import re
from typing import Any, Mapping

from ..keyword_counters import keyword_counter_mechanic
from .counter_placement_templates import (
    existing_target_counter_placement_effect_template,
    fixed_counter_placement_effect_template,
)


_TARGET_CREATURE = re.compile(
    r"(?P<subject>target creature"
    r"(?P<relation> you control| an opponent controls| you don't control)?|it) "
    r"(?P<body>.+?) until end of turn\.?",
    re.IGNORECASE,
)
_GETS = re.compile(
    r"gets (?P<power>[+-]\d+)/(?P<toughness>[+-]\d+)"
    r"(?: and gains (?P<keywords>.+))?",
    re.IGNORECASE,
)
_GAINS = re.compile(r"gains (?P<keywords>.+)", re.IGNORECASE)
_KEYWORDS = frozenset(
    {
        "deathtouch",
        "double strike",
        "first strike",
        "flying",
        "haste",
        "hexproof",
        "indestructible",
        "lifelink",
        "menace",
        "reach",
        "trample",
        "vigilance",
    }
)
_SEQUENCE_MECHANIC = "fixed-target-effect-sequence"


def _keyword_list(text: str) -> tuple[str, ...] | None:
    values = tuple(
        value.strip().casefold()
        for value in re.split(r"\s+and\s+", text)
        if value.strip()
    )
    if (
        not values
        or len(values) > 2
        or len(set(values)) != len(values)
        or any(value not in _KEYWORDS for value in values)
    ):
        return None
    return tuple(value.title() for value in values)


@dataclass(frozen=True, slots=True)
class FixedTargetCharacteristicsTemplate:
    power: int | None
    toughness: int | None
    keywords: tuple[str, ...]
    controller_relation: str | None

    def __post_init__(self) -> None:
        if (self.power is None) is not (self.toughness is None):
            raise ValueError("Power and toughness changes must be paired")
        if self.power == 0 and self.toughness == 0:
            raise ValueError("Characteristic change cannot be empty")
        if self.power is None and not self.keywords:
            raise ValueError("Characteristic change cannot be empty")
        if self.controller_relation not in {None, "any", "you", "opponent"}:
            raise ValueError("Target controller relation is unsupported")
        if len(set(self.keywords)) != len(self.keywords) or any(
            value.casefold() not in _KEYWORDS for value in self.keywords
        ):
            raise ValueError("Granted keyword set is unsupported")

    @property
    def effects(self) -> tuple[Mapping[str, Any], ...]:
        effects: list[Mapping[str, Any]] = []
        if self.power is not None and self.toughness is not None:
            effects.append(
                {
                    "op": "modify_stats_until_end_of_turn",
                    "card": "$target.0",
                    "power": self.power,
                    "toughness": self.toughness,
                }
            )
        effects.extend(
            {
                "op": "grant_keyword_until_end_of_turn",
                "card": "$target.0",
                "keyword": keyword,
            }
            for keyword in self.keywords
        )
        return tuple(effects)

    @property
    def target_schema(self) -> Mapping[str, Any] | None:
        if self.controller_relation is None:
            return None
        schema: dict[str, Any] = {
            "zones": ["battlefield"],
            "categories": ["permanent"],
            "types_any": ["creature"],
            "count": 1,
        }
        if self.controller_relation != "any":
            schema["controller_relation"] = self.controller_relation
        return schema

    def compiled(
        self,
    ) -> tuple[
        str,
        tuple[Mapping[str, Any], ...],
        Mapping[str, Any] | None,
        tuple[str, ...],
    ]:
        keyword_mechanics = tuple(
            mechanic
            for keyword in self.keywords
            if (mechanic := keyword_counter_mechanic(keyword)) is not None
        )
        return (
            "fixed-target-characteristics-until-end-of-turn-v1",
            self.effects,
            self.target_schema,
            (
                ("cr-611-continuous-effects", *keyword_mechanics)
                if self.controller_relation is None
                else (
                    "cr-611-continuous-effects",
                    "cr-115-targets",
                    *keyword_mechanics,
                )
            ),
        )


def fixed_target_characteristics_effect_template(
    text: str,
    *,
    existing_target: bool = False,
) -> FixedTargetCharacteristicsTemplate | None:
    """Parse one fixed target or target-pronoun characteristic instruction."""

    match = _TARGET_CREATURE.fullmatch(text.strip())
    if match is None:
        return None
    subject = match.group("subject").casefold()
    if (subject == "it") is not existing_target:
        return None
    relation = (match.group("relation") or "").casefold()
    controller_relation = (
        None
        if existing_target
        else "you"
        if relation == " you control"
        else "opponent"
        if relation
        else "any"
    )
    body = match.group("body")
    gets = _GETS.fullmatch(body)
    gains = _GAINS.fullmatch(body)
    if gets is not None:
        keywords = (
            _keyword_list(gets.group("keywords"))
            if gets.group("keywords")
            else ()
        )
        if keywords is None:
            return None
        return FixedTargetCharacteristicsTemplate(
            power=int(gets.group("power")),
            toughness=int(gets.group("toughness")),
            keywords=keywords,
            controller_relation=controller_relation,
        )
    if gains is None:
        return None
    keywords = _keyword_list(gains.group("keywords"))
    if keywords is None:
        return None
    return FixedTargetCharacteristicsTemplate(
        power=None,
        toughness=None,
        keywords=keywords,
        controller_relation=controller_relation,
    )


def _sentences(text: str) -> tuple[str, ...]:
    normalized = " ".join(text.strip().split())
    if any(value in normalized for value in ('"', "(", ")")):
        return ()
    clauses = tuple(
        value.strip() + "."
        for value in re.split(r"\.\s+", normalized.rstrip("."))
        if value.strip()
    )
    return clauses if 2 <= len(clauses) <= 3 else ()


def _fixed_creature_target_schema(value: Mapping[str, Any] | None) -> bool:
    if value is None:
        return False
    schema = dict(value)
    relation = schema.pop("controller_relation", "any")
    return relation in {"any", "you", "opponent"} and schema == {
        "zones": ["battlefield"],
        "categories": ["permanent"],
        "types_any": ["creature"],
        "count": 1,
    }


@dataclass(frozen=True, slots=True)
class FixedTargetEffectSequenceTemplate:
    effects: tuple[Mapping[str, Any], ...]
    target_schema: Mapping[str, Any]
    mechanic_ids: tuple[str, ...]

    def compiled(
        self,
    ) -> tuple[
        str,
        tuple[Mapping[str, Any], ...],
        Mapping[str, Any],
        tuple[str, ...],
    ]:
        return (
            "fixed-target-counter-characteristics-sequence-v1",
            self.effects,
            self.target_schema,
            self.mechanic_ids,
        )


def fixed_target_effect_sequence_template(
    text: str,
    *,
    card_name: str,
) -> FixedTargetEffectSequenceTemplate | None:
    """Lower two or three mandatory instructions sharing target index zero."""

    clauses = _sentences(text)
    if not clauses:
        return None
    effects: list[Mapping[str, Any]] = []
    mechanic_ids: list[str] = [
        _SEQUENCE_MECHANIC,
        "cr-115-targets",
        "cr-122-counters",
        "cr-611-continuous-effects",
    ]
    target_schema: Mapping[str, Any] | None = None
    for clause in clauses:
        compiled = fixed_target_characteristics_effect_template(
            clause,
            existing_target=target_schema is not None,
        )
        if compiled is None and target_schema is None:
            compiled = fixed_counter_placement_effect_template(
                clause,
                card_name=card_name,
            )
        if compiled is None and target_schema is not None:
            compiled = existing_target_counter_placement_effect_template(clause)
        if compiled is None:
            return None
        _template_id, clause_effects, clause_schema, mechanics = compiled.compiled()
        if clause_schema is not None:
            if target_schema is not None or not _fixed_creature_target_schema(
                clause_schema
            ):
                return None
            target_schema = clause_schema
        effects.extend(clause_effects)
        mechanic_ids.extend(mechanics)
    operations = {str(effect.get("op") or "") for effect in effects}
    if target_schema is None or not {
        "place_counters",
    }.issubset(operations) or not operations.intersection(
        {"modify_stats_until_end_of_turn", "grant_keyword_until_end_of_turn"}
    ):
        return None
    return FixedTargetEffectSequenceTemplate(
        effects=tuple(effects),
        target_schema=target_schema,
        mechanic_ids=tuple(dict.fromkeys(mechanic_ids)),
    )


__all__ = [
    "FixedTargetCharacteristicsTemplate",
    "FixedTargetEffectSequenceTemplate",
    "fixed_target_characteristics_effect_template",
    "fixed_target_effect_sequence_template",
]
