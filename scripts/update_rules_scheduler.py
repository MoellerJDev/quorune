from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quorune.rules_scheduler import (
    build_rules_dependency_queue_from_root,
)
from quorune.util import stable_json


JSON_OUTPUT = ROOT / "coverage" / "rules-dependency-queue.json"
MARKDOWN_OUTPUT = ROOT / "docs" / "RULES_DEPENDENCY_QUEUE.md"


def _json_text(value: Mapping[str, Any]) -> str:
    return stable_json(value) + "\n"


def _compact_markdown(value: Mapping[str, Any]) -> str:
    summary = value["summary"]
    selected = value["selected_batch"]
    work = value["work_selection"]
    selected_work = next(
        candidate
        for candidate in work["candidates"]
        if candidate["candidate_id"] == work["selected_candidate_id"]
    )
    command = r".\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write"
    fingerprint = hashlib.sha256(_json_text(value).encode("utf-8")).hexdigest()
    blockers = list(selected["exit_criteria"])
    if not blockers:
        blockers = ["No selected-batch blockers were reported."]
    lines = [
        "---",
        'title: "Rules dependency queue"',
        'status: "generated"',
        'authoritative_source: "coverage/rules-dependency-queue.json"',
        f'verified: "{fingerprint}"',
        'audience: "rules, compiler, and engine contributors"',
        'maintenance: "generated"',
        'generated_source: "coverage/rules-dependency-queue.json"',
        f'generation_command: "{command}"',
        "---",
        "",
        "# Rules dependency queue",
        "",
        f"Source fingerprint: `{value['fingerprint']}`",
        "",
        "## Current top-level state",
        "",
        f"- Pinned rules: `{summary['total_rules']}`",
        f"- Queued rules: `{summary['queued_rules']}`",
        f"- Subsystems: `{summary['subsystem_count']}`",
        f"- Selected subsystem: `{selected['subsystem_id']}`",
        f"- Selected batch: `{selected['batch_id']}`",
        f"- Selected cross-program work: `{selected_work['candidate_id']}`",
        f"- Selected work class: `{selected_work['candidate_class']}`",
        "",
        "## Cross-program work selection",
        "",
        "The rules batch remains dependency-ready, but final foreground work is "
        "reranked with deterministic CI, replay/privacy, architecture, runtime-text, "
        "interaction-assurance, compiler, and card-frontier evidence. A larger card "
        "gain cannot outrank a higher-priority correctness class.",
        "",
        "Priority classes: "
        + " → ".join(f"`{item}`" for item in work["priority_classes"]),
        "",
        "| Rank | State | Candidate | Class | Complete cards | Residuals | Runtime text | Direct writes |",
        "|---:|---|---|---|---:|---:|---:|---:|",
        *(
            "| "
            + " | ".join(
                [
                    str(candidate["rank"]),
                    str(candidate["selection_state"]),
                    f"`{candidate['candidate_id']}`",
                    f"`{candidate['candidate_class']}`",
                    (
                        str(candidate["expected_complete_card_gain"])
                        if candidate["expected_complete_card_gain"] is not None
                        else "unknown"
                    ),
                    (
                        str(candidate["expected_material_residual_reduction"])
                        if candidate["expected_material_residual_reduction"] is not None
                        else "unknown"
                    ),
                    (
                        str(
                            candidate["runtime_oracle_text_removal"].get(
                                "expected_count"
                            )
                        )
                        if candidate["runtime_oracle_text_removal"].get(
                            "expected_count"
                        )
                        is not None
                        else "unknown"
                    ),
                    (
                        str(candidate["direct_write_migration"].get("expected_count"))
                        if candidate["direct_write_migration"].get("expected_count")
                        is not None
                        else "unknown"
                    ),
                ]
            )
            + " |"
            for candidate in work["candidates"]
        ),
        "",
        f"Selected reason: {selected_work['reranking_reason']}",
        "",
        "## Top blockers",
        "",
        *(f"- {item}" for item in blockers[:5]),
        "",
        "Complete rule, subsystem, dependency, classification, and selected-batch data "
        "plus complete readiness, blocker-card, architecture, interaction, and reranking "
        "fields for every serious candidate are in the "
        "[machine-readable rules queue](../coverage/rules-dependency-queue.json).",
        "",
        "Exact generation command:",
        "",
        "```powershell",
        command,
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build_rules_dependency_queue_from_root(ROOT)
    expected_json = _json_text(value)
    expected_markdown = _compact_markdown(value)
    if args.write:
        JSON_OUTPUT.write_text(
            expected_json, encoding="utf-8", newline="\n"
        )
        MARKDOWN_OUTPUT.write_text(
            expected_markdown, encoding="utf-8", newline="\n"
        )
        return 0
    stale = []
    for path, expected in (
        (JSON_OUTPUT, expected_json),
        (MARKDOWN_OUTPUT, expected_markdown),
    ):
        actual = path.read_text(encoding="utf-8") if path.exists() else ""
        if actual != expected:
            stale.append(path.relative_to(ROOT).as_posix())
    if stale:
        print(
            "Rules scheduler outputs are stale; run "
            "python scripts/update_rules_scheduler.py --write: "
            + ", ".join(stale),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
