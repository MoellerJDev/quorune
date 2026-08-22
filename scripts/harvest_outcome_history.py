from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping, Sequence

from quorune.util import stable_json


HARVEST_HISTORY_SCHEMA_VERSION = 1
HARVEST_HISTORY_ALGORITHM_VERSION = "git-corpus-receipt-delta-v1"
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_PROGRAM_PATH = "coverage/card-program-coverage-commander.json"
_FRONTIER_PATH = "coverage/card-unlock-frontier.json.gz"


class HarvestOutcomeHistoryError(ValueError):
    pass


def _hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def _git(root: Path, *args: str, check: bool = True) -> bytes:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise HarvestOutcomeHistoryError(
            "Unable to read immutable harvest provenance from Git"
        ) from exc
    return completed.stdout


def _canonical_commit(root: Path, value: Any, label: str) -> str:
    commit = str(value or "")
    if not _COMMIT.fullmatch(commit):
        raise HarvestOutcomeHistoryError(f"{label} must be a full Git commit")
    resolved = _git(root, "rev-parse", f"{commit}^{{commit}}").decode().strip()
    if resolved != commit:
        raise HarvestOutcomeHistoryError(f"{label} is not canonical")
    return commit


def _blob(root: Path, commit: str, path: str) -> tuple[str, bytes]:
    oid = _git(root, "rev-parse", f"{commit}:{path}").decode().strip()
    raw = _git(root, "show", f"{commit}:{path}")
    return oid, raw


def _json_object(raw: bytes, label: str, *, compressed: bool = False) -> dict:
    try:
        payload = gzip.decompress(raw) if compressed else raw
        value = json.loads(payload)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HarvestOutcomeHistoryError(f"Invalid {label}") from exc
    if not isinstance(value, dict):
        raise HarvestOutcomeHistoryError(f"{label} must be an object")
    return value


def _receipt(root: Path, commit: str) -> dict[str, Any]:
    program_oid, program_raw = _blob(root, commit, _PROGRAM_PATH)
    frontier_oid, frontier_raw = _blob(root, commit, _FRONTIER_PATH)
    program = _json_object(program_raw, _PROGRAM_PATH)
    frontier = _json_object(frontier_raw, _FRONTIER_PATH, compressed=True)
    program_snapshot = program.get("card_data_snapshot")
    frontier_snapshot = frontier.get("card_data_snapshot")
    identity_fields = {
        "schema_version",
        "card_count",
        "oracle_source_sha256",
        "rulings_source_sha256",
        "scryfall_oracle_updated_at",
        "scryfall_rulings_updated_at",
    }
    if (
        not isinstance(program_snapshot, Mapping)
        or not isinstance(frontier_snapshot, Mapping)
        or {
            field: program_snapshot.get(field) for field in identity_fields
        }
        != {field: frontier_snapshot.get(field) for field in identity_fields}
        or int(program.get("cards_considered") or -1)
        != int(frontier.get("cards_considered") or -2)
        or program.get("compiler_version") is None
        or not frontier.get("fingerprint")
    ):
        raise HarvestOutcomeHistoryError(
            f"Corpus receipts disagree at commit {commit}"
        )
    cards = frontier.get("cards")
    if not isinstance(cards, list):
        raise HarvestOutcomeHistoryError(
            f"Frontier receipt lacks complete cards at commit {commit}"
        )
    exact_abilities = 0
    for card in cards:
        if not isinstance(card, Mapping):
            raise HarvestOutcomeHistoryError("Frontier card rows must be objects")
        value = card.get("exact_ability_count")
        if type(value) is not int or value < 0:
            raise HarvestOutcomeHistoryError(
                "Frontier exact ability counts must be nonnegative integers"
            )
        exact_abilities += value
    statuses = program.get("status_counts")
    if not isinstance(statuses, Mapping):
        raise HarvestOutcomeHistoryError("Program receipt lacks status counts")
    trusted = statuses.get("trusted")
    residuals = program.get("material_residuals")
    if (
        type(trusted) is not int
        or trusted < 0
        or type(residuals) is not int
        or residuals < 0
    ):
        raise HarvestOutcomeHistoryError("Program receipt counts are malformed")
    return {
        "commit": commit,
        "card_program_blob_oid": program_oid,
        "card_program_sha256": hashlib.sha256(program_raw).hexdigest(),
        "frontier_blob_oid": frontier_oid,
        "frontier_sha256": hashlib.sha256(frontier_raw).hexdigest(),
        "frontier_fingerprint": str(frontier["fingerprint"]),
        "compiler_version": str(program["compiler_version"]),
        "card_program_schema_version": int(
            program["card_program_schema_version"]
        ),
        "card_data_snapshot": {
            field: program_snapshot.get(field) for field in sorted(identity_fields)
        },
        "cards_considered": int(program["cards_considered"]),
        "trusted_programs": trusted,
        "exact_abilities": exact_abilities,
        "material_residuals": residuals,
    }


def _provenance_rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise HarvestOutcomeHistoryError("Harvest provenance must be an array")
    rows = list(value)
    if any(not isinstance(row, Mapping) for row in rows):
        raise HarvestOutcomeHistoryError("Harvest provenance rows must be objects")
    return rows


def build_harvest_outcome_history(
    root: str | Path,
    provenance: Any,
) -> dict[str, Any]:
    repository = Path(root).resolve()
    expected = {
        "bundle_id",
        "candidate_ids",
        "expected_complete_card_gain",
        "base_commit",
        "head_commit",
    }
    seen_bundles: set[str] = set()
    entries: list[dict[str, Any]] = []
    for index, row in enumerate(_provenance_rows(provenance)):
        if set(row) != expected:
            raise HarvestOutcomeHistoryError(
                f"Harvest provenance row {index} has an invalid shape"
            )
        bundle_id = str(row.get("bundle_id") or "")
        candidate_ids = [str(value) for value in row.get("candidate_ids", [])]
        expected_gain = row.get("expected_complete_card_gain")
        if (
            not bundle_id.startswith("bundle:")
            or bundle_id in seen_bundles
            or not candidate_ids
            or candidate_ids != sorted(set(candidate_ids))
            or type(expected_gain) is not int
            or expected_gain < 0
        ):
            raise HarvestOutcomeHistoryError(
                "Harvest provenance identity and prediction fields are invalid"
            )
        seen_bundles.add(bundle_id)
        base_commit = _canonical_commit(
            repository, row.get("base_commit"), "base_commit"
        )
        head_commit = _canonical_commit(
            repository, row.get("head_commit"), "head_commit"
        )
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", base_commit, head_commit],
            cwd=repository,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if ancestor.returncode != 0 or base_commit == head_commit:
            raise HarvestOutcomeHistoryError(
                "Harvest base must be a strict ancestor of its head"
            )
        base = _receipt(repository, base_commit)
        head = _receipt(repository, head_commit)
        if (
            base["card_data_snapshot"] != head["card_data_snapshot"]
            or base["cards_considered"] != head["cards_considered"]
        ):
            raise HarvestOutcomeHistoryError(
                "Harvest corpus receipts must use one pinned card snapshot"
            )
        deltas = {
            "actual_complete_card_gain": (
                head["trusted_programs"] - base["trusted_programs"]
            ),
            "actual_exact_ability_gain": (
                head["exact_abilities"] - base["exact_abilities"]
            ),
            "actual_material_residual_reduction": (
                base["material_residuals"] - head["material_residuals"]
            ),
        }
        if any(type(value) is not int or value < 0 for value in deltas.values()):
            raise HarvestOutcomeHistoryError(
                "Harvest corpus deltas must be monotonic and nonnegative"
            )
        entries.append(
            {
                "bundle_id": bundle_id,
                "candidate_ids": candidate_ids,
                "expected_complete_card_gain": expected_gain,
                "base_receipt": base,
                "head_receipt": head,
                **deltas,
            }
        )
    payload: dict[str, Any] = {
        "schema_version": HARVEST_HISTORY_SCHEMA_VERSION,
        "algorithm_version": HARVEST_HISTORY_ALGORITHM_VERSION,
        "entries": entries,
        "outcome_basis": (
            "Actual outcomes are derived from immutable Git blob receipts for "
            "the pinned Commander CardProgram corpus and card-unlock frontier."
        ),
    }
    payload["fingerprint"] = _hash(payload)
    return payload


__all__ = [
    "build_harvest_outcome_history",
    "HARVEST_HISTORY_ALGORITHM_VERSION",
    "HARVEST_HISTORY_SCHEMA_VERSION",
    "HarvestOutcomeHistoryError",
]
