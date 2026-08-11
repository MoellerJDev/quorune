from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
import unittest

from quorune.architecture_cli import (
    changed_capsules,
    execute_architecture_operation,
)
from quorune.cli import main
from scripts.update_architecture_audit import ROOT


class ArchitectureCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(
            (ROOT / "coverage" / "architecture-audit.json").read_text(
                encoding="utf-8"
            )
        )

    def test_show_returns_one_bounded_complete_capsule(self):
        capsule = execute_architecture_operation(
            "show", root=ROOT, subsystem="trigger_processing"
        )
        self.assertEqual(capsule["id"], "trigger_processing")
        self.assertIn("state_authority", capsule)
        self.assertIn("upstream_dependencies", capsule)
        self.assertIn("events_produced", capsule)
        self.assertIn("replay_behavior", capsule)
        self.assertLessEqual(len(capsule["primary_tests"]), 100)
        self.assertLessEqual(len(capsule["reusable_pieces"]), 100)

    def test_changed_maps_only_matching_capsules_and_preserves_unmapped_files(self):
        result = changed_capsules(
            self.report,
            ["quorune/trigger_discovery.py", "README.md"],
        )
        self.assertIn(
            "trigger_processing",
            [row["subsystem"] for row in result["affected_capsules"]],
        )
        self.assertEqual(result["unmapped_files"], ["README.md"])

    def test_debt_writes_and_runtime_text_are_current_generated_views(self):
        debt = execute_architecture_operation("debt", root=ROOT)
        writes = execute_architecture_operation(
            "writes", root=ROOT, subsystem="turn_priority_and_decisions"
        )
        runtime_text = execute_architecture_operation("runtime-text", root=ROOT)
        self.assertEqual(debt["missing_dedicated_owner_count"], 3)
        self.assertNotIn(
            "trigger_processing",
            [row["subsystem"] for row in debt["migration_queue"]],
        )
        self.assertEqual(debt["direct_game_state_writes"]["unowned"], 0)
        self.assertGreater(writes["count"], 0)
        self.assertEqual(
            runtime_text["prohibited_runtime_interpretation_count"],
            debt["runtime_oracle_text_access"]["by_classification"][
                "prohibited_runtime_interpretation"
            ],
        )

    def test_simctl_architecture_owners_reports_live_coordinates(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = main(["architecture", "owners", "--root", str(ROOT)])
        value = json.loads(output.getvalue())
        self.assertEqual(result, 0)
        self.assertTrue(value["current_feature"]["head"])
        self.assertTrue(value["current_main"]["head"])
        self.assertIsNone(value["certified_exact_head"]["head"])
        self.assertIn("reason", value["certified_exact_head"])


if __name__ == "__main__":
    unittest.main()
