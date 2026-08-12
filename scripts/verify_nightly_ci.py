from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.shard_result_validation import (
    ShardResultError,
    result_documents,
    validate_result_document,
)
from scripts.test_shards import load_manifest


class NightlyCertificationError(ValueError):
    pass


EXPECTED_DEPENDENCIES = frozenset(
    {
        "plan",
        "python",
        "browser",
        "properties",
        "mutation-and-soak",
        "corpus",
        "security",
    }
)


def validate_dependencies(needs: Mapping) -> None:
    observed = set(needs)
    if observed != EXPECTED_DEPENDENCIES:
        raise NightlyCertificationError(
            "Nightly dependency graph is incomplete or unreviewed: "
            + json.dumps(
                {
                    "missing": sorted(EXPECTED_DEPENDENCIES - observed),
                    "unknown": sorted(observed - EXPECTED_DEPENDENCIES),
                },
                sort_keys=True,
            )
        )
    failed = sorted(
        name
        for name in EXPECTED_DEPENDENCIES
        if not isinstance(needs.get(name), Mapping)
        or needs[name].get("result") != "success"
    )
    if failed:
        raise NightlyCertificationError(
            f"Nightly dependencies did not all pass: {failed}"
        )


def expected_assignments() -> tuple[tuple[str, str, str], ...]:
    manifest = load_manifest()
    return tuple(
        (
            platform,
            suite,
            "unittest" if suite == "generated-validation" else "pytest-xdist",
        )
        for suite in manifest["execution_order"]
        for platform in ("ubuntu", "windows")
    )


def validate_results(directory: Path) -> dict:
    expected = {
        (platform, suite): backend
        for platform, suite, backend in expected_assignments()
    }
    observed: dict[tuple[str, str], dict] = {}
    for document in result_documents(directory):
        key = (document.get("platform"), document.get("suite"))
        if key in observed:
            raise NightlyCertificationError(
                f"Duplicate nightly shard result: {key}"
            )
        backend = expected.get(key)
        if backend is None:
            raise NightlyCertificationError(
                f"Unexpected nightly shard result: {key}"
            )
        try:
            observed[key] = validate_result_document(
                document,
                expected_suite=key[1],
                expected_platform=key[0],
                expected_backend=backend,
            )
        except ShardResultError as exc:
            raise NightlyCertificationError(str(exc)) from exc
    missing = sorted(set(expected) - set(observed))
    if missing:
        raise NightlyCertificationError(
            f"Nightly shard results are incomplete: {missing}"
        )
    return {
        "assignments": len(observed),
        "platforms": 2,
        "suites": len(load_manifest()["execution_order"]),
        "tests_run": sum(item["tests_run"] for item in observed.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed nightly certification")
    parser.add_argument("--results-dir", required=True)
    args = parser.parse_args()
    raw = os.environ.get("CI_NIGHTLY_NEEDS_JSON")
    if not raw:
        print("CI_NIGHTLY_NEEDS_JSON is required")
        return 1
    try:
        needs = json.loads(raw)
        if not isinstance(needs, dict):
            raise NightlyCertificationError(
                "CI_NIGHTLY_NEEDS_JSON must contain an object"
            )
        validate_dependencies(needs)
        summary = validate_results(Path(args.results_dir))
    except (
        json.JSONDecodeError,
        NightlyCertificationError,
        OSError,
        ShardResultError,
        ValueError,
    ) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps({"ok": True, **summary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
