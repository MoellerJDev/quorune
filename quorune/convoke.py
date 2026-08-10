from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from typing import Any


MANA_VECTOR_KEYS = ("GENERIC", "W", "U", "B", "R", "G", "C")
CONVOKE_COLOR_SYMBOLS = ("W", "U", "B", "R", "G")
CONVOKE_PAYMENT_SYMBOLS = (*CONVOKE_COLOR_SYMBOLS, "GENERIC")


class ConvokeError(ValueError):
    """A Convoke descriptor, candidate, or payment plan is invalid."""


@dataclass(frozen=True, slots=True)
class ConvokeSpec:
    """The closed ordinary printed Convoke payment permission."""

    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ConvokeError("Unsupported Convoke specification version")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ConvokeSpec":
        if not isinstance(value, Mapping) or set(value) != {
            "schema_version",
            "kind",
        }:
            raise ConvokeError("Convoke specification fields are closed")
        if value.get("kind") != "convoke":
            raise ConvokeError("Convoke specification kind must be convoke")
        return cls(schema_version=value.get("schema_version"))

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "kind": "convoke"}


def _mana_vector(value: Mapping[str, Any]) -> tuple[int, ...]:
    if not isinstance(value, Mapping):
        raise ConvokeError("Convoke mana requirements must be an object")
    unknown = set(value).difference(MANA_VECTOR_KEYS)
    if unknown:
        raise ConvokeError(
            "Convoke mana requirements contain unsupported symbols: "
            + ", ".join(sorted(str(symbol) for symbol in unknown))
        )
    result: list[int] = []
    for symbol in MANA_VECTOR_KEYS:
        amount = value.get(symbol, 0)
        if type(amount) is not int or amount < 0:
            raise ConvokeError(
                "Convoke mana requirements must be exact nonnegative integers"
            )
        result.append(amount)
    return tuple(result)


def canonical_mana_requirements(value: Mapping[str, Any]) -> dict[str, int]:
    return dict(zip(MANA_VECTOR_KEYS, _mana_vector(value), strict=True))


@dataclass(frozen=True, slots=True)
class ConvokeCandidate:
    ref: str
    object_id: str
    logical_object_id: str
    colors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if any(
            type(value) is not str or not value
            for value in (self.ref, self.object_id, self.logical_object_id)
        ):
            raise ConvokeError(
                "Convoke candidates require public, physical, and logical identity"
            )
        if type(self.colors) is not tuple or any(
            type(color) is not str for color in self.colors
        ):
            raise ConvokeError(
                "Convoke candidate colors must be an immutable string tuple"
            )
        raw_colors = tuple(color.upper() for color in self.colors)
        if any(color not in CONVOKE_COLOR_SYMBOLS for color in raw_colors):
            raise ConvokeError("Convoke candidate colors must use W, U, B, R, or G")
        if len(raw_colors) != len(set(raw_colors)):
            raise ConvokeError("Convoke candidate colors must be unique")
        object.__setattr__(
            self,
            "colors",
            tuple(
                color for color in CONVOKE_COLOR_SYMBOLS if color in raw_colors
            ),
        )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ConvokeCandidate":
        if not isinstance(value, Mapping) or set(value) != {
            "ref",
            "object_id",
            "logical_object_id",
            "colors",
        }:
            raise ConvokeError("Convoke candidate fields are closed")
        colors = value.get("colors")
        if not isinstance(colors, list) or any(
            type(color) is not str for color in colors
        ):
            raise ConvokeError("Convoke candidate colors must be a string list")
        if any(
            type(value.get(field)) is not str or not value.get(field)
            for field in ("ref", "object_id", "logical_object_id")
        ):
            raise ConvokeError("Convoke candidate identities must be nonempty strings")
        return cls(
            ref=value["ref"],
            object_id=value["object_id"],
            logical_object_id=value["logical_object_id"],
            colors=tuple(colors),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref": self.ref,
            "object_id": self.object_id,
            "logical_object_id": self.logical_object_id,
            "colors": list(self.colors),
        }


@dataclass(frozen=True, slots=True)
class ConvokeContribution:
    candidate: ConvokeCandidate
    symbol: str

    def __post_init__(self) -> None:
        if not isinstance(self.candidate, ConvokeCandidate):
            raise ConvokeError(
                "Convoke contributions require a typed candidate"
            )
        if self.symbol not in CONVOKE_PAYMENT_SYMBOLS:
            raise ConvokeError("Convoke contributions require a colored or generic symbol")
        if self.symbol != "GENERIC" and self.symbol not in self.candidate.colors:
            raise ConvokeError(
                "A creature cannot pay a colored Convoke symbol it does not have"
            )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ConvokeContribution":
        if not isinstance(value, Mapping) or set(value) != {"candidate", "symbol"}:
            raise ConvokeError("Convoke contribution fields are closed")
        candidate = value.get("candidate")
        if not isinstance(candidate, Mapping) or type(value.get("symbol")) is not str:
            raise ConvokeError("Convoke contributions require a candidate and symbol")
        return cls(
            candidate=ConvokeCandidate.from_dict(candidate),
            symbol=value["symbol"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {"candidate": self.candidate.to_dict(), "symbol": self.symbol}


@dataclass(frozen=True, slots=True)
class ConvokePaymentPlan:
    requirements: tuple[int, ...]
    remaining: tuple[int, ...]
    contributions: tuple[ConvokeContribution, ...] = ()
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ConvokeError("Unsupported Convoke payment-plan schema version")
        if type(self.requirements) is not tuple or type(self.remaining) is not tuple:
            raise ConvokeError(
                "Convoke payment-plan mana vectors must be immutable tuples"
            )
        if type(self.contributions) is not tuple or any(
            not isinstance(value, ConvokeContribution)
            for value in self.contributions
        ):
            raise ConvokeError(
                "Convoke payment-plan contributions must be a typed tuple"
            )
        if len(self.requirements) != len(MANA_VECTOR_KEYS) or len(
            self.remaining
        ) != len(MANA_VECTOR_KEYS):
            raise ConvokeError("Convoke payment plans require complete mana vectors")
        if any(type(amount) is not int or amount < 0 for amount in self.requirements):
            raise ConvokeError("Convoke requirements must be nonnegative integers")
        if any(type(amount) is not int or amount < 0 for amount in self.remaining):
            raise ConvokeError("Convoke remainders must be nonnegative integers")
        canonical = tuple(
            sorted(
                self.contributions,
                key=lambda contribution: (
                    contribution.candidate.object_id,
                    contribution.candidate.logical_object_id,
                    contribution.candidate.ref,
                ),
            )
        )
        identities = tuple(
            contribution.candidate.object_id for contribution in canonical
        )
        logical_identities = tuple(
            contribution.candidate.logical_object_id
            for contribution in canonical
        )
        if len(identities) != len(set(identities)) or len(
            logical_identities
        ) != len(set(logical_identities)):
            raise ConvokeError("A permanent can contribute to Convoke only once")
        object.__setattr__(self, "contributions", canonical)
        expected = list(self.requirements)
        for contribution in canonical:
            index = MANA_VECTOR_KEYS.index(contribution.symbol)
            if expected[index] <= 0:
                raise ConvokeError("Convoke contributions exceed the announced cost")
            expected[index] -= 1
        if tuple(expected) != self.remaining:
            raise ConvokeError("Convoke contributions do not produce the stated remainder")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ConvokePaymentPlan":
        if not isinstance(value, Mapping) or set(value) != {
            "schema_version",
            "requirements",
            "remaining",
            "contributions",
            "fingerprint",
        }:
            raise ConvokeError("Convoke payment-plan fields are closed")
        contributions = value.get("contributions")
        requirements = value.get("requirements")
        remaining = value.get("remaining")
        if not isinstance(contributions, list):
            raise ConvokeError("Convoke contributions must be a list")
        if not isinstance(requirements, Mapping) or not isinstance(remaining, Mapping):
            raise ConvokeError("Convoke payment plans require mana-vector objects")
        if set(requirements) != set(MANA_VECTOR_KEYS) or set(remaining) != set(
            MANA_VECTOR_KEYS
        ):
            raise ConvokeError("Serialized Convoke mana vectors must be complete")
        plan = cls(
            schema_version=value.get("schema_version"),
            requirements=_mana_vector(requirements),
            remaining=_mana_vector(remaining),
            contributions=tuple(
                ConvokeContribution.from_dict(contribution)
                for contribution in contributions
            ),
        )
        if type(value.get("fingerprint")) is not str or value["fingerprint"] != plan.fingerprint:
            raise ConvokeError("Convoke payment-plan fingerprint mismatch")
        return plan

    @property
    def requirement_dict(self) -> dict[str, int]:
        return dict(zip(MANA_VECTOR_KEYS, self.requirements, strict=True))

    @property
    def remaining_dict(self) -> dict[str, int]:
        return dict(zip(MANA_VECTOR_KEYS, self.remaining, strict=True))

    @property
    def selected_refs(self) -> tuple[str, ...]:
        return tuple(
            contribution.candidate.ref for contribution in self.contributions
        )

    @property
    def selected_object_ids(self) -> frozenset[str]:
        return frozenset(
            contribution.candidate.object_id for contribution in self.contributions
        )

    @property
    def fingerprint(self) -> str:
        payload = self.to_dict(include_fingerprint=False)
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return sha256(encoded).hexdigest()

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        result = {
            "schema_version": self.schema_version,
            "requirements": self.requirement_dict,
            "remaining": self.remaining_dict,
            "contributions": [
                contribution.to_dict() for contribution in self.contributions
            ],
        }
        if include_fingerprint:
            result["fingerprint"] = self.fingerprint
        return result


def _canonical_candidates(
    candidates: Iterable[ConvokeCandidate],
) -> tuple[ConvokeCandidate, ...]:
    result = tuple(
        sorted(
            candidates,
            key=lambda candidate: (
                candidate.object_id,
                candidate.logical_object_id,
                candidate.ref,
            ),
        )
    )
    identities = tuple(candidate.object_id for candidate in result)
    logical_identities = tuple(candidate.logical_object_id for candidate in result)
    refs = tuple(candidate.ref for candidate in result)
    if (
        len(identities) != len(set(identities))
        or len(logical_identities) != len(set(logical_identities))
        or len(refs) != len(set(refs))
    ):
        raise ConvokeError("Convoke candidates must have unique identities and refs")
    return result


def convoke_plans_for_selected(
    requirements: Mapping[str, Any],
    candidates: Sequence[ConvokeCandidate],
) -> tuple[ConvokePaymentPlan, ...]:
    """Return every distinct canonical remainder for the selected permanents."""

    base = _mana_vector(requirements)
    selected = _canonical_candidates(candidates)
    payable_positions = tuple(MANA_VECTOR_KEYS.index(symbol) for symbol in CONVOKE_PAYMENT_SYMBOLS)
    if len(selected) > sum(base[index] for index in payable_positions):
        return ()
    states: dict[tuple[int, ...], tuple[ConvokeContribution, ...]] = {base: ()}
    for candidate in selected:
        next_states: dict[tuple[int, ...], tuple[ConvokeContribution, ...]] = {}
        for remaining, contributions in sorted(states.items()):
            choices = tuple(
                symbol
                for symbol in CONVOKE_PAYMENT_SYMBOLS
                if remaining[MANA_VECTOR_KEYS.index(symbol)] > 0
                and (symbol == "GENERIC" or symbol in candidate.colors)
            )
            for symbol in choices:
                values = list(remaining)
                values[MANA_VECTOR_KEYS.index(symbol)] -= 1
                next_remaining = tuple(values)
                proposal = (*contributions, ConvokeContribution(candidate, symbol))
                prior = next_states.get(next_remaining)
                proposal_key = tuple(
                    CONVOKE_PAYMENT_SYMBOLS.index(item.symbol) for item in proposal
                )
                prior_key = (
                    tuple(CONVOKE_PAYMENT_SYMBOLS.index(item.symbol) for item in prior)
                    if prior is not None
                    else None
                )
                if prior is None or proposal_key < prior_key:
                    next_states[next_remaining] = proposal
        states = next_states
        if not states:
            return ()
    return tuple(
        ConvokePaymentPlan(
            requirements=base,
            remaining=remaining,
            contributions=contributions,
        )
        for remaining, contributions in sorted(states.items())
    )


ConvokeAffordability = Callable[[ConvokePaymentPlan], bool]


def select_convoke_plan(
    requirements: Mapping[str, Any],
    candidates: Sequence[ConvokeCandidate],
    *,
    affordable: ConvokeAffordability,
) -> ConvokePaymentPlan | None:
    for plan in convoke_plans_for_selected(requirements, candidates):
        if affordable(plan):
            return plan
    return None


def find_convoke_plan(
    requirements: Mapping[str, Any],
    candidates: Sequence[ConvokeCandidate],
    *,
    affordable: ConvokeAffordability,
) -> ConvokePaymentPlan | None:
    """Find the deterministic minimum-permanent payable Convoke plan."""

    base = canonical_mana_requirements(requirements)
    ordered = _canonical_candidates(candidates)
    maximum = min(
        len(ordered),
        sum(base[symbol] for symbol in CONVOKE_PAYMENT_SYMBOLS),
    )
    for count in range(maximum + 1):
        for selected in combinations(ordered, count):
            plan = select_convoke_plan(base, selected, affordable=affordable)
            if plan is not None:
                return plan
    return None


__all__ = [
    "CONVOKE_COLOR_SYMBOLS",
    "CONVOKE_PAYMENT_SYMBOLS",
    "MANA_VECTOR_KEYS",
    "ConvokeCandidate",
    "ConvokeContribution",
    "ConvokeError",
    "ConvokePaymentPlan",
    "ConvokeSpec",
    "canonical_mana_requirements",
    "convoke_plans_for_selected",
    "find_convoke_plan",
    "select_convoke_plan",
]
