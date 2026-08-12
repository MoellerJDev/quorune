from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

import pytest

from scripts.pytest_shard_plugin import (
    canonical_collection,
    expected_collection,
)
from scripts.test_shards import (
    canonical_test_ids,
    discovered_modules,
    functional_shards,
    load_manifest,
    load_suite,
    primary_matrix,
    PytestShardRecorder,
    run_modules,
    suite_modules,
    test_collection_fingerprint,
    TestShardError,
    validate_partition,
)


class TestShardManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_manifest()

    def test_every_test_module_has_one_primary_shard(self):
        summary = validate_partition(self.manifest)
        self.assertEqual(len(discovered_modules()), summary["test_modules"])

    def test_primary_matrix_uses_every_authoritative_shard_once(self):
        rows = primary_matrix(self.manifest)["include"]
        self.assertEqual(
            list(self.manifest["execution_order"]),
            [row["shard"] for row in rows],
        )
        self.assertIn("generated-validation", [row["shard"] for row in rows])
        self.assertEqual(
            [
                name
                for name in self.manifest["execution_order"]
                if name != "generated-validation"
            ],
            list(functional_shards(self.manifest)),
        )

    def test_execution_order_is_a_strict_permutation(self):
        with TemporaryDirectory() as raw:
            path = Path(raw) / "test-shards.json"
            for mutation, message in (
                (lambda value: value["execution_order"].pop(), "every primary"),
                (
                    lambda value: value["execution_order"].append(
                        value["execution_order"][0]
                    ),
                    "duplicates",
                ),
                (
                    lambda value: value["execution_order"].__setitem__(0, "unknown"),
                    "every primary",
                ),
            ):
                mutated = deepcopy(self.manifest)
                mutation(mutated)
                path.write_text(json.dumps(mutated), encoding="utf-8")
                with self.subTest(message=message):
                    with self.assertRaisesRegex(TestShardError, message):
                        load_manifest(path)

    def test_duplicate_primary_assignment_fails_closed(self):
        mutated = deepcopy(self.manifest)
        module = mutated["primary_shards"]["core-domain"][0]
        mutated["primary_shards"]["compiler-cardprogram"].append(module)
        with self.assertRaisesRegex(TestShardError, "duplicates"):
            validate_partition(mutated)

    def test_missing_primary_assignment_fails_closed(self):
        mutated = deepcopy(self.manifest)
        mutated["primary_shards"]["core-domain"].pop()
        with self.assertRaisesRegex(TestShardError, "missing"):
            validate_partition(mutated)

    def test_overlay_suites_are_explicit_and_known(self):
        windows = suite_modules(self.manifest, "windows-compat")
        self.assertIn("test_server_app", windows)
        self.assertIn("test_game_record_v3", windows)

    def test_unknown_suite_fails_closed(self):
        with self.assertRaisesRegex(TestShardError, "Unknown test suite"):
            suite_modules(self.manifest, "not-a-suite")

    def test_unittest_collection_has_one_stable_canonical_fingerprint(self):
        modules = suite_modules(self.manifest, "main-smoke")
        first = canonical_test_ids(load_suite(modules))
        second = canonical_test_ids(load_suite(tuple(reversed(modules))))
        self.assertEqual(first, second)
        self.assertEqual(len(first), len(set(first)))
        self.assertEqual(
            test_collection_fingerprint(first),
            test_collection_fingerprint(second),
        )
        self.assertNotEqual(
            test_collection_fingerprint(first),
            test_collection_fingerprint((*first[:-1], first[-1] + "-changed")),
        )

    def test_parallel_worker_configuration_fails_closed(self):
        with self.assertRaisesRegex(TestShardError, "at least two workers"):
            run_modules(
                ("test_rules_primitives",),
                backend="pytest-xdist",
                workers=1,
            )
        with self.assertRaisesRegex(TestShardError, "exactly one worker"):
            run_modules(
                ("test_rules_primitives",),
                backend="unittest",
                workers=2,
            )

    def test_pytest_collection_adapter_rejects_non_unittest_and_duplicates(self):
        def item(identifier: str):
            return SimpleNamespace(
                nodeid=identifier,
                _testcase=SimpleNamespace(id=lambda: identifier),
            )

        self.assertEqual(("a", "b"), canonical_collection((item("b"), item("a"))))
        with self.assertRaisesRegex(pytest.UsageError, "duplicate"):
            canonical_collection((item("a"), item("a")))
        with self.assertRaisesRegex(pytest.UsageError, "only accept unittest"):
            canonical_collection((SimpleNamespace(nodeid="free_function"),))

    def test_expected_parallel_collection_fails_closed_for_malformed_data(self):
        with TemporaryDirectory() as raw:
            path = Path(raw) / "expected.json"
            path.write_text(json.dumps(["b", "a"]), encoding="utf-8")
            with self.assertRaisesRegex(pytest.UsageError, "canonically sorted"):
                expected_collection(path)
            path.write_text(json.dumps(["a", "a"]), encoding="utf-8")
            with self.assertRaisesRegex(pytest.UsageError, "duplicate"):
                expected_collection(path)

    def test_parallel_result_recorder_reports_observed_module_time(self):
        recorder = PytestShardRecorder()
        recorder.pytest_runtest_logreport(
            SimpleNamespace(
                nodeid="tests/test_sample.py::Case::test_ok",
                duration=1.25,
                skipped=False,
                failed=False,
                passed=True,
                when="call",
            )
        )
        recorder.pytest_runtest_logreport(
            SimpleNamespace(
                nodeid="tests/test_sample.py::Case::test_bad",
                duration=0.5,
                skipped=False,
                failed=True,
                passed=False,
                when="call",
            )
        )
        self.assertEqual(2, len(recorder.seen_items))
        self.assertEqual(1, recorder.failures)
        self.assertEqual(
            [{"module": "test_sample", "worker_elapsed_seconds": 1.75}],
            recorder.module_timings(),
        )


if __name__ == "__main__":
    unittest.main()
