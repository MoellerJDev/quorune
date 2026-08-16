from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .util import stable_json


WORK_SELECTION_SCHEMA_VERSION = 1
_CANDIDATE_CLASSES = {
    "ci_correctness",
    "replay_privacy_defect",
    "architecture_owner_extraction",
    "runtime_oracle_removal",
    "interaction_assurance",
    "architecture_debt",
    "rules_foundation",
    "compiler_harvest",
    "card_family",
}
_REQUIRED_CANDIDATE_FIELDS = {
    "candidate_id",
    "candidate_class",
    "universal_subsystem",
    "reusable_piece_ids",
    "rules_dependency_ids",
    "compiler_readiness",
    "runtime_readiness",
    "assurance_readiness",
    "affected_commander_cards",
    "sole_blocker_cards",
    "one_additional_blocker_cards",
    "two_additional_blocker_cards",
    "expected_exact_ability_gain",
    "expected_complete_card_gain",
    "expected_material_residual_reduction",
    "interaction_debt_introduced",
    "architecture_debt_removed",
    "direct_write_migration",
    "engine_extraction",
    "runtime_oracle_text_removal",
    "estimated_effort",
    "reranking_reason",
    "eligible",
    "priority_within_class",
}
_REASON_FIELD = "reason"
_STATUS_FIELD = "status"


class WorkSelectionError(ValueError):
    pass


def _hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WorkSelectionError(f"{label} must be an object")
    return value


def _nonnegative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise WorkSelectionError(f"{label} must be a nonnegative integer")
    return value


def _validated_policy(policy: Mapping[str, Any]) -> dict[str, Any]:
    if int(policy.get("policy_version") or 0) != 1:
        raise WorkSelectionError("Unsupported work-selection policy")
    priority_classes = [str(value) for value in policy.get("priority_classes", [])]
    if (
        not priority_classes
        or len(priority_classes) != len(set(priority_classes))
        or set(priority_classes) != _CANDIDATE_CLASSES
    ):
        raise WorkSelectionError(
            "Work-selection priority classes must name every known class once"
        )
    assurance = _mapping(
        policy.get("interaction_assurance"), "interaction_assurance"
    )
    starting_uncovered = _nonnegative_int(
        assurance.get("starting_uncovered_high_risk_pairs"),
        "starting_uncovered_high_risk_pairs",
    )
    coverage = _mapping(policy.get("coverage_family"), "coverage_family")
    minimum_gain = _nonnegative_int(
        coverage.get("minimum_complete_card_gain"),
        "minimum_complete_card_gain",
    )
    minimum_ability_gain = _nonnegative_int(
        coverage.get("minimum_exact_ability_gain"),
        "minimum_exact_ability_gain",
    )
    minimum_residual_reduction = _nonnegative_int(
        coverage.get("minimum_material_residual_reduction"),
        "minimum_material_residual_reduction",
    )
    candidate_limit = _nonnegative_int(
        coverage.get("candidate_limit"), "candidate_limit"
    )
    rank_order = [str(value) for value in coverage.get("rank_order", [])]
    expected_rank_fields = {
        "expected_exact_ability_gain",
        "expected_complete_card_gain",
        "expected_material_residual_reduction",
    }
    if (
        minimum_gain < 50
        or minimum_ability_gain < 100
        or minimum_residual_reduction < 100
        or candidate_limit < 1
        or len(rank_order) != len(set(rank_order))
        or set(rank_order) != expected_rank_fields
    ):
        raise WorkSelectionError(
            "Coverage work must declare the card, ability, residual, ranking, and candidate thresholds"
        )
    excluded_efforts = {
        str(value) for value in coverage.get("excluded_efforts", []) if value
    }
    history = list(policy.get("reviewed_rerank_history", []))
    history_ids: set[str] = set()
    for index, raw in enumerate(history):
        row = _mapping(raw, f"reviewed_rerank_history[{index}]")
        expected = {"candidate_id", "selected_over", _REASON_FIELD}
        if set(row) != expected:
            raise WorkSelectionError(
                "Reviewed rerank history entries have an invalid shape"
            )
        candidate_id = str(row.get("candidate_id") or "")
        selected_over = str(row.get("selected_over") or "")
        reason = str(row.get(_REASON_FIELD) or "")
        if not candidate_id or not selected_over or not reason:
            raise WorkSelectionError(
                "Reviewed rerank history entries must be complete"
            )
        if candidate_id in history_ids:
            raise WorkSelectionError(
                f"Duplicate reviewed rerank history entry: {candidate_id}"
            )
        history_ids.add(candidate_id)
    return {
        "policy_version": 1,
        "priority_classes": priority_classes,
        "starting_uncovered_high_risk_pairs": starting_uncovered,
        "minimum_complete_card_gain": minimum_gain,
        "minimum_exact_ability_gain": minimum_ability_gain,
        "minimum_material_residual_reduction": minimum_residual_reduction,
        "candidate_limit": candidate_limit,
        "coverage_rank_order": rank_order,
        "excluded_efforts": excluded_efforts,
        "reviewed_rerank_history": history,
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise WorkSelectionError(f"Missing work-selection input: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkSelectionError(f"Invalid work-selection input: {path}") from exc
    if not isinstance(value, dict):
        raise WorkSelectionError(f"Work-selection input must be an object: {path}")
    return value


def _read_gzip_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise WorkSelectionError(f"Missing work-selection input: {path}")
    try:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkSelectionError(f"Invalid work-selection input: {path}") from exc
    if not isinstance(value, dict):
        raise WorkSelectionError(f"Work-selection input must be an object: {path}")
    return value


def load_work_selection_inputs(root: str | Path) -> dict[str, Any]:
    repository = Path(root)
    return {
        "architecture_audit": _read_json(
            repository / "coverage" / "architecture-audit.json"
        ),
        "card_unlock_frontier": _read_gzip_json(
            repository / "coverage" / "card-unlock-frontier.json.gz"
        ),
        "compact_ci_dependencies": _read_json(
            repository / "coverage" / "compact-ci-card-dependencies.json"
        ),
        "platform_readiness": _read_json(
            repository / "coverage" / "platform-readiness.json"
        ),
        "reusable_piece_delta": _read_json(
            repository / "coverage" / "reusable-piece-delta.json"
        ),
    }


def _readiness(status: str, evidence: str) -> dict[str, str]:
    return {_STATUS_FIELD: status, "evidence": evidence}


def _debt(value: int | None, basis: str) -> dict[str, Any]:
    return {"expected_count": value, "basis": basis}


def _candidate(
    *,
    candidate_id: str,
    candidate_class: str,
    universal_subsystem: str,
    compiler_readiness: Mapping[str, str],
    runtime_readiness: Mapping[str, str],
    assurance_readiness: Mapping[str, str],
    estimated_effort: str,
    reranking_reason: str,
    eligible: bool,
    reusable_piece_ids: Sequence[str] = (),
    rules_dependency_ids: Sequence[str] = (),
    affected_commander_cards: int | None = 0,
    sole_blocker_cards: int | None = 0,
    one_additional_blocker_cards: int | None = 0,
    two_additional_blocker_cards: int | None = 0,
    expected_exact_ability_gain: int | None = 0,
    expected_complete_card_gain: int | None = 0,
    expected_material_residual_reduction: int | None = 0,
    interaction_debt_introduced: Mapping[str, Any] | None = None,
    architecture_debt_removed: Mapping[str, Any] | None = None,
    direct_write_migration: Mapping[str, Any] | None = None,
    engine_extraction: Mapping[str, Any] | None = None,
    runtime_oracle_text_removal: Mapping[str, Any] | None = None,
    priority_within_class: int = 0,
) -> dict[str, Any]:
    if candidate_class not in _CANDIDATE_CLASSES:
        raise WorkSelectionError(f"Unknown candidate class: {candidate_class}")
    row = {
        "candidate_id": candidate_id,
        "candidate_class": candidate_class,
        "universal_subsystem": universal_subsystem,
        "reusable_piece_ids": sorted({str(value) for value in reusable_piece_ids}),
        "rules_dependency_ids": sorted({str(value) for value in rules_dependency_ids}),
        "compiler_readiness": dict(compiler_readiness),
        "runtime_readiness": dict(runtime_readiness),
        "assurance_readiness": dict(assurance_readiness),
        "affected_commander_cards": affected_commander_cards,
        "sole_blocker_cards": sole_blocker_cards,
        "one_additional_blocker_cards": one_additional_blocker_cards,
        "two_additional_blocker_cards": two_additional_blocker_cards,
        "expected_exact_ability_gain": expected_exact_ability_gain,
        "expected_complete_card_gain": expected_complete_card_gain,
        "expected_material_residual_reduction": expected_material_residual_reduction,
        "interaction_debt_introduced": dict(interaction_debt_introduced or {}),
        "architecture_debt_removed": dict(architecture_debt_removed or {}),
        "direct_write_migration": dict(direct_write_migration or _debt(0, "none")),
        "engine_extraction": dict(engine_extraction or _debt(0, "none")),
        "runtime_oracle_text_removal": dict(
            runtime_oracle_text_removal or _debt(0, "none")
        ),
        "estimated_effort": estimated_effort,
        "reranking_reason": reranking_reason,
        "eligible": bool(eligible),
        "priority_within_class": _nonnegative_int(
            priority_within_class, "priority_within_class"
        ),
    }
    if set(row) != _REQUIRED_CANDIDATE_FIELDS:
        raise WorkSelectionError("Work-selection candidate shape is incomplete")
    return row


def _runtime_oracle_candidates(
    capsules: Sequence[Mapping[str, Any]], prohibited: int
) -> list[dict[str, Any]]:
    affected_capsules = [
        row
        for row in capsules
        if int(row.get("prohibited_runtime_oracle_text_accesses") or 0) > 0
    ]
    candidates = []
    attributed_accesses = 0
    for capsule in affected_capsules:
        subsystem_id = str(capsule.get("id") or "")
        count = _nonnegative_int(
            capsule.get("prohibited_runtime_oracle_text_accesses"),
            f"{subsystem_id} prohibited runtime text count",
        )
        attributed_accesses += count
        candidates.append(
            _candidate(
                candidate_id=f"architecture:runtime-oracle-text-removal:{subsystem_id}",
                candidate_class="runtime_oracle_removal",
                universal_subsystem=subsystem_id,
                reusable_piece_ids=capsule.get("reusable_pieces", []),
                compiler_readiness=_readiness(
                    "partial",
                    "typed compiler inputs exist but this runtime owner still inspects prose",
                ),
                runtime_readiness=_readiness(
                    "blocked",
                    f"{count} subsystem accesses from {prohibited} prohibited total",
                ),
                assurance_readiness=_readiness(
                    "required",
                    "the bounded migration needs focused replay and interaction evidence",
                ),
                estimated_effort="small" if count <= 3 else "medium",
                reranking_reason=(
                    f"{count} prohibited runtime-text accesses remain in the existing "
                    f"{subsystem_id} typed owner and outrank card expansion."
                ),
                eligible=True,
                architecture_debt_removed={
                    "prohibited_runtime_text_accesses": count
                },
                runtime_oracle_text_removal=_debt(
                    count, "generated subsystem architecture capsule"
                ),
                priority_within_class=1_000 + count,
            )
        )
    unattributed = prohibited - attributed_accesses
    if unattributed < 0:
        raise WorkSelectionError(
            "Subsystem runtime-text counts exceed the architecture total"
        )
    if unattributed:
        candidates.append(
            _candidate(
                candidate_id="architecture:runtime-oracle-text-subsystem-attribution",
                candidate_class="runtime_oracle_removal",
                universal_subsystem="architecture_runtime_text_inventory",
                compiler_readiness=_readiness(
                    "not_applicable", "architecture attribution"
                ),
                runtime_readiness=_readiness(
                    "blocked",
                    f"{unattributed} of {prohibited} prohibited accesses lack a bounded "
                    "subsystem capsule",
                ),
                assurance_readiness=_readiness(
                    "required",
                    "attribute each access before selecting its behavioral migration",
                ),
                estimated_effort="medium",
                reranking_reason=(
                    "Complete subsystem attribution after the already bounded runtime-text "
                    "slices; do not treat the remainder as one implementation batch."
                ),
                eligible=True,
                architecture_debt_removed={
                    "unattributed_prohibited_runtime_text_accesses": unattributed
                },
                runtime_oracle_text_removal=_debt(
                    unattributed,
                    "generated total minus subsystem-attributed accesses",
                ),
                priority_within_class=1,
            )
        )
    return candidates


def _architecture_candidates(
    architecture_report: Mapping[str, Any],
) -> list[dict[str, Any]]:
    architecture = _mapping(
        architecture_report.get("architecture"), "architecture audit"
    )
    capsules = list(architecture.get("subsystem_capsules", []))
    missing = [
        str(row.get("id") or row.get("subsystem") or "")
        for row in architecture.get("missing_dedicated_owners", [])
    ]
    missing = sorted(value for value in missing if value)
    runtime = _mapping(
        architecture.get("runtime_oracle_text_access"), "runtime text inventory"
    )
    prohibited = _nonnegative_int(
        runtime.get("prohibited_runtime_interpretation_count"),
        "prohibited runtime interpretation count",
    )
    ownership = _mapping(
        architecture.get("direct_game_state_write_ownership"),
        "direct write ownership",
    )
    engine_writes = _nonnegative_int(
        ownership.get("writes_in_commander_engine"), "engine write count"
    )
    grandfathered = _nonnegative_int(
        ownership.get("grandfathered_engine_writes"),
        "grandfathered engine write count",
    )
    card_named = architecture.get("card_named_helpers")
    card_named_count = len(card_named) if isinstance(card_named, list) else int(bool(card_named))
    card_specific = _mapping(
        architecture.get("semantic_operation_branches"),
        "semantic operation inventory",
    ).get("card_specific_operation_branch_occurrences", {})
    card_specific_count = sum(
        int(value) for value in _mapping(card_specific, "card-specific operations").values()
    )
    runtime_candidates = _runtime_oracle_candidates(capsules, prohibited)
    return [
        _candidate(
            candidate_id="architecture:dedicated-owner-extraction",
            candidate_class="architecture_owner_extraction",
            universal_subsystem=",".join(missing) or "all_declared_subsystems",
            compiler_readiness=_readiness("not_applicable", "ownership boundary"),
            runtime_readiness=_readiness(
                "blocked" if missing else "complete",
                f"{len(missing)} missing dedicated owners",
            ),
            assurance_readiness=_readiness(
                "required" if missing else "complete",
                "owner migrations require replay, privacy, and interaction evidence",
            ),
            estimated_effort="large" if missing else "complete",
            reranking_reason=(
                "Missing authoritative owners outrank card expansion."
                if missing
                else "All declared dedicated-owner gaps are resolved."
            ),
            eligible=bool(missing),
            architecture_debt_removed={"missing_dedicated_owners": len(missing)},
            engine_extraction=_debt(
                None if missing else 0,
                "must be measured from the selected owner capsule",
            ),
        ),
        *runtime_candidates,
        _candidate(
            candidate_id="architecture:engine-mutation-and-specificity-debt",
            candidate_class="architecture_debt",
            universal_subsystem="commander_engine_compatibility_facade",
            compiler_readiness=_readiness("not_applicable", "architecture migration"),
            runtime_readiness=_readiness(
                "partial" if grandfathered or card_named_count or card_specific_count else "complete",
                "typed owners exist but legacy engine authority remains",
            ),
            assurance_readiness=_readiness(
                "required",
                "migrations require exact replay and subsystem interaction evidence",
            ),
            estimated_effort="large",
            reranking_reason=(
                f"{grandfathered} grandfathered engine writes, {card_named_count} card-named "
                f"helpers, and {card_specific_count} card-specific operation branches remain."
            ),
            eligible=bool(grandfathered or card_named_count or card_specific_count),
            architecture_debt_removed={
                "grandfathered_engine_writes": grandfathered,
                "card_named_helpers": card_named_count,
                "card_specific_operation_branches": card_specific_count,
            },
            direct_write_migration=_debt(
                grandfathered, "generated direct-write ownership inventory"
            ),
            engine_extraction=_debt(
                engine_writes, "current CommanderEngine direct-write inventory"
            ),
        ),
    ]


def _system_candidates(
    compact: Mapping[str, Any],
    readiness: Mapping[str, Any],
    reusable_delta: Mapping[str, Any],
    *,
    assurance_baseline: int,
) -> list[dict[str, Any]]:
    compact_closed = compact.get("closed") is True
    validation = _mapping(readiness.get("validation"), "platform validation")
    replay = str(validation.get("replay") or "")
    privacy = str(validation.get("privacy") or "")
    replay_privacy_closed = replay.startswith("pass") and privacy.startswith("pass")
    interaction = _mapping(
        reusable_delta.get("interaction_coverage"), "interaction coverage"
    )
    applicable = _nonnegative_int(
        interaction.get("applicable_high_risk_pairs"), "applicable high-risk pairs"
    )
    covered = _nonnegative_int(
        interaction.get("covered_high_risk_pairs"), "covered high-risk pairs"
    )
    if covered > applicable:
        raise WorkSelectionError("Covered high-risk pairs exceed applicable pairs")
    uncovered = applicable - covered
    assurance_gate_open = uncovered > assurance_baseline
    return [
        _candidate(
            candidate_id="ci:compact-card-dependency-closure",
            candidate_class="ci_correctness",
            universal_subsystem="deterministic_ci_card_data",
            compiler_readiness=_readiness("not_applicable", "CI dependency closure"),
            runtime_readiness=_readiness(
                "complete" if compact_closed else "blocked",
                f"closed={compact_closed}; {compact.get('card_count', 0)} cards and "
                f"{compact.get('requirements_discovered', 0)} requirements",
            ),
            assurance_readiness=_readiness(
                "complete" if compact_closed else "blocked",
                "canonical compact dependency validator",
            ),
            estimated_effort="complete" if compact_closed else "medium",
            reranking_reason=(
                "Compact CI dependency coverage is closed."
                if compact_closed
                else "A deterministic CI omission outranks feature work."
            ),
            eligible=not compact_closed,
        ),
        _candidate(
            candidate_id="correctness:replay-privacy-recovery",
            candidate_class="replay_privacy_defect",
            universal_subsystem="replay_and_projection",
            compiler_readiness=_readiness("not_applicable", "runtime correctness"),
            runtime_readiness=_readiness(
                "complete" if replay_privacy_closed else "blocked",
                f"replay={replay}; privacy={privacy}",
            ),
            assurance_readiness=_readiness(
                "complete" if replay_privacy_closed else "blocked",
                "generated platform validation",
            ),
            estimated_effort="complete" if replay_privacy_closed else "unknown",
            reranking_reason=(
                "No current generated replay or privacy defect is recorded."
                if replay_privacy_closed
                else "Replay or hidden-information correctness outranks feature work."
            ),
            eligible=not replay_privacy_closed,
        ),
        _candidate(
            candidate_id="assurance:critical-interaction-recovery",
            candidate_class="interaction_assurance",
            universal_subsystem="cross_owner_interactions",
            compiler_readiness=_readiness("not_applicable", "behavioral assurance"),
            runtime_readiness=_readiness("implemented", "existing typed owners"),
            assurance_readiness=_readiness(
                "blocked" if assurance_gate_open else "exit_gate_satisfied",
                f"{covered}/{applicable} covered; {uncovered} uncovered; "
                f"starting baseline {assurance_baseline}",
            ),
            estimated_effort="medium" if assurance_gate_open else "ongoing",
            reranking_reason=(
                "Uncovered high-risk interactions remain above the verified "
                "stabilization baseline."
                if assurance_gate_open
                else (
                    "The stabilization exit gate is satisfied and no uncovered "
                    "high-risk interaction debt remains."
                    if uncovered == 0
                    else "The stabilization exit gate is satisfied at or below "
                    "the configured baseline, though uncovered high-risk "
                    "interaction debt remains."
                )
            ),
            eligible=assurance_gate_open,
            interaction_debt_introduced={
                "applicable_high_risk_pairs": applicable,
                "covered_high_risk_pairs": covered,
                "uncovered_high_risk_pairs": uncovered,
                "starting_uncovered_high_risk_pairs": assurance_baseline,
            },
        ),
    ]


def _rules_candidate(selected_batch: Mapping[str, Any]) -> dict[str, Any]:
    rules = list(selected_batch.get("rules", []))
    return _candidate(
        candidate_id=f"rules:{selected_batch.get('batch_id') or 'selected-batch'}",
        candidate_class="rules_foundation",
        universal_subsystem=str(selected_batch.get("subsystem_id") or "rules"),
        reusable_piece_ids=selected_batch.get("target_capability_ids", []),
        rules_dependency_ids=selected_batch.get("rule_ids", []),
        compiler_readiness=_readiness(
            "partial", "selected dependency-ready bounded rules batch"
        ),
        runtime_readiness=_readiness(
            "partial",
            f"{len(rules)} selected blocked behavioral rule records",
        ),
        assurance_readiness=_readiness(
            "planned",
            f"{len(selected_batch.get('executable_test_ids', []))} existing test identities",
        ),
        affected_commander_cards=None,
        sole_blocker_cards=None,
        one_additional_blocker_cards=None,
        two_additional_blocker_cards=None,
        expected_exact_ability_gain=None,
        expected_complete_card_gain=None,
        expected_material_residual_reduction=None,
        interaction_debt_introduced={
            _STATUS_FIELD: "must_be_measured_before_implementation"
        },
        estimated_effort="medium",
        reranking_reason=(
            "The rules queue remains dependency-ready, but correctness, runtime-text, "
            "owner, and assurance gates may rank ahead of its unknown card gain."
        ),
        eligible=True,
    )


def _frontier_candidates(
    frontier: Mapping[str, Any], policy: Mapping[str, Any]
) -> list[dict[str, Any]]:
    candidates = []
    for row in frontier.get("family_candidates", []):
        complete_gain = int(row.get("expected_exact_card_gain") or 0)
        ability_gain = int(row.get("expected_exact_ability_gain") or 0)
        residual_reduction = int(
            row.get("expected_material_residual_gain") or 0
        )
        if (
            complete_gain < int(policy["minimum_complete_card_gain"])
            and ability_gain < int(policy["minimum_exact_ability_gain"])
            and residual_reduction
            < int(policy["minimum_material_residual_reduction"])
        ):
            continue
        if str(row.get("estimated_effort") or "") in policy["excluded_efforts"]:
            continue
        family_id = str(row.get("family_id") or "")
        if family_id.startswith("effect_clause:") or family_id.startswith(
            "activated_effect:"
        ):
            candidate_class = "compiler_harvest"
        elif family_id.startswith("keyword_dependency:"):
            candidate_class = "card_family"
        else:
            candidate_class = "rules_foundation"
        prerequisites = [str(value) for value in row.get("prerequisites", [])]
        candidates.append(
            _candidate(
                candidate_id=f"frontier:{family_id}",
                candidate_class=candidate_class,
                universal_subsystem=str(row.get("base_family") or family_id),
                rules_dependency_ids=prerequisites,
                compiler_readiness=_readiness(
                    str(row.get("runtime_compiler_readiness") or "unknown"),
                    "generated card-unlock frontier",
                ),
                runtime_readiness=_readiness(
                    "blocked_by_prerequisites" if prerequisites else "candidate",
                    f"{len(prerequisites)} recorded prerequisites",
                ),
                assurance_readiness=_readiness(
                    "required_before_trust",
                    f"interaction risk={row.get('interaction_risk') or 'unknown'}",
                ),
                affected_commander_cards=int(row.get("affected_cards") or 0),
                sole_blocker_cards=int(row.get("sole_blocker_cards") or 0),
                one_additional_blocker_cards=int(
                    row.get("one_additional_blocker_cards") or 0
                ),
                two_additional_blocker_cards=int(
                    row.get("two_additional_blocker_cards") or 0
                ),
                expected_exact_ability_gain=int(
                    ability_gain
                ),
                expected_complete_card_gain=complete_gain,
                expected_material_residual_reduction=int(
                    residual_reduction
                ),
                interaction_debt_introduced={
                    _STATUS_FIELD: "unmeasured",
                    "risk": str(row.get("interaction_risk") or "unknown"),
                },
                estimated_effort=str(row.get("estimated_effort") or "unknown"),
                reranking_reason=(
                    "Blocked prerequisites keep this high-yield frontier behind ready work."
                    if prerequisites
                    else "Meets a post-stabilization card, exact-ability, or material-residual "
                    "harvest threshold but remains behind higher-priority correctness gates."
                ),
                eligible=not prerequisites,
            )
        )
        if len(candidates) >= int(policy["candidate_limit"]):
            break
    return candidates


def build_work_selection(
    *,
    selected_batch: Mapping[str, Any],
    policy: Mapping[str, Any],
    inputs: Mapping[str, Any],
) -> dict[str, Any]:
    validated = _validated_policy(policy)
    required_inputs = {
        "architecture_audit",
        "card_unlock_frontier",
        "compact_ci_dependencies",
        "platform_readiness",
        "reusable_piece_delta",
    }
    if set(inputs) != required_inputs:
        raise WorkSelectionError(
            "Work-selection inputs must be the canonical generated reports"
        )
    candidates = [
        *_system_candidates(
            _mapping(inputs["compact_ci_dependencies"], "compact CI report"),
            _mapping(inputs["platform_readiness"], "platform readiness"),
            _mapping(inputs["reusable_piece_delta"], "reusable-piece delta"),
            assurance_baseline=int(validated["starting_uncovered_high_risk_pairs"]),
        ),
        *_architecture_candidates(
            _mapping(inputs["architecture_audit"], "architecture audit")
        ),
        _rules_candidate(selected_batch),
        *_frontier_candidates(
            _mapping(inputs["card_unlock_frontier"], "card-unlock frontier"),
            validated,
        ),
    ]
    ids = [str(row["candidate_id"]) for row in candidates]
    if len(ids) != len(set(ids)):
        raise WorkSelectionError("Work-selection candidate ids must be unique")
    priorities = {
        candidate_class: index
        for index, candidate_class in enumerate(validated["priority_classes"])
    }
    candidates.sort(
        key=lambda row: (
            not bool(row["eligible"]),
            priorities[str(row["candidate_class"])],
            -int(row["priority_within_class"]),
            *(
                -int(row[field] or 0)
                for field in validated["coverage_rank_order"]
            ),
            str(row["candidate_id"]),
        )
    )
    selected = next((row for row in candidates if row["eligible"]), None)
    for index, row in enumerate(candidates, start=1):
        row["rank"] = index
        if row is selected:
            selection_state = "selected"
        elif row["eligible"]:
            selection_state = "deferred"
        elif row["runtime_readiness"].get(_STATUS_FIELD) == "complete" or row[
            "assurance_readiness"
        ].get(_STATUS_FIELD) in {"complete", "exit_gate_satisfied"}:
            selection_state = "complete"
        else:
            selection_state = "blocked"
        row["selection_state"] = selection_state
    payload = {
        "schema_version": WORK_SELECTION_SCHEMA_VERSION,
        "policy_version": validated["policy_version"],
        "priority_classes": validated["priority_classes"],
        "source_fingerprints": {
            "architecture_audit": _hash(inputs["architecture_audit"]),
            "card_unlock_frontier": str(
                inputs["card_unlock_frontier"].get("fingerprint") or ""
            ),
            "compact_ci_dependencies": _hash(inputs["compact_ci_dependencies"]),
            "platform_readiness": _hash(inputs["platform_readiness"]),
            "reusable_piece_delta": str(
                inputs["reusable_piece_delta"].get("fingerprint") or ""
            ),
        },
        "selection_policy": {
            "starting_uncovered_high_risk_pairs": validated[
                "starting_uncovered_high_risk_pairs"
            ],
            "minimum_complete_card_gain": validated[
                "minimum_complete_card_gain"
            ],
            "minimum_exact_ability_gain": validated[
                "minimum_exact_ability_gain"
            ],
            "minimum_material_residual_reduction": validated[
                "minimum_material_residual_reduction"
            ],
            "coverage_rank_order": validated["coverage_rank_order"],
            "coverage_candidate_limit": validated["candidate_limit"],
            "excluded_efforts": sorted(validated["excluded_efforts"]),
        },
        "reviewed_rerank_history": validated["reviewed_rerank_history"],
        "selected_candidate_id": (
            str(selected["candidate_id"]) if selected is not None else None
        ),
        "serious_candidate_count": len(candidates),
        "eligible_candidate_count": sum(bool(row["eligible"]) for row in candidates),
        "candidates": candidates,
    }
    payload["fingerprint"] = _hash(payload)
    return payload


__all__ = [
    "WORK_SELECTION_SCHEMA_VERSION",
    "WorkSelectionError",
    "build_work_selection",
    "load_work_selection_inputs",
]
