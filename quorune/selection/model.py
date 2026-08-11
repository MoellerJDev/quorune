from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Mapping

from ..replacement.immutable import (
    FrozenMap,
    ImmutableValueError,
    thaw_value,
)


class SelectionModelError(ValueError):
    """A target, search, or nontarget continuation is malformed."""


class SelectionContract(str, Enum):
    TARGETING = "targeting"
    SEARCH = "search"
    NONTARGET_CHOICE = "nontarget_choice"
    COST_SELECTION = "cost_selection"
    AFFECTED_OBJECT_FILTER = "affected_object_filter"


def _nonempty(value: Any, *, field_name: str) -> str:
    if type(value) is not str or not value:
        raise SelectionModelError(f"{field_name} must be a nonempty string")
    return value


def _optional_nonempty(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    return _nonempty(value, field_name=field_name)


@dataclass(frozen=True, slots=True)
class SelectionContinuation:
    """Replay-pinned identity and payload for one server-issued selection.

    The contract is explicit so targeting, hidden-zone searches, public
    nontarget choices, and cost selections cannot silently share legality
    semantics.  The payload is immutable and operation-specific; the owner
    that issued ``operation_id`` is the only component allowed to decode it.
    """

    contract: SelectionContract
    operation_id: str
    actor: str
    state_revision: int
    payload: FrozenMap = field(default_factory=FrozenMap)
    stack_ref: str | None = None
    source_ref: str | None = None
    visibility: str = "public"
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise SelectionModelError("Unsupported selection continuation version")
        if not isinstance(self.contract, SelectionContract):
            try:
                object.__setattr__(
                    self,
                    "contract",
                    SelectionContract(str(self.contract)),
                )
            except ValueError as exc:
                raise SelectionModelError("Unknown selection contract") from exc
        _nonempty(self.operation_id, field_name="operation_id")
        _nonempty(self.actor, field_name="actor")
        _optional_nonempty(self.stack_ref, field_name="stack_ref")
        _optional_nonempty(self.source_ref, field_name="source_ref")
        if type(self.state_revision) is not int or self.state_revision < 0:
            raise SelectionModelError("state_revision must be a nonnegative integer")
        if self.visibility not in {"public", "actor_private"}:
            raise SelectionModelError("Unknown selection visibility")
        if not isinstance(self.payload, FrozenMap):
            if not isinstance(self.payload, Mapping):
                raise SelectionModelError("selection payload must be a mapping")
            try:
                object.__setattr__(self, "payload", FrozenMap(self.payload))
            except ImmutableValueError as exc:
                raise SelectionModelError(str(exc)) from exc

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "contract": self.contract.value,
            "operation_id": self.operation_id,
            "actor": self.actor,
            "state_revision": self.state_revision,
            "stack_ref": self.stack_ref,
            "source_ref": self.source_ref,
            "visibility": self.visibility,
            "payload": thaw_value(self.payload),
        }

    @property
    def fingerprint(self) -> str:
        serialized = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SelectionContinuation":
        if not isinstance(value, Mapping):
            raise SelectionModelError(
                "selection continuation must be a mapping"
            )
        required = {
            "schema_version",
            "contract",
            "operation_id",
            "actor",
            "state_revision",
            "stack_ref",
            "source_ref",
            "visibility",
            "payload",
        }
        missing = sorted(required - value.keys())
        unknown = sorted(value.keys() - required)
        if missing:
            raise SelectionModelError(
                "selection continuation is missing fields: " + ", ".join(missing)
            )
        if unknown:
            raise SelectionModelError(
                "selection continuation has unknown fields: " + ", ".join(unknown)
            )
        payload = value["payload"]
        if not isinstance(payload, Mapping):
            raise SelectionModelError("selection payload must be a mapping")
        try:
            contract = SelectionContract(str(value["contract"]))
        except ValueError as exc:
            raise SelectionModelError("Unknown selection contract") from exc
        try:
            return cls(
                schema_version=value["schema_version"],
                contract=contract,
                operation_id=value["operation_id"],
                actor=value["actor"],
                state_revision=value["state_revision"],
                stack_ref=value["stack_ref"],
                source_ref=value["source_ref"],
                visibility=value["visibility"],
                payload=FrozenMap(payload),
            )
        except ImmutableValueError as exc:
            raise SelectionModelError(str(exc)) from exc


def decode_selection_continuation(
    value: Mapping[str, Any],
    *,
    expected_contract: SelectionContract,
    expected_operation_id: str,
    legacy: SelectionContinuation | None = None,
) -> SelectionContinuation:
    """Decode the strict envelope or an explicitly supplied v3 legacy shape."""

    raw = value.get("selection")
    if raw is None:
        if legacy is None:
            raise SelectionModelError("Selection continuation envelope is missing")
        continuation = legacy
    else:
        if not isinstance(raw, Mapping):
            raise SelectionModelError("selection continuation must be a mapping")
        continuation = SelectionContinuation.from_dict(raw)
    if continuation.contract is not expected_contract:
        raise SelectionModelError("Selection contract changed")
    if continuation.operation_id != expected_operation_id:
        raise SelectionModelError("Selection operation identity changed")
    return continuation
