from __future__ import annotations

import unittest

from tests.common import ROOT
from scripts.validate_pr_body import (
    EVIDENCE_CLASSES,
    validate_body,
    validate_status_changes,
)


TEMPLATE = (ROOT / ".github" / "pull_request_template.md").read_text(
    encoding="utf-8"
)


def valid_body() -> str:
    evidence = "\n".join(
        f"| {name} | N/A — this CI-policy change does not alter that behavioral surface. |"
        for name in EVIDENCE_CLASSES
    )
    return f"""# Summary

Validate pull-request descriptions before expensive certification jobs begin.

## Change class and authority

- Change class: tooling
- Governing rules or capabilities: N/A — repository policy only.
- Oracle/rulings snapshot: N/A — no card data is changed.
- Supported profile affected: N/A — protocol behavior is unchanged.

## Ownership and implementation

- Owner before: prose-only pull-request template
- Owner after: deterministic early CI validator
- Duplicate or superseded paths removed: none
- `CommanderEngine` delta: zero
- Direct authoritative-write delta: zero
- Prohibited identity-dispatch delta: zero
- Oracle-ID literal delta: zero
- Compiler/CardProgram changes: none
- Card, residual, and capability-closure deltas: N/A — no rules change.

## Evidence

| Class | Result |
| --- | --- |
{evidence}

## Generated artifacts

- Source inputs changed: none
- Generators run: N/A — no generated source or output changed.
- Outputs changed: none
- Freshness checks: canonical finalizer check remains in public CI.

## Documentation and decisions

- Current documents changed: CI contributor guidance
- ADR added or superseded: N/A — this applies an existing policy.
- Changelog effect: none

## Limitations and rollback

- Exact remaining limitations: semantic evidence quality still requires review.
- Rollback plan: revert the validator and workflow step together.
- Compatibility or migration risk: none

## Safety checklist

- [x] The change is one coherent subsystem-sized unit; unrelated cleanup is excluded.
- [x] Advertised actions and accepted commands use the same authoritative legality path, or this is N/A with a reason above.
- [x] No card-name, collector-number, set-code, or Oracle-ID behavior was added to the generic runtime.
- [x] No direct `GameState` write was added outside a declared owner.
- [x] Deterministic replay, protocol/schema versions, privacy projection, and rollback are preserved or explicitly versioned and certified.
- [x] Generated outputs were regenerated only by their owners and contain no hand-edited metrics.
- [x] No credential, capability, private hand, library order, checkpoint, live record, bulk archive, database, cache, or artwork was added.
- [x] Third-party content remains within `docs/LEGAL_CONTENT_BOUNDARY.md`.
- [x] Required checks were not weakened, bypassed, renamed, or made optional.
- [x] Every N/A above includes a concrete reason.
"""


class PullRequestBodyPolicyTests(unittest.TestCase):
    def codes(self, body: str) -> set[str]:
        return {failure.code for failure in validate_body(body, TEMPLATE)}

    def test_complete_description_is_accepted(self) -> None:
        self.assertEqual(set(), self.codes(valid_body()))

    def test_untouched_template_comment_is_rejected(self) -> None:
        body = valid_body().replace(
            "Validate pull-request descriptions",
            "<!-- CI validates this form. Remove every instructional comment, "
            "fill every evidence row, explain each N/A, and check every safety "
            "assertion. Explain the durable outcome and why this is one coherent "
            "change. -->\n\n"
            "Validate pull-request descriptions",
        )
        self.assertIn("template-comment", self.codes(body))

    def test_missing_and_empty_required_sections_are_rejected(self) -> None:
        missing = valid_body().replace("# Summary", "# Overview", 1)
        self.assertIn("missing-section", self.codes(missing))
        empty = valid_body().replace(
            "Validate pull-request descriptions before expensive certification jobs begin.",
            "",
            1,
        )
        self.assertIn("empty-section", self.codes(empty))

    def test_structured_fields_cannot_be_left_blank(self) -> None:
        body = valid_body().replace(
            "- Owner after: deterministic early CI validator", "- Owner after:"
        )
        self.assertIn("blank-field", self.codes(body))

    def test_every_evidence_row_requires_a_result_or_reasoned_not_applicable(self) -> None:
        blank = valid_body().replace(
            "| Focused mutation | N/A — this CI-policy change does not alter that behavioral surface. |",
            "| Focused mutation | |",
        )
        self.assertIn("blank-evidence", self.codes(blank))
        bare = valid_body().replace(
            "| Property and fuzz | N/A — this CI-policy change does not alter that behavioral surface. |",
            "| Property and fuzz | N/A |",
        )
        self.assertIn("bare-not-applicable", self.codes(bare))

    def test_generated_claim_requires_canonical_write_finalizer(self) -> None:
        claimed = valid_body().replace(
            "- Source inputs changed: none",
            "- Source inputs changed: platform/readiness-source.json",
        ).replace(
            "- Outputs changed: none",
            "- Outputs changed: coverage/platform-readiness.json",
        )
        self.assertIn("missing-finalizer", self.codes(claimed))
        finalized = claimed.replace(
            "- Generators run: N/A — no generated source or output changed.",
            "- Generators run: `.\\.venv\\Scripts\\python.exe scripts/finalize_generated.py --write`",
        )
        self.assertNotIn("missing-finalizer", self.codes(finalized))

    def test_broad_local_success_claim_requires_command_and_numeric_result(self) -> None:
        unsupported = valid_body().replace(
            "canonical finalizer check remains in public CI.",
            "The full local test suite passed.",
        )
        self.assertIn("unsupported-local-claim", self.codes(unsupported))
        supported = unsupported.replace(
            "The full local test suite passed.",
            "The full local test suite passed: `python -m unittest tests.test_pr_body_policy`; 12 tests passed.",
        )
        self.assertNotIn("unsupported-local-claim", self.codes(supported))

    def test_broad_ci_success_claim_requires_actions_run_url(self) -> None:
        unsupported = valid_body().replace(
            "Validate pull-request descriptions before expensive certification jobs begin.",
            "Validate pull-request descriptions before expensive certification "
            "jobs begin. All required CI checks passed.",
        )
        self.assertIn("unsupported-ci-claim", self.codes(unsupported))
        supported = unsupported.replace(
            "All required CI checks passed.",
            "All required CI checks passed in "
            "https://github.com/MoellerJDev/quorune/actions/runs/31340000000.",
        )
        self.assertNotIn("unsupported-ci-claim", self.codes(supported))

    def test_unchecked_safety_assertion_is_rejected(self) -> None:
        body = valid_body().replace(
            "- [x] The change is one coherent", "- [ ] The change is one coherent"
        )
        self.assertIn("unchecked-safety", self.codes(body))

    def test_missing_safety_assertion_is_rejected(self) -> None:
        body = valid_body().replace(
            "- [x] Required checks were not weakened, bypassed, renamed, or made optional.\n",
            "",
        )
        self.assertIn("missing-safety", self.codes(body))

    def test_new_volatile_status_provenance_is_rejected(self) -> None:
        before = {"milestones": []}
        after = {
            "milestones": [
                {
                    "evidence": (
                        "PR #175 passed exact-head run 31340000000 on "
                        "rules/example-branch."
                    )
                }
            ]
        }
        failures = validate_status_changes(
            before, after, source="platform/readiness-source.json"
        )
        self.assertEqual({"volatile-status-provenance"}, {row.code for row in failures})

    def test_source_paths_under_branch_named_directories_are_not_provenance(self) -> None:
        before = {"scope": {"state_owner_modules": []}}
        after = {
            "scope": {
                "state_owner_modules": [
                    "quorune/rules/casting/commit.py",
                    "quorune/rules/activation/commit.py",
                ]
            }
        }
        self.assertEqual(
            (),
            validate_status_changes(
                before,
                after,
                source="platform/architecture-audit-source.json",
            ),
        )

    def test_standalone_feature_branch_remains_volatile_provenance(self) -> None:
        failures = validate_status_changes(
            {"milestones": []},
            {"milestones": [{"source": "rules/example-branch"}]},
            source="platform/readiness-source.json",
        )
        self.assertEqual({"volatile-status-provenance"}, {row.code for row in failures})

    def test_durable_repository_paths_are_not_feature_branch_provenance(self) -> None:
        failures = validate_status_changes(
            {"subsystems": []},
            {
                "subsystems": [
                    {
                        "adrs": [
                            "docs/adr/0018-unified-trigger-batch-ownership.md"
                        ]
                    }
                ]
            },
            source="platform/architecture-audit-source.json",
        )
        self.assertEqual((), failures)

    def test_new_explicit_historical_observation_is_durable(self) -> None:
        failures = validate_status_changes(
            {"historical_observations": []},
            {
                "historical_observations": [
                    {
                        "baseline_main_commit": "a" * 40,
                        "certification": {
                            "run_id": 31340000000,
                            "url": (
                                "https://github.com/MoellerJDev/quorune/"
                                "actions/runs/31340000000"
                            ),
                        },
                    }
                ]
            },
            source="platform/architecture-audit-source.json",
        )
        self.assertEqual((), failures)

    def test_unchanged_historical_provenance_is_not_reinterpreted(self) -> None:
        value = {
            "audit": {"baseline_main_commit": "a" * 40},
            "ci": {"run_id": 12345678},
        }
        self.assertEqual(
            (),
            validate_status_changes(
                value, value, source="platform/architecture-audit-source.json"
            ),
        )

    def test_changed_volatile_field_is_rejected_but_durable_policy_is_allowed(self) -> None:
        failures = validate_status_changes(
            {"ci": {"run_id": 12345678}},
            {"ci": {"run_id": 12345679}},
            source="platform/architecture-audit-source.json",
        )
        self.assertEqual(1, len(failures))
        durable = validate_status_changes(
            {"repository": {"default_branch": "main"}, "policy": "old"},
            {
                "repository": {"default_branch": "main"},
                "policy": "Exact-head public CI remains the merge authority.",
            },
            source="platform/readiness-source.json",
        )
        self.assertEqual((), durable)


if __name__ == "__main__":
    unittest.main()
