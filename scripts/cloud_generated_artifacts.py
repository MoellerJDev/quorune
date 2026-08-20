from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generated_artifacts import (
    GeneratorSpec,
    all_outputs,
    check_command,
    load_manifest,
    topological_order,
    write_command,
)
from scripts.generated_finalization_receipt import write_finalization_receipt
from scripts.source_tree_fingerprint import tracked_worktree_source_fingerprint
from scripts.validate_python_runtime import require_supported_python


SCHEMA_VERSION = 1
_LOCAL_ROOT = (ROOT / "local").resolve()


class CloudGeneratedArtifactError(RuntimeError):
    """A cloud-generated owner or bundle is malformed or unsafe."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_stage_directory(raw: str | Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(_LOCAL_ROOT)
    except ValueError as exc:
        raise CloudGeneratedArtifactError(
            "Cloud artifact staging directories must stay below local/"
        ) from exc
    if resolved == _LOCAL_ROOT:
        raise CloudGeneratedArtifactError(
            "Cloud artifact staging cannot replace the whole local directory"
        )
    return resolved


def _reset_stage_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def _run(label: str, command: Sequence[str]) -> None:
    print(f"[{label}] {' '.join(command)}", flush=True)
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode:
        raise CloudGeneratedArtifactError(
            f"{label} failed with exit code {result.returncode}"
        )


def _spec(specs: Sequence[GeneratorSpec], owner: str) -> GeneratorSpec:
    result = next((spec for spec in specs if spec.id == owner), None)
    if result is None:
        raise CloudGeneratedArtifactError(f"Unknown generated owner: {owner}")
    return result


def _copy_outputs(outputs: Iterable[str], stage: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in outputs:
        source = ROOT / relative
        if not source.is_file():
            raise CloudGeneratedArtifactError(
                f"Generated output is missing: {relative}"
            )
        destination = stage / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        result[relative] = _sha256(destination)
    return result


def _source_commit() -> str:
    expected = os.environ.get("CLOUD_GENERATED_SOURCE_SHA") or os.environ.get(
        "GITHUB_SHA"
    )
    observed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
    ).stdout.strip()
    if expected and expected != observed:
        raise CloudGeneratedArtifactError(
            "GitHub source SHA does not match the checked-out commit"
        )
    return observed


def _snapshot_metadata() -> dict[str, Any]:
    rules = json.loads((ROOT / "rules" / "manifest.json").read_text(encoding="utf-8"))
    cards = rules.get("card_data_snapshot") or {}
    return {
        "rules_effective_date": rules.get("effective_date"),
        "rules_source_sha256": rules.get("source_sha256"),
        "oracle_source_sha256": (cards.get("oracle_bulk") or {}).get("sha256"),
        "rulings_source_sha256": (cards.get("rulings_bulk") or {}).get("sha256"),
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run_owner(owner: str, stage_dir: str, database: str | None) -> dict[str, Any]:
    specs = load_manifest()
    selected = _spec(specs, owner)
    by_id = {spec.id: spec for spec in specs}
    for dependency in selected.depends_on:
        _run(f"dependency:{dependency}", check_command(by_id[dependency]))
    database_path = Path(database).resolve() if database else None
    command = write_command(
        selected,
        database=database_path,
        include_manual=False,
    )
    if command is None:
        raise CloudGeneratedArtifactError(
            f"Generated owner {owner} has no cloud-safe write command"
        )
    _run(owner, command)
    _run(f"check:{owner}", check_command(selected))

    stage = _safe_stage_directory(stage_dir)
    _reset_stage_directory(stage)
    hashes = _copy_outputs(selected.outputs, stage)
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "kind": "generated_owner",
        "owner": owner,
        "source_commit": _source_commit(),
        "source_tree_fingerprint": tracked_worktree_source_fingerprint(ROOT),
        "outputs": hashes,
        **_snapshot_metadata(),
    }
    _write_json(stage / "_cloud" / "owners" / f"{owner}.json", receipt)
    return receipt


def stage_bundle(stage_dir: str) -> dict[str, Any]:
    specs = load_manifest()
    stage = _safe_stage_directory(stage_dir)
    _reset_stage_directory(stage)
    hashes = _copy_outputs(all_outputs(specs), stage)
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "kind": "generated_bundle",
        "source_commit": _source_commit(),
        "source_tree_fingerprint": tracked_worktree_source_fingerprint(ROOT),
        "generator_count": len(specs),
        "output_count": len(hashes),
        "outputs": hashes,
        **_snapshot_metadata(),
    }
    _write_json(stage / "_cloud" / "bundle.json", receipt)
    return receipt


def install_bundle(
    bundle_dir: str,
    expected_commit: str | None,
    *,
    write_receipt: bool = True,
) -> dict[str, Any]:
    bundle = Path(bundle_dir).resolve()
    receipt_path = bundle / "_cloud" / "bundle.json"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CloudGeneratedArtifactError(
            "Downloaded cloud bundle has no valid receipt"
        ) from exc
    specs = load_manifest()
    expected_outputs = set(all_outputs(specs))
    outputs = receipt.get("outputs")
    if (
        receipt.get("schema_version") != SCHEMA_VERSION
        or receipt.get("kind") != "generated_bundle"
        or not isinstance(outputs, dict)
        or set(outputs) != expected_outputs
    ):
        raise CloudGeneratedArtifactError(
            "Downloaded cloud bundle does not match the generated manifest"
        )
    if expected_commit and receipt.get("source_commit") != expected_commit:
        raise CloudGeneratedArtifactError(
            "Downloaded cloud bundle belongs to a different source commit"
        )
    current_commit = _source_commit()
    if receipt.get("source_commit") != current_commit:
        raise CloudGeneratedArtifactError(
            "Downloaded cloud bundle does not match the current HEAD"
        )

    changed: list[str] = []
    for relative in sorted(expected_outputs):
        source = bundle / relative
        if not source.is_file() or _sha256(source) != outputs[relative]:
            raise CloudGeneratedArtifactError(
                f"Downloaded cloud output is missing or corrupt: {relative}"
            )
        destination = ROOT / relative
        if not destination.is_file() or destination.read_bytes() != source.read_bytes():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            changed.append(relative)
    source_fingerprint = tracked_worktree_source_fingerprint(ROOT)
    if source_fingerprint != receipt.get("source_tree_fingerprint"):
        raise CloudGeneratedArtifactError(
            "Downloaded cloud bundle does not match the local source tree"
        )
    receipt_path = None
    if write_receipt:
        receipt_path, _ = write_finalization_receipt(
            specs,
            database=None,
            root=ROOT,
        )
    return {
        "ok": True,
        "source_commit": receipt["source_commit"],
        "installed_outputs": len(expected_outputs),
        "changed_outputs": changed,
        "finalization_receipt": str(receipt_path) if receipt_path else None,
    }


def main() -> int:
    require_supported_python()
    parser = argparse.ArgumentParser(
        description="Run, stage, or install governed cloud-generated artifacts"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    owner = subparsers.add_parser("run-owner")
    owner.add_argument("--owner", required=True)
    owner.add_argument("--stage-dir", required=True)
    owner.add_argument("--db")

    bundle = subparsers.add_parser("stage-bundle")
    bundle.add_argument("--stage-dir", required=True)

    install = subparsers.add_parser("install-bundle")
    install.add_argument("--bundle-dir", required=True)
    install.add_argument("--expected-commit", required=True)

    args = parser.parse_args()
    try:
        if args.command == "run-owner":
            result = run_owner(args.owner, args.stage_dir, args.db)
        elif args.command == "stage-bundle":
            result = stage_bundle(args.stage_dir)
        else:
            result = install_bundle(args.bundle_dir, args.expected_commit)
    except (CloudGeneratedArtifactError, OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
