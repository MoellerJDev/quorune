from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

import pytest


EXPECTED_COLLECTION_ENV = "QUORUNE_EXPECTED_UNITTEST_COLLECTION"


def canonical_unittest_item_id(item: Any) -> str:
    """Return the unittest identity that owns one pytest collection item."""

    testcase = getattr(item, "_testcase", None)
    identifier = testcase.id() if testcase is not None else None
    if not isinstance(identifier, str) or not identifier:
        nodeid = getattr(item, "nodeid", repr(item))
        raise pytest.UsageError(
            "parallel deterministic shards only accept unittest items: "
            f"{nodeid}"
        )
    return identifier


def canonical_collection(items: Iterable[Any]) -> tuple[str, ...]:
    identifiers = tuple(sorted(canonical_unittest_item_id(item) for item in items))
    if len(identifiers) != len(set(identifiers)):
        raise pytest.UsageError(
            "parallel unittest collection contains duplicate test IDs"
        )
    return identifiers


def expected_collection(path: Path) -> tuple[str, ...]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
    ):
        raise pytest.UsageError(
            "expected unittest collection must be a nonempty string list"
        )
    identifiers = tuple(value)
    if identifiers != tuple(sorted(identifiers)):
        raise pytest.UsageError(
            "expected unittest collection must be canonically sorted"
        )
    if len(identifiers) != len(set(identifiers)):
        raise pytest.UsageError(
            "expected unittest collection contains duplicate test IDs"
        )
    return identifiers


def pytest_collection_finish(session: Any) -> None:
    """Fail every xdist worker closed if pytest changes the unittest test set."""

    # Under xdist only workers collect. The controller receives their canonical
    # collection and enforces equality across workers itself.
    if not hasattr(session.config, "workerinput"):
        return
    raw = os.environ.get(EXPECTED_COLLECTION_ENV)
    if not raw:
        raise pytest.UsageError(
            f"{EXPECTED_COLLECTION_ENV} is required under xdist"
        )
    expected = expected_collection(Path(raw))
    observed = canonical_collection(session.items)
    if observed != expected:
        missing = sorted(set(expected) - set(observed))
        unexpected = sorted(set(observed) - set(expected))
        raise pytest.UsageError(
            "pytest/unittest collection parity failed: "
            f"expected={len(expected)} observed={len(observed)} "
            f"missing={missing[:10]} unexpected={unexpected[:10]}"
        )


__all__ = [
    "EXPECTED_COLLECTION_ENV",
    "canonical_collection",
    "canonical_unittest_item_id",
    "expected_collection",
]
