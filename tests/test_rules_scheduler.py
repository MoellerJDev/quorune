from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from quorune.rules_corpus import (
    CORPUS_OPERATIONS,
    execute_rules_corpus_operation,
    rules_next,
)
from quorune.rules_scheduler import (
    RulesSchedulerError,
    build_rules_dependency_queue,
    build_rules_dependency_queue_from_root,
    load_rules_dependency_queue,
    rules_dependency_queue_errors,
)
from quorune.work_selection import (
    WorkSelectionError,
    build_work_selection,
    load_work_selection_inputs,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _reviewed_frontier_comparisons(inputs):
    frontier = inputs["card_unlock_frontier"]["family_candidates"]
    family_ids = {"effect_clause:destroy-target"}
    family_ids.update(
        selected_over.removeprefix("frontier:")
        for row in _json("platform/rules-subsystems.json")[
            "work_selection"
        ]["reviewed_rerank_history"]
        if (selected_over := str(row["selected_over"])).startswith(
            "frontier:"
        )
    )
    comparisons = []
    for row in frontier:
        family_id = str(row["family_id"])
        if family_id not in family_ids:
            continue
        comparison = deepcopy(row)
        if family_id != "effect_clause:destroy-target":
            comparison["prerequisites"] = [
                *comparison.get("prerequisites", []),
                "fixture:reviewed-rerank-context",
            ]
        comparisons.append(comparison)
    if {row["family_id"] for row in comparisons} != family_ids:
        raise AssertionError(
            "Synthetic scheduler inputs must preserve reviewed frontier "
            "comparisons"
        )
    return comparisons


def _with_dependency_ready_compiler_harvest(inputs):
    updated = deepcopy(inputs)
    updated["card_unlock_frontier"]["family_candidates"] = [
        {
            "family_id": "effect_clause:fixture-harvest",
            "base_family": "effect_clause:fixture-harvest",
            "expected_exact_card_gain": 50,
            "estimated_effort": "medium",
            "prerequisites": [],
            "runtime_compiler_readiness": "missing_lowering",
            "affected_cards": 60,
            "sole_blocker_cards": 50,
            "one_additional_blocker_cards": 10,
            "two_additional_blocker_cards": 0,
            "expected_exact_ability_gain": 60,
            "expected_material_residual_gain": 60,
            "interaction_risk": "medium",
        },
        *_reviewed_frontier_comparisons(updated),
    ]
    return updated


def _with_large_ability_compiler_harvest(inputs):
    updated = deepcopy(inputs)
    updated["card_unlock_frontier"]["family_candidates"] = [
        {
            "family_id": "effect_clause:large-ability-fixture",
            "base_family": "effect_clause:large-ability-fixture",
            "expected_exact_card_gain": 21,
            "estimated_effort": "large",
            "prerequisites": [],
            "runtime_compiler_readiness": "missing_lowering",
            "affected_cards": 521,
            "sole_blocker_cards": 21,
            "one_additional_blocker_cards": 109,
            "two_additional_blocker_cards": 86,
            "expected_exact_ability_gain": 130,
            "expected_material_residual_gain": 130,
            "interaction_risk": "high",
        },
        *_reviewed_frontier_comparisons(updated),
    ]
    return updated


class RulesSchedulerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rule_index = _json("rules/rule-index.json")
        cls.conformance = _json("rules/conformance-cases.json")
        cls.catalog = _json("platform/rules-subsystems.json")
        cls.capabilities = _json(
            "quorune/rules/capability-registry.json"
        )
        cls.queue = load_rules_dependency_queue(ROOT)
        cls.work_inputs = load_work_selection_inputs(ROOT)

    def test_generated_queue_is_fresh_and_source_pinned(self):
        self.assertEqual([], rules_dependency_queue_errors(ROOT))
        self.assertEqual(
            self.queue,
            build_rules_dependency_queue_from_root(ROOT),
        )
        self.assertEqual(
            self.rule_index["source_sha256"],
            self.queue["source_sha256"],
        )
        self.assertEqual(
            len(self.rule_index["rules"]),
            self.queue["summary"]["total_rules"],
        )

    def test_every_untrusted_or_unclassified_candidate_is_queued_once(self):
        expected = {
            str(case["rule_id"])
            for case in self.conformance["cases"]
            if case["status"] in {"blocked", "unreviewed"}
            and case["classification"]
            in {"behavioral", "unclassified"}
        }
        queued = [
            str(rule["rule_id"])
            for subsystem in self.queue["subsystems"]
            for rule in subsystem["rules"]
        ]
        self.assertEqual(len(expected), len(queued))
        self.assertEqual(len(queued), len(set(queued)))
        self.assertEqual(expected, set(queued))
        reviewed_blocked = sum(
            case["status"] == "blocked"
            and case["classification"] == "behavioral"
            for case in self.conformance["cases"]
        )
        review_required = sum(
            case["status"] == "unreviewed"
            and case["classification"]
            in {"behavioral", "unclassified"}
            for case in self.conformance["cases"]
        )
        self.assertEqual(
            reviewed_blocked,
            self.queue["summary"]["reviewed_behavioral_blocked"],
        )
        self.assertEqual(
            review_required,
            self.queue["summary"]["behavioral_review_required"],
        )

    def test_subsystems_cover_every_section_once_in_dependency_order(self):
        indexed_sections = {
            str(rule["section"]["id"])
            for rule in self.rule_index["rules"]
        }
        scheduled_sections = [
            str(section_id)
            for subsystem in self.queue["subsystems"]
            for section_id in subsystem["section_ids"]
        ]
        self.assertEqual(147, len(scheduled_sections))
        self.assertEqual(
            len(scheduled_sections), len(set(scheduled_sections))
        )
        self.assertEqual(indexed_sections, set(scheduled_sections))
        positions = {
            subsystem["subsystem_id"]: subsystem["schedule_order"]
            for subsystem in self.queue["subsystems"]
        }
        for subsystem in self.queue["subsystems"]:
            for dependency in subsystem["depends_on_subsystems"]:
                self.assertLess(
                    positions[dependency],
                    positions[subsystem["subsystem_id"]],
                )

    def test_each_queue_item_carries_required_work_context(self):
        for subsystem in self.queue["subsystems"]:
            self.assertTrue(subsystem["compiler_impact"])
            for rule in subsystem["rules"]:
                self.assertTrue(rule["active_profiles"])
                self.assertTrue(rule["compiler_impact"])
                self.assertIn(
                    rule["work_state"],
                    {
                        "behavioral_review_required",
                        "blocked_by_queued_rule",
                        "reviewed_behavioral_blocked",
                    },
                )
                self.assertIsInstance(
                    rule["implementation_components"], list
                )
                self.assertIsInstance(rule["executable_test_ids"], list)
                self.assertIsInstance(rule["dependency_rule_ids"], list)
                self.assertNotIn("text", rule)
                self.assertNotIn("short_summary", rule)

    def test_selected_batch_is_dependency_ready_and_cli_next_uses_it(self):
        selected = self.queue["selected_batch"]
        self.assertEqual(
            "counter-producer-replacement-closure",
            selected["batch_id"],
        )
        self.assertEqual(
            "replacement-prevention", selected["subsystem_id"]
        )
        self.assertEqual(
            {"614.16"},
            set(selected["rule_ids"]),
        )
        self.assertTrue(
            all(
                rule["reviewed"]
                and rule["classification"] == "behavioral"
                and rule["conformance_status"] == "blocked"
                and rule["work_state"] == "reviewed_behavioral_blocked"
                for rule in selected["rules"]
            )
        )
        next_batch = rules_next(ROOT, limit=20)
        self.assertEqual(
            self.queue["fingerprint"],
            next_batch["scheduler_fingerprint"],
        )
        self.assertEqual(
            selected["rule_ids"],
            [rule["rule_id"] for rule in next_batch["next"]],
        )
        self.assertEqual(
            self.queue["work_selection"]["selected_candidate_id"],
            next_batch["selected_work"]["candidate_id"],
        )
        self.assertNotIn(
            "reusable_piece_ids", next_batch["selected_work"]
        )
        selected_work = next(
            candidate
            for candidate in self.queue["work_selection"]["candidates"]
            if candidate["candidate_id"]
            == self.queue["work_selection"]["selected_candidate_id"]
        )
        self.assertEqual(
            len(selected_work["reusable_piece_ids"]),
            next_batch["selected_work"]["reusable_piece_count"],
        )
        self.assertIn("queue", CORPUS_OPERATIONS)
        self.assertEqual(
            self.queue["fingerprint"],
            execute_rules_corpus_operation(
                "queue", root=ROOT
            )["fingerprint"],
        )

    def test_catalog_rejects_duplicate_sections_dependency_cycles_and_bad_batch(self):
        duplicate = deepcopy(self.catalog)
        duplicate["subsystems"][1]["section_ids"].append("100")
        with self.assertRaisesRegex(
            RulesSchedulerError, "assigned more than once"
        ):
            build_rules_dependency_queue(
                self.rule_index,
                self.conformance,
                duplicate,
                self.capabilities,
            )

        completed_selection = deepcopy(self.catalog)
        completed_selection["selected_batch"] = {
            "batch_id": "typed-ordinary-cycling-activation",
            "subsystem_id": "keyword-abilities",
            "rule_ids": ["702.29a", "702.29b"],
            "target_capability_ids": ["activation.cycling.hand"],
            "exit_criteria": ["The bounded family is already complete."],
        }
        with self.assertRaisesRegex(
            RulesSchedulerError,
            "already complete",
        ):
            build_rules_dependency_queue(
                self.rule_index,
                self.conformance,
                completed_selection,
                self.capabilities,
                repository_root=ROOT,
            )

        cycle = deepcopy(self.catalog)
        cycle["subsystems"][0]["depends_on"] = ["formats"]
        with self.assertRaisesRegex(RulesSchedulerError, "cycle"):
            build_rules_dependency_queue(
                self.rule_index,
                self.conformance,
                cycle,
                self.capabilities,
            )

        trusted_selection = deepcopy(self.catalog)
        trusted_selection["selected_batch"]["rule_ids"] = ["614.5"]
        with self.assertRaisesRegex(
            RulesSchedulerError,
            "trusted, definition-only, or unknown rule",
        ):
            build_rules_dependency_queue(
                self.rule_index,
                self.conformance,
                trusted_selection,
                self.capabilities,
            )

    def test_cross_program_selection_ranks_correctness_before_card_gain(self):
        inputs = _with_dependency_ready_compiler_harvest(self.work_inputs)
        work = build_work_selection(
            selected_batch=self.queue["selected_batch"],
            policy=self.catalog["work_selection"],
            inputs=inputs,
        )
        selected = next(
            candidate
            for candidate in work["candidates"]
            if candidate["candidate_id"] == work["selected_candidate_id"]
        )
        runtime_total = int(
            inputs["architecture_audit"]["architecture"]
            ["runtime_oracle_text_access"]
            ["prohibited_runtime_interpretation_count"]
        )
        if runtime_total == 0:
            self.assertFalse(
                any(
                    candidate["candidate_class"]
                    == "runtime_oracle_removal"
                    for candidate in work["candidates"]
                )
            )
            assurance = next(
                candidate
                for candidate in work["candidates"]
                if candidate["candidate_id"]
                == "assurance:critical-interaction-recovery"
            )
            debt = assurance["interaction_debt_introduced"]
            gate_open = (
                debt["uncovered_high_risk_pairs"]
                > debt["starting_uncovered_high_risk_pairs"]
            )
            card_candidates = [
                candidate
                for candidate in work["candidates"]
                if candidate["candidate_class"]
                in {"compiler_harvest", "card_family"}
                and candidate["eligible"]
            ]
            self.assertTrue(card_candidates)
            if gate_open:
                self.assertEqual(assurance, selected)
                self.assertTrue(
                    all(
                        selected["rank"] < candidate["rank"]
                        for candidate in card_candidates
                    )
                )
            else:
                self.assertFalse(assurance["eligible"])
                self.assertEqual(
                    "exit_gate_satisfied",
                    assurance["assurance_readiness"]["status"],
                )
                self.assertIn(
                    selected["candidate_class"],
                    {"compiler_harvest", "card_family"},
                )
            return
        self.assertEqual("runtime_oracle_removal", selected["candidate_class"])
        self.assertNotEqual(
            "cross_subsystem_runtime_semantics",
            selected["universal_subsystem"],
        )
        selected_runtime_count = int(
            selected["runtime_oracle_text_removal"]["expected_count"]
        )
        self.assertGreater(selected_runtime_count, 0)
        if (
            selected["candidate_id"]
            == "architecture:runtime-oracle-text-subsystem-attribution"
        ):
            self.assertEqual(runtime_total, selected_runtime_count)
            self.assertEqual(
                "not_applicable", selected["compiler_readiness"]["status"]
            )
            self.assertIn(
                "do not treat the remainder as one implementation batch",
                selected["reranking_reason"],
            )
        else:
            runtime_candidates = [
                candidate
                for candidate in work["candidates"]
                if candidate["candidate_class"] == "runtime_oracle_removal"
            ]
            if len(runtime_candidates) == 1:
                self.assertEqual(
                    selected["candidate_id"],
                    runtime_candidates[0]["candidate_id"],
                )
                self.assertEqual(runtime_total, selected_runtime_count)
            else:
                self.assertLess(selected_runtime_count, runtime_total)
        self.assertGreater(selected["priority_within_class"], 0)
        card_candidates = [
            candidate
            for candidate in work["candidates"]
            if candidate["candidate_class"]
            in {"compiler_harvest", "card_family"}
            and candidate["eligible"]
        ]
        self.assertTrue(card_candidates)
        self.assertGreater(
            max(
                int(candidate["expected_complete_card_gain"] or 0)
                for candidate in card_candidates
            ),
            int(selected["expected_complete_card_gain"] or 0),
        )
        self.assertTrue(
            all(selected["rank"] < candidate["rank"] for candidate in card_candidates)
        )

    def test_assurance_exit_gate_accepts_baseline_and_resumes_card_harvest(self):
        inputs = _with_dependency_ready_compiler_harvest(self.work_inputs)
        interaction = inputs["reusable_piece_delta"]["interaction_coverage"]
        baseline = self.catalog["work_selection"]["interaction_assurance"][
            "starting_uncovered_high_risk_pairs"
        ]
        self.assertEqual(0, baseline)
        interaction["covered_high_risk_pairs"] = (
            interaction["applicable_high_risk_pairs"] - baseline
        )

        work = build_work_selection(
            selected_batch=self.queue["selected_batch"],
            policy=self.catalog["work_selection"],
            inputs=inputs,
        )
        assurance = next(
            candidate
            for candidate in work["candidates"]
            if candidate["candidate_id"]
            == "assurance:critical-interaction-recovery"
        )
        selected = next(
            candidate
            for candidate in work["candidates"]
            if candidate["candidate_id"] == work["selected_candidate_id"]
        )

        self.assertFalse(assurance["eligible"])
        self.assertEqual(
            "exit_gate_satisfied",
            assurance["assurance_readiness"]["status"],
        )
        self.assertIn(
            "no uncovered high-risk interaction debt remains",
            assurance["reranking_reason"],
        )
        self.assertEqual("compiler_harvest", selected["candidate_class"])
        self.assertIn(
            selected["candidate_id"],
            {
                f"frontier:{row['family_id']}"
                for row in inputs["card_unlock_frontier"]["family_candidates"]
            },
        )

    def test_large_exact_ability_harvest_can_rerank_unknown_gain_rules_work(self):
        inputs = _with_large_ability_compiler_harvest(self.work_inputs)
        work = build_work_selection(
            selected_batch=self.queue["selected_batch"],
            policy=self.catalog["work_selection"],
            inputs=inputs,
        )
        selected = next(
            candidate
            for candidate in work["candidates"]
            if candidate["candidate_id"] == work["selected_candidate_id"]
        )

        self.assertEqual(
            "frontier:effect_clause:large-ability-fixture",
            selected["candidate_id"],
        )
        self.assertEqual("compiler_harvest", selected["candidate_class"])
        self.assertEqual(21, selected["expected_complete_card_gain"])
        self.assertEqual(130, selected["expected_exact_ability_gain"])
        self.assertEqual(
            [
                "expected_exact_ability_gain",
                "expected_material_residual_reduction",
                "expected_complete_card_gain",
            ],
            work["selection_policy"]["coverage_rank_order"],
        )

    def test_runtime_text_candidates_are_split_by_declared_subsystem(self):
        work = self.queue["work_selection"]
        candidates = [
            candidate
            for candidate in work["candidates"]
            if candidate["candidate_class"] == "runtime_oracle_removal"
        ]
        self.assertNotIn(
            "architecture:runtime-oracle-text-subsystem-attribution",
            {candidate["candidate_id"] for candidate in candidates},
        )
        runtime_total = int(
            self.work_inputs["architecture_audit"]["architecture"]
            ["runtime_oracle_text_access"]
            ["prohibited_runtime_interpretation_count"]
        )
        self.assertEqual(
            runtime_total,
            sum(
                int(candidate["runtime_oracle_text_removal"]["expected_count"])
                for candidate in candidates
            ),
        )
        subsystems_with_debt = {
            str(capsule["id"])
            for capsule in self.work_inputs["architecture_audit"]
            ["architecture"]["subsystem_capsules"]
            if int(capsule["prohibited_runtime_oracle_text_accesses"]) > 0
        }
        self.assertEqual(
            subsystems_with_debt,
            {candidate["universal_subsystem"] for candidate in candidates},
        )

    def test_every_serious_candidate_carries_auditable_reranking_context(self):
        required = {
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
            "rank",
            "selection_state",
        }
        candidates = self.queue["work_selection"]["candidates"]
        self.assertTrue(candidates)
        for candidate in candidates:
            self.assertEqual(required, set(candidate))
            self.assertTrue(candidate["reranking_reason"])
            self.assertTrue(candidate["universal_subsystem"])
        history = self.queue["work_selection"]["reviewed_rerank_history"]
        self.assertEqual(
            self.catalog["work_selection"]["reviewed_rerank_history"],
            history,
        )
        candidate_ids = {candidate["candidate_id"] for candidate in candidates}
        for row in history:
            self.assertEqual(
                {"candidate_id", "selected_over", "reason"}, set(row)
            )
            self.assertRegex(row["candidate_id"], r"^(rules|compiler):")
            self.assertIn(row["selected_over"], candidate_ids)
            self.assertNotEqual(row["candidate_id"], row["selected_over"])
            self.assertGreaterEqual(len(row["reason"].split()), 12)

    def test_work_selection_policy_fails_closed(self):
        policy = deepcopy(self.catalog["work_selection"])
        policy["priority_classes"].append(policy["priority_classes"][0])
        with self.assertRaisesRegex(
            WorkSelectionError, "priority classes"
        ):
            build_work_selection(
                selected_batch=self.queue["selected_batch"],
                policy=policy,
                inputs=self.work_inputs,
            )

        policy = deepcopy(self.catalog["work_selection"])
        policy["reviewed_rerank_history"][0]["selected_over"] = (
            "frontier:missing-completed-candidate"
        )
        with self.assertRaisesRegex(
            WorkSelectionError, "selected_over must reference a current candidate"
        ):
            build_work_selection(
                selected_batch=self.queue["selected_batch"],
                policy=policy,
                inputs=self.work_inputs,
            )

        with self.assertRaisesRegex(
            RulesSchedulerError, "work-selection inputs"
        ):
            build_rules_dependency_queue(
                self.rule_index,
                self.conformance,
                self.catalog,
                self.capabilities,
                repository_root=ROOT,
            )


if __name__ == "__main__":
    unittest.main()
