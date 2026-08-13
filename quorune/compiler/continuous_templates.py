from __future__ import annotations

import re
from typing import Any, Mapping

from ..object_predicate import ObjectQuerySpec
from ..ability_fragments import (
    ConditionalKeywordSpec,
    DynamicPowerToughnessSpec,
    ToxicSpec,
    ability_fragment_to_dict,
    parse_protection_line,
)
from ..characteristic_fragments import (
    CharacteristicCountKind,
    PowerToughnessCalculation,
)
from .creature_subtypes import canonical_creature_subtype
from ..rules.source_references import SourceReferenceSpec


_BASIC_LAND_TYPE_ADDITION = re.compile(
    r"^Each land is (?:a|an) "
    r"(?P<subtype>Plains|Island|Swamp|Mountain|Forest) "
    r"in addition to its other land types\.?$",
    re.IGNORECASE,
)
_CONTROLLED_CREATURE_MODIFIER = re.compile(
    r"^(?P<other>Other )?"
    r"(?:(?P<qualifier>[Aa]rtifact|[Ww]hite|[Bb]lue|[Bb]lack|"
    r"[Rr]ed|[Gg]reen|[Ll]egendary|"
    r"[A-Z][A-Za-z'-]*(?: [A-Z][A-Za-z'-]*)?) )?"
    r"[Cc]reatures you control get (?P<power>[+-]\d+)/(?P<toughness>[+-]\d+)"
    r"(?P<until> until end of turn)?\.?$"
)
_CONTROLLED_SUBTYPE_PLURAL_MODIFIER = re.compile(
    r"^(?P<other>Other )?(?P<plural>[A-Z][A-Za-z'-]*) you control get "
    r"(?P<power>[+-]\d+)/(?P<toughness>[+-]\d+)"
    r"(?P<until> until end of turn)?\.?$"
)

_IRREGULAR_CREATURE_PLURALS = dict(
    value.split(":", 1)
    for value in (
        "aetherborn:aetherborn|allies:ally|dwarves:dwarf|elves:elf|"
        "faeries:faerie|heroes:hero|kithkin:kithkin|merfolk:merfolk|"
        "mice:mouse|myr:myr|phyrexians:phyrexian|treefolk:treefolk|"
        "wolves:wolf"
    ).split("|")
)
_STATEFUL_CREATURE_QUALIFIER = re.compile(
    r"^(?:attacking|blocking|enchanted|equipped|tapped|untapped)$"
)
_ATTACHED_SUBJECT = r"(?:Enchanted creature|Equipped creature|Fortified land)"
_ATTACHED_FIXED_CHARACTERISTICS = re.compile(
    rf"^(?P<subject>{_ATTACHED_SUBJECT}) (?P<body>.+?)\.?$",
    re.IGNORECASE,
)
_ATTACHED_FIXED_PT = re.compile(
    r"^gets (?P<power>[+-]\d+)/(?P<toughness>[+-]\d+)"
    r"(?: and has (?P<abilities>.+))?$",
    re.IGNORECASE,
)
_ATTACHED_HAS_OR_LOSES = re.compile(
    r"^(?P<verb>has|loses) (?P<abilities>.+)$",
    re.IGNORECASE,
)
_ATTACHED_ADDED_TYPE = re.compile(
    r"^is (?:a|an) (?P<type>[A-Z][A-Za-z'-]*) "
    r"in addition to its other types$",
)
_ATTACHED_SUPPORTED_ABILITIES = frozenset(
    {
        "deathtouch",
        "defender",
        "double strike",
        "first strike",
        "flash",
        "flying",
        "haste",
        "hexproof",
        "indestructible",
        "infect",
        "lifelink",
        "menace",
        "reach",
        "shadow",
        "shroud",
        "trample",
        "vigilance",
        "wither",
    }
)
_CARD_TYPE_WORDS = frozenset(
    {
        "artifact",
        "battle",
        "creature",
        "enchantment",
        "land",
        "planeswalker",
    }
)
_CONTROLLED_KEYWORD_GRANT = re.compile(
    r"^(?P<subject>Artifacts|Creature tokens) you control have "
    r"(?P<keyword>hexproof|haste)\."
    r"(?: \([^()]*\))?$",
    re.IGNORECASE,
)


def _singular_creature_subtype(plural: str) -> str | None:
    value = plural.casefold()
    if value in _IRREGULAR_CREATURE_PLURALS:
        candidate = _IRREGULAR_CREATURE_PLURALS[value]
        return canonical_creature_subtype(candidate)
    if value.endswith("s") and not value.endswith("ss") and len(value) > 2:
        return canonical_creature_subtype(value[:-1])
    return None


def controlled_creature_fixed_modifier(
    oracle_line: str,
    *,
    until_end_of_turn: bool,
) -> tuple[ObjectQuerySpec, int, int, bool] | None:
    """Parse one closed fixed modifier over controlled creatures.

    Conditional, combat-state, token, equipped, enchanted, commander, and
    negative-color predicates remain residual rather than being approximated.
    """

    text = oracle_line.strip()
    match = _CONTROLLED_CREATURE_MODIFIER.fullmatch(text)
    subtype_plural = False
    if match is None:
        match = _CONTROLLED_SUBTYPE_PLURAL_MODIFIER.fullmatch(text)
        subtype_plural = match is not None
    if match is None or bool(match.group("until")) is not until_end_of_turn:
        return None
    qualifier = (
        _singular_creature_subtype(match.group("plural"))
        if subtype_plural
        else (match.group("qualifier") or "").casefold()
    )
    if subtype_plural and qualifier is None:
        return None
    fields: dict[str, Any] = {
        "zones": ("battlefield",),
        "types_all": ("creature",),
    }
    if qualifier == "artifact":
        fields["types_all"] = ("artifact", "creature")
    elif qualifier == "legendary":
        fields["supertypes_all"] = ("legendary",)
    elif qualifier in {"white", "blue", "black", "red", "green"}:
        fields["colors_all"] = (
            {
                "white": "W",
                "blue": "U",
                "black": "B",
                "red": "R",
                "green": "G",
            }[qualifier],
        )
    elif qualifier:
        # Capitalization is not semantic.  Only the pinned CR 205.3m
        # creature-type vocabulary may enter the subtype predicate.  The
        # grammar deliberately leaves state, token, snow, commander,
        # negative, compound, and other unsupported qualities residual.
        subtype = canonical_creature_subtype(qualifier)
        if subtype is None or _STATEFUL_CREATURE_QUALIFIER.fullmatch(
            qualifier
        ):
            return None
        fields["subtypes_all"] = (subtype,)
    return (
        ObjectQuerySpec(**fields),
        int(match.group("power")),
        int(match.group("toughness")),
        bool(match.group("other")),
    )


def fixed_power_toughness_anthem_handler(
    oracle_line: str,
) -> tuple[str, Mapping[str, Any], str] | None:
    parsed = controlled_creature_fixed_modifier(
        oracle_line, until_end_of_turn=False
    )
    if parsed is None:
        return None
    predicate, power, toughness, exclude_source = parsed
    return (
        "continuous-fixed-query-anthem-v2",
        {
            "handler_id": "continuous.anthem.fixed-query.v2",
            "schema_version": 2,
            "event": "characteristics.evaluate",
            "condition": {
                "target_controller": "source_controller",
                "predicate": predicate.to_dict(),
                "exclude_source": exclude_source,
            },
            "modifier": {"power": power, "toughness": toughness},
        },
        "continuous.power_toughness.fixed_anthem",
    )


def fixed_query_keyword_grant_handler(
    oracle_line: str,
) -> tuple[str, Mapping[str, Any], str] | None:
    """Lower two closed controller-wide keyword grants."""

    match = _CONTROLLED_KEYWORD_GRANT.fullmatch(oracle_line.strip())
    if match is None:
        return None
    subject = match.group("subject").casefold()
    keyword = match.group("keyword").title()
    if (subject, keyword) not in {
        ("artifacts", "Hexproof"),
        ("creature tokens", "Haste"),
    }:
        return None
    predicate = ObjectQuerySpec(
        zones=("battlefield",),
        types_all=(
            ("artifact",) if subject == "artifacts" else ("creature",)
        ),
        token=(True if subject == "creature tokens" else None),
    )
    return (
        "continuous-fixed-query-keyword-grant-v1",
        {
            "handler_id": "continuous.ability.fixed-query-keyword-grant.v1",
            "schema_version": 1,
            "event": "characteristics.evaluate",
            "condition": {
                "target_controller": "source_controller",
                "predicate": predicate.to_dict(),
                "exclude_source": False,
            },
            "modifier": {"add_abilities": [keyword]},
        },
        "continuous.ability.fixed_query_keyword_grant",
    )


def _self_subject_pattern(source_name: str) -> str:
    source = SourceReferenceSpec(source_name).regex_pattern
    return rf"(?:This creature|This token|{source})"


def conditional_self_keyword_handler(
    oracle_line: str,
    *,
    source_name: str,
) -> tuple[str, Mapping[str, Any], str] | None:
    pattern = re.compile(
        rf"^{_self_subject_pattern(source_name)} has haste as long as an "
        r"opponent has (?P<life>\d+) or less life\.?$",
        re.IGNORECASE,
    )
    match = pattern.fullmatch(oracle_line.strip())
    if match is None:
        return None
    fragment = ConditionalKeywordSpec(
        keyword="Haste",
        opponent_life_at_most=int(match.group("life")),
    )
    return (
        "continuous-self-conditional-keyword-v1",
        {
            "handler_id": "ability.static.conditional-keyword.v1",
            "schema_version": 1,
            "event": "continuous",
            "fragment": ability_fragment_to_dict(fragment),
        },
        "continuous.characteristics.conditional_keyword",
    )


def dynamic_self_power_toughness_handler(
    oracle_line: str,
    *,
    source_name: str,
) -> tuple[str, Mapping[str, Any], str] | None:
    subject = _self_subject_pattern(source_name)
    per_object = re.compile(
        rf"^{subject} gets \+1/\+1 for each (?P<object>artifact you "
        r"control|creature card in your graveyard)\.?$",
        re.IGNORECASE,
    ).fullmatch(oracle_line.strip())
    if per_object is not None:
        count_kind = (
            CharacteristicCountKind.CONTROLLER_BATTLEFIELD_ARTIFACTS
            if per_object.group("object").casefold().startswith("artifact")
            else CharacteristicCountKind.OWNER_GRAVEYARD_CREATURE_CARDS
        )
        fragment = DynamicPowerToughnessSpec(
            count_kind=count_kind,
            calculation=PowerToughnessCalculation.PER_MATCHING_OBJECT,
            power=1,
            toughness=1,
        )
    else:
        threshold = re.compile(
            rf"^{subject} gets \+2/\+2 as long as there are three or more "
            r"land cards in your graveyard\.?$",
            re.IGNORECASE,
        ).fullmatch(oracle_line.strip())
        if threshold is None:
            return None
        fragment = DynamicPowerToughnessSpec(
            count_kind=CharacteristicCountKind.OWNER_GRAVEYARD_LAND_CARDS,
            calculation=PowerToughnessCalculation.FIXED_IF_THRESHOLD,
            power=2,
            toughness=2,
            minimum_count=3,
        )
    return (
        "continuous-self-dynamic-power-toughness-v1",
        {
            "handler_id": "ability.static.dynamic-power-toughness.v1",
            "schema_version": 1,
            "event": "continuous",
            "fragment": ability_fragment_to_dict(fragment),
        },
        "continuous.characteristics.dynamic_power_toughness",
    )


def _attached_abilities(value: str) -> tuple[str, ...] | None:
    normalized = re.sub(r",?\s+and\s+", ",", value.strip())
    abilities = tuple(
        part.strip().casefold()
        for part in normalized.split(",")
        if part.strip()
    )
    if (
        not abilities
        or len(set(abilities)) != len(abilities)
        or any(
            ability not in _ATTACHED_SUPPORTED_ABILITIES
            and re.fullmatch(r"toxic [1-9]\d*", ability) is None
            for ability in abilities
        )
    ):
        return None
    return tuple(ability.title() for ability in abilities)


def _toxic_ability_fragments(
    abilities: tuple[str, ...],
) -> tuple[Mapping[str, Any], ...]:
    return tuple(
        ability_fragment_to_dict(
            ToxicSpec(value=int(match.group("value")))
        )
        for ability in abilities
        if (
            match := re.fullmatch(
                r"Toxic (?P<value>[1-9]\d*)",
                ability,
                re.IGNORECASE,
            )
        )
        is not None
    )


def attached_fixed_characteristics_handler(
    oracle_line: str,
) -> tuple[str, Mapping[str, Any], str] | None:
    """Lower one closed attached-object fixed-characteristic sentence.

    Dynamic values, conditions, combat restrictions, quoted rules text, and
    mechanics outside the reviewed keyword vocabulary remain residual.
    """

    match = _ATTACHED_FIXED_CHARACTERISTICS.fullmatch(oracle_line.strip())
    if match is None:
        return None
    body = match.group("body")
    type_operations: list[dict[str, Any]] = []
    add_abilities: tuple[str, ...] = ()
    remove_abilities: tuple[str, ...] = ()
    add_ability_fragments: tuple[Mapping[str, Any], ...] = ()
    power = 0
    toughness = 0

    pt_match = _ATTACHED_FIXED_PT.fullmatch(body)
    ability_match = _ATTACHED_HAS_OR_LOSES.fullmatch(body)
    type_match = _ATTACHED_ADDED_TYPE.fullmatch(body)
    if pt_match is not None:
        power = int(pt_match.group("power"))
        toughness = int(pt_match.group("toughness"))
        if pt_match.group("abilities"):
            parsed = _attached_abilities(pt_match.group("abilities"))
            if parsed is None:
                return None
            add_abilities = parsed
            add_ability_fragments = _toxic_ability_fragments(parsed)
    elif ability_match is not None:
        parsed = _attached_abilities(ability_match.group("abilities"))
        if parsed is None:
            protection = (
                parse_protection_line(ability_match.group("abilities"))
                if ability_match.group("verb").casefold() == "has"
                else None
            )
            if protection is None:
                return None
            add_abilities = ("Protection",)
            add_ability_fragments = tuple(
                ability_fragment_to_dict(fragment)
                for fragment in protection
            )
        elif ability_match.group("verb").casefold() == "has":
            add_abilities = parsed
            add_ability_fragments = _toxic_ability_fragments(parsed)
        else:
            if _toxic_ability_fragments(parsed):
                # Removing a typed granted/printed ability requires a closed
                # fragment-removal descriptor, which this handler does not yet
                # own. Do not leave the executable fragment behind.
                return None
            remove_abilities = parsed
    elif type_match is not None:
        type_word = type_match.group("type")
        type_operations.append(
            {
                "op": "add_types",
                "field": (
                    "card_types"
                    if type_word.casefold() in _CARD_TYPE_WORDS
                    else "subtypes"
                ),
                "values": [type_word],
            }
        )
    else:
        return None

    if not (
        type_operations
        or add_abilities
        or remove_abilities
        or add_ability_fragments
        or power
        or toughness
    ):
        return None
    return (
        "continuous-attached-fixed-characteristics-v1",
        {
            "handler_id": "continuous.attached.fixed-characteristics.v1",
            "schema_version": 1,
            "event": "characteristics.evaluate",
            "condition": {"relation": "source_attached_object"},
            "modifier": {
                "type_operations": type_operations,
                "add_abilities": list(add_abilities),
                "remove_abilities": list(remove_abilities),
                "add_rules_text": [],
                "add_ability_fragments": list(
                    add_ability_fragments
                ),
                "power": power,
                "toughness": toughness,
            },
        },
        "continuous.attached.fixed_characteristics",
    )


def controlled_creature_until_end_of_turn_effect(
    oracle_line: str,
) -> tuple[str, tuple[Mapping[str, Any], ...], tuple[str, ...]] | None:
    parsed = controlled_creature_fixed_modifier(
        oracle_line, until_end_of_turn=True
    )
    if parsed is None:
        return None
    predicate, power, toughness, exclude_source = parsed
    predicate_fields = {
        **predicate.to_dict(),
        "controller": "$controller",
    }
    if exclude_source:
        predicate_fields["exclude_ref"] = "$source"
    return (
        "modify-controlled-creatures-fixed-stats-eot-v1",
        (
            {
                "op": "modify_all_matching_permanents_until_end_of_turn",
                "predicate": ObjectQuerySpec.from_dict(
                    predicate_fields
                ).to_dict(),
                "power": power,
                "toughness": toughness,
            },
        ),
        ("cr-611-continuous-effects",),
    )


def basic_land_type_addition_handler(
    oracle_line: str,
) -> tuple[str, Mapping[str, Any], str] | None:
    """Lower the exact CR 305.7 additive basic-land-type wording.

    This intentionally recognizes only the closed, nonconditional wording.
    Type-setting effects and restricted object sets require different layer-4
    contracts and remain residual rather than being approximated here.
    """

    match = _BASIC_LAND_TYPE_ADDITION.fullmatch(oracle_line.strip())
    if match is None:
        return None
    subtype = match.group("subtype").casefold()
    return (
        "continuous-add-basic-land-type-all-lands-v1",
        {
            "handler_id": "continuous.basic_land_type.add_all_lands.v1",
            "schema_version": 1,
            "event": "characteristics.evaluate",
            "condition": {"target_types_all": ["land"]},
            "modifier": {"basic_land_type": subtype},
        },
        "continuous.basic_land_type.add_all_lands",
    )
