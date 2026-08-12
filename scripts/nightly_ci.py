from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.test_shards import load_manifest, primary_matrix


PUBLIC_JOB_CONCURRENCY_LIMIT = 20
NIGHTLY_PYTHON_MAX_PARALLEL = 6
NIGHTLY_OTHER_PARALLEL_JOBS = 9
NIGHTLY_RECOVERY_HEADROOM = 5


def nightly_python_matrix() -> dict:
    rows = []
    for row in primary_matrix(load_manifest())["include"]:
        suite = row["shard"]
        rows.extend(
            (
                {
                    "platform": "ubuntu",
                    "runs_on": "ubuntu-latest",
                    "shard": suite,
                },
                {
                    "platform": "windows",
                    "runs_on": "windows-latest",
                    "shard": suite,
                },
            )
        )
    return {"include": rows}


def nightly_concurrency_budget() -> dict[str, int]:
    peak = NIGHTLY_PYTHON_MAX_PARALLEL + NIGHTLY_OTHER_PARALLEL_JOBS
    headroom = PUBLIC_JOB_CONCURRENCY_LIMIT - peak
    if headroom < NIGHTLY_RECOVERY_HEADROOM:
        raise ValueError(
            "Nightly CI exceeds its concurrency budget: "
            f"peak={peak} limit={PUBLIC_JOB_CONCURRENCY_LIMIT} "
            f"headroom={headroom} required={NIGHTLY_RECOVERY_HEADROOM}"
        )
    return {
        "public_job_limit": PUBLIC_JOB_CONCURRENCY_LIMIT,
        "python_max_parallel": NIGHTLY_PYTHON_MAX_PARALLEL,
        "other_parallel_jobs": NIGHTLY_OTHER_PARALLEL_JOBS,
        "peak_jobs": peak,
        "headroom": headroom,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build fail-closed nightly CI plan")
    parser.add_argument("--github-output")
    args = parser.parse_args()
    matrix = nightly_python_matrix()
    budget = nightly_concurrency_budget()
    output = args.github_output or os.environ.get("GITHUB_OUTPUT")
    if output:
        with Path(output).open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(
                "python_matrix="
                + json.dumps(matrix, separators=(",", ":"))
                + "\n"
            )
            stream.write(
                f"python_max_parallel={budget['python_max_parallel']}\n"
            )
    print(json.dumps({"matrix": matrix, "budget": budget}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
