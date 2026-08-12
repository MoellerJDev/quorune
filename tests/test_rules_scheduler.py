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
        self.assertEqual(3300, self.queue["summary"]["total_rules"])

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
        work = self.queue["work_selection"]
        selected = next(
            candidate
            for candidate in work["candidates"]
            if candidate["candidate_id"] == work["selected_candidate_id"]
        )
        self.assertEqual("runtime_oracle_removal", selected["candidate_class"])
        self.assertNotEqual(
            "cross_subsystem_runtime_semantics", selected["universal_subsystem"]
        )
        runtime_total = int(
            self.work_inputs["architecture_audit"]["architecture"]
            ["runtime_oracle_text_access"]
            ["prohibited_runtime_interpretation_count"]
        )
        selected_runtime_count = int(
            selected["runtime_oracle_text_removal"]["expected_count"]
        )
        self.assertGreater(selected_runtime_count, 0)
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
            {
                "rules:ordinary-shroud-target-legality",
                "rules:ordinary-echo-upkeep-trigger",
                "rules:ordinary-fixed-threshold-crew",
            },
            {row["candidate_id"] for row in history},
        )

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
