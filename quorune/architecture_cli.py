from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from quorune.util import stable_json


_REPORT = Path("coverage/architecture-audit.json")
_REASON_FIELD = "reason"


def _load_report(root: Path) -> dict[str, Any]:
    path = root / _REPORT
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 2:
        raise ValueError(f"{path} is not a current architecture audit")
    return value


def _capsules(report: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    value = report.get("architecture", {}).get("subsystem_capsules", [])
    if not isinstance(value, list):
        raise ValueError("architecture audit has no subsystem capsule list")
    return [row for row in value if isinstance(row, Mapping)]


def _run_git(root: Path, *args: str, check: bool = True) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        if check:
            detail = result.stderr.strip() or result.stdout.strip()
            raise ValueError(f"git {' '.join(args)} failed: {detail}")
        return None
    return result.stdout.strip()


def _changed_files(root: Path, base: str) -> list[str]:
    merge_base = _run_git(root, "merge-base", base, "HEAD")
    output = _run_git(root, "diff", "--name-only", str(merge_base)) or ""
    return sorted({line.replace("\\", "/") for line in output.splitlines() if line})


def changed_capsules(
    report: Mapping[str, Any], changed_files: Sequence[str]
) -> dict[str, Any]:
    normalized = sorted({str(value).replace("\\", "/") for value in changed_files})
    matched: dict[str, list[str]] = {}
    covered: set[str] = set()
    for capsule in _capsules(report):
        modules = [str(value) for value in capsule.get("modules", [])]
        files = [
            relative
            for relative in normalized
            if any(
                relative == module
                or relative.startswith(module.rstrip("/") + "/")
                for module in modules
            )
        ]
        if files:
            identifier = str(capsule["id"])
            matched[identifier] = files
            covered.update(files)
    return {
        "changed_files": normalized,
        "affected_capsules": [
            {"subsystem": identifier, "files": matched[identifier]}
            for identifier in sorted(matched)
        ],
        "unmapped_files": sorted(set(normalized) - covered),
    }


def _debt_view(report: Mapping[str, Any]) -> dict[str, Any]:
    architecture = report["architecture"]
    writes = architecture["direct_game_state_write_ownership"]
    runtime_text = architecture["runtime_oracle_text_access"]
    interaction = architecture["interaction_assurance_baseline"]
    return {
        "missing_dedicated_owner_count": len(
            architecture["missing_dedicated_owners"]
        ),
        "missing_dedicated_owners": architecture["missing_dedicated_owners"],
        "commander_engine_logical_lines": architecture["engine"]["logical_lines"],
        "direct_game_state_writes": {
            "total": writes["total_detected_writes"],
            "engine_local": writes["writes_in_commander_engine"],
            "canonical_owner": writes["writes_in_canonical_owners"],
            "unowned": writes["unowned_writes"],
        },
        "runtime_oracle_text_access": {
            "total": runtime_text["total_accesses"],
            "by_classification": runtime_text["by_classification"],
        },
        "oversized_modules": architecture["production"]["oversized_module_count"],
        "oversized_functions_and_methods": architecture["production"][
            "oversized_function_and_method_count"
        ],
        "interaction_assurance": interaction,
        "migration_queue": architecture["migration_queue"],
        "next_owner_migration": (
            architecture["migration_queue"][0]
            if architecture["migration_queue"]
            else None
        ),
    }


def _write_view(
    report: Mapping[str, Any], subsystem: str | None
) -> dict[str, Any]:
    inventory = report["architecture"]["direct_game_state_write_ownership"]
    if subsystem is None:
        return {
            key: inventory[key]
            for key in (
                "total_detected_writes",
                "writes_in_commander_engine",
                "writes_in_canonical_owners",
                "unowned_writes",
                "by_classification",
                "by_subsystem",
                "newly_added_writes",
                "removed_writes",
                "migrated_writes",
            )
        }
    locations = [
        row for row in inventory["locations"] if subsystem in row["subsystems"]
    ]
    known = {str(row["id"]) for row in _capsules(report)}
    if subsystem not in known:
        raise KeyError(f"unknown architecture subsystem: {subsystem}")
    return {
        "subsystem": subsystem,
        "count": len(locations),
        "locations": locations,
    }


def _runtime_text_view(report: Mapping[str, Any]) -> dict[str, Any]:
    inventory = report["architecture"]["runtime_oracle_text_access"]
    return {
        "total_accesses": inventory["total_accesses"],
        "by_classification": inventory["by_classification"],
        "prohibited_runtime_interpretation_count": inventory[
            "prohibited_runtime_interpretation_count"
        ],
        "prohibited_runtime_interpretation": inventory[
            "prohibited_runtime_interpretation"
        ],
    }


def _worktree_rows(root: Path) -> list[dict[str, Any]]:
    output = _run_git(root, "worktree", "list", "--porcelain") or ""
    rows: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in [*output.splitlines(), ""]:
        if not line:
            if current:
                rows.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "branch":
            value = value.removeprefix("refs/heads/")
        current[key] = value or True
    return rows


def _owner_coordinates(root: Path, report: Mapping[str, Any]) -> dict[str, Any]:
    worktrees = _worktree_rows(root)
    current_path = str(root.resolve()).casefold()
    current = next(
        (
            row
            for row in worktrees
            if str(Path(str(row["worktree"])).resolve()).casefold() == current_path
        ),
        {},
    )
    feature_rows = [
        row for row in worktrees if str(row.get("branch", "")) != "main"
    ]
    published = [
        row
        for row in feature_rows
        if row.get("branch")
        and _run_git(
            root,
            "rev-parse",
            "--abbrev-ref",
            f"{row['branch']}@{{upstream}}",
            check=False,
        )
    ]
    unpublished = [row for row in feature_rows if row not in published]
    ordered = [*published, *unpublished]
    slots: dict[str, Any] = {
        "slot_a": ordered[0] if ordered else None,
        "slot_b": ordered[1] if len(ordered) > 1 else None,
    }
    return {
        "current_feature": {
            "branch": current.get("branch"),
            "head": _run_git(root, "rev-parse", "HEAD"),
            "worktree": current.get("worktree"),
        },
        "current_main": {
            "head": _run_git(root, "rev-parse", "origin/main", check=False),
            "source": "origin/main",
        },
        "certified_exact_head": {
            "head": None,
            _REASON_FIELD: (
                "Exact-head certification receipts are GitHub Actions artifacts, "
                "not trusted from tracked source files."
            ),
        },
        "evaluated_source_tree": report["coordinates"]["evaluated_source_tree"],
        "active_slots": slots,
        "worktrees": worktrees,
    }


def execute_architecture_operation(
    operation: str,
    *,
    root: str | Path = ".",
    subsystem: str | None = None,
    base: str | None = None,
    changed_files: Sequence[str] | None = None,
) -> dict[str, Any]:
    repository = Path(root).resolve()
    report = _load_report(repository)
    if operation == "show":
        matches = [row for row in _capsules(report) if row.get("id") == subsystem]
        if len(matches) != 1:
            raise KeyError(f"unknown architecture subsystem: {subsystem}")
        return dict(matches[0])
    if operation == "changed":
        if changed_files is None:
            if not base:
                raise ValueError("architecture changed requires --base")
            changed_files = _changed_files(repository, base)
        return {"base": base, **changed_capsules(report, changed_files)}
    if operation == "debt":
        return _debt_view(report)
    if operation == "writes":
        return _write_view(report, subsystem)
    if operation == "runtime-text":
        return _runtime_text_view(report)
    if operation == "owners":
        return _owner_coordinates(repository, report)
    raise ValueError(f"unknown architecture operation: {operation}")


def configure_architecture_commands(sub: Any) -> None:
    parser = sub.add_parser(
        "architecture", help="Inspect generated architecture ownership and debt"
    )
    commands = parser.add_subparsers(dest="architecture_cmd", required=True)
    show = commands.add_parser("show", help="Show one bounded subsystem capsule")
    show.add_argument("subsystem")
    changed = commands.add_parser(
        "changed", help="Map changes against a Git base to subsystem capsules"
    )
    changed.add_argument("--base", required=True)
    commands.add_parser("debt", help="Show current architecture debt metrics")
    writes = commands.add_parser("writes", help="Show classified state writes")
    writes.add_argument("subsystem", nargs="?")
    commands.add_parser(
        "runtime-text", help="Show structurally inventoried Oracle-text access"
    )
    commands.add_parser("owners", help="Show live branch, main, and worktree owners")
    for child in commands.choices.values():
        child.add_argument("--root", default=".")


def run_architecture_command(args: argparse.Namespace) -> int | None:
    if args.cmd != "architecture":
        return None
    try:
        value = execute_architecture_operation(
            args.architecture_cmd,
            root=args.root,
            subsystem=getattr(args, "subsystem", None),
            base=getattr(args, "base", None),
        )
    except (KeyError, OSError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print(stable_json(value))
    return 0


__all__ = [
    "changed_capsules",
    "configure_architecture_commands",
    "execute_architecture_operation",
    "run_architecture_command",
]
