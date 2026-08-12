from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.change_impact import (
    changed_files,
    changed_python_symbols,
    classify_changes,
    github_base,
    github_event_labels,
)
from scripts.test_shards import functional_shards, load_manifest, primary_matrix


PUBLIC_JOB_CONCURRENCY_LIMIT = 20
PUBLIC_JOB_RECOVERY_HEADROOM = 2
FIXED_PARALLEL_JOBS = 3  # generated, package, and Windows package
# Full Windows shards are consistently slower than their Ubuntu counterparts.
# Weight the two matrices from observed exact-head duration artifacts instead of
# giving every remaining slot to Ubuntu before considering the Windows tail.
UBUNTU_FUNCTIONAL_WEIGHT = 4
WINDOWS_FULL_WEIGHT = 5
EXPECTED_PR_JOB_IDS = frozenset(
    {
        "plan",
        "python",
        "generated",
        "package",
        "windows_compatibility",
        "windows_full",
        "windows_package",
        "windows_certification",
        "browser",
        "certification",
        "metrics",
    }
)


def workflow_job_ids(
    path: Path = ROOT / ".github" / "workflows" / "ci.yml",
) -> frozenset[str]:
    in_jobs = False
    identifiers: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "jobs:":
            in_jobs = True
            continue
        if not in_jobs:
            continue
        match = re.fullmatch(r"  ([a-z][a-z0-9_]*):", line)
        if match:
            identifiers.add(match.group(1))
    if identifiers != EXPECTED_PR_JOB_IDS:
        raise ValueError(
            "PR CI job graph changed without concurrency-budget review: "
            f"expected={sorted(EXPECTED_PR_JOB_IDS)} "
            f"observed={sorted(identifiers)}"
        )
    return frozenset(identifiers)


def python_matrix() -> dict:
    manifest = load_manifest()
    return {
        "include": [
            {"shard": shard} for shard in functional_shards(manifest)
        ]
    }


def ci_concurrency_budget(
    *,
    browser_full: bool,
    windows_full: bool,
) -> dict[str, int]:
    workflow_job_ids()
    manifest = load_manifest()
    browser_jobs = len(browser_matrix(browser_full)["include"])
    available_shard_jobs = (
        PUBLIC_JOB_CONCURRENCY_LIMIT
        - PUBLIC_JOB_RECOVERY_HEADROOM
        - FIXED_PARALLEL_JOBS
        - browser_jobs
    )
    python_job_count = len(functional_shards(manifest))
    if windows_full:
        windows_job_count = len(primary_matrix(manifest)["include"])
        weighted_python_demand = python_job_count * UBUNTU_FUNCTIONAL_WEIGHT
        weighted_windows_demand = windows_job_count * WINDOWS_FULL_WEIGHT
        weighted_total = weighted_python_demand + weighted_windows_demand
        windows_jobs = (
            available_shard_jobs * weighted_windows_demand + weighted_total // 2
        ) // weighted_total
        windows_jobs = min(
            windows_job_count,
            max(1, min(available_shard_jobs - 1, windows_jobs)),
        )
        python_jobs = min(
            python_job_count,
            available_shard_jobs - windows_jobs,
        )
        windows_jobs = min(
            windows_job_count,
            available_shard_jobs - python_jobs,
        )
    else:
        windows_jobs = 1
        python_jobs = min(
            python_job_count,
            available_shard_jobs - windows_jobs,
        )
    if python_jobs <= 0:
        raise ValueError("PR CI leaves no runner capacity for Python shards")
    peak = (
        python_jobs
        + windows_jobs
        + browser_jobs
        + FIXED_PARALLEL_JOBS
    )
    headroom = PUBLIC_JOB_CONCURRENCY_LIMIT - peak
    if headroom < PUBLIC_JOB_RECOVERY_HEADROOM:
        raise ValueError(
            "PR CI exceeds its concurrency budget: "
            f"peak={peak} limit={PUBLIC_JOB_CONCURRENCY_LIMIT} "
            f"headroom={headroom} required={PUBLIC_JOB_RECOVERY_HEADROOM}"
        )
    return {
        "public_job_limit": PUBLIC_JOB_CONCURRENCY_LIMIT,
        "target_headroom": PUBLIC_JOB_RECOVERY_HEADROOM,
        "python_max_parallel": python_jobs,
        "windows_max_parallel": windows_jobs,
        "browser_max_parallel": browser_jobs,
        "fixed_parallel_jobs": FIXED_PARALLEL_JOBS,
        "peak_jobs": peak,
        "headroom": headroom,
    }


def browser_matrix(browser_full: bool) -> dict:
    groups = (
        (
            {
                "group": "lifecycle",
                "grep": "@browser-lifecycle",
                "server_port": 18081,
                "web_port": 15171,
            },
            {
                "group": "rules",
                "grep": "@browser-rules",
                "server_port": 18082,
                "web_port": 15172,
            },
            {
                "group": "soak",
                "grep": "@browser-soak",
                "server_port": 18083,
                "web_port": 15173,
            },
        )
        if browser_full
        else (
            {
                "group": "smoke",
                "grep": "@smoke",
                "server_port": 18081,
                "web_port": 15171,
            },
        )
    )
    return {"include": list(groups)}


def _write_github_output(path: Path, plan: dict) -> None:
    budget = ci_concurrency_budget(
        browser_full=bool(plan["browser_full"]),
        windows_full=bool(plan["windows_full"]),
    )
    values = {
        "browser_full": str(plan["browser_full"]).lower(),
        "browser_focus_grep": "|".join(plan["browser_focus_patterns"]),
        "windows_full": str(plan["windows_full"]).lower(),
        "changed_files": json.dumps(plan["changed_files"], separators=(",", ":")),
        "browser_matrix": json.dumps(
            browser_matrix(bool(plan["browser_full"])), separators=(",", ":")
        ),
        "windows_matrix": json.dumps(
            primary_matrix(load_manifest()), separators=(",", ":")
        ),
        "python_matrix": json.dumps(
            python_matrix(), separators=(",", ":")
        ),
        "python_max_parallel": str(budget["python_max_parallel"]),
        "windows_max_parallel": str(budget["windows_max_parallel"]),
        "ci_peak_jobs": str(budget["peak_jobs"]),
        "ci_job_headroom": str(budget["headroom"]),
    }
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        for key, value in values.items():
            stream.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify exact PR CI impact")
    parser.add_argument("--base")
    parser.add_argument("--event")
    parser.add_argument("--github-output")
    args = parser.parse_args()
    base = args.base or github_base(args.event)
    plan = classify_changes(
        changed_files(base, include_worktree=False),
        changed_symbols=changed_python_symbols(
            base,
            include_worktree=False,
        ),
        labels=github_event_labels(args.event),
    ).to_dict()
    plan["ci_concurrency_budget"] = ci_concurrency_budget(
        browser_full=bool(plan["browser_full"]),
        windows_full=bool(plan["windows_full"]),
    )
    output = args.github_output or os.environ.get("GITHUB_OUTPUT")
    if output:
        _write_github_output(Path(output), plan)
    print(json.dumps({"base": base, **plan}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
