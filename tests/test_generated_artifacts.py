from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest

from scripts.finalize_generated import stabilization_ids, write_until_stable
from scripts.update_compiler_corpus_coverage import (
    CompilerCorpusCoverageError,
    validate_reports,
)
from scripts.generated_artifacts import (
    GeneratedArtifactManifestError,
    GeneratorSpec,
    ROOT,
    all_outputs,
    load_manifest,
    parse_manifest,
    topological_order,
)
from scripts.install_dev_hooks import (
    HookInstallationError,
    check as check_hooks,
    install as install_hooks,
)
from quorune.oracle_ir import ORACLE_COMPILER_VERSION
from quorune.rules.capabilities import load_default_capability_registry


class GeneratedArtifactFinalizationTests(unittest.TestCase):
    def test_compiler_corpus_reports_fail_closed_on_stale_source_or_counts(self):
        capabilities = load_default_capability_registry()
        snapshot = {"oracle_source_sha256": "a" * 64}

        def oracle(commander_only: bool, count: int) -> dict:
            return {
                "compiler_version": ORACLE_COMPILER_VERSION,
                "capability_profile": "commander_review",
                "capability_registry_fingerprint": capabilities.fingerprint,
                "capability_evidence_fingerprint": (
                    capabilities.evidence_fingerprint
                ),
                "card_data_snapshot": snapshot,
                "commander_legal_only": commander_only,
                "total_oracle_ids": count,
                "status_counts": {"exact": count},
            }

        def program(commander_only: bool, count: int) -> dict:
            return {
                "compiler_version": ORACLE_COMPILER_VERSION,
                "profile": "commander_review",
                "capability_registry_fingerprint": capabilities.fingerprint,
                "capability_evidence_fingerprint": (
                    capabilities.evidence_fingerprint
                ),
                "card_data_snapshot": snapshot,
                "commander_legal_only": commander_only,
                "cards_considered": count,
                "status_counts": {"trusted": count},
            }

        reports = {
            "oracle_full": oracle(False, 4),
            "oracle_commander": oracle(True, 3),
            "program_full": program(False, 4),
            "program_commander": program(True, 3),
        }
        validate_reports(reports)

        stale = copy.deepcopy(reports)
        stale["program_commander"]["compiler_version"] = "oracle-ir-stale"
        with self.assertRaisesRegex(
            CompilerCorpusCoverageError, "compiler version is stale"
        ):
            validate_reports(stale)

        mismatched = copy.deepcopy(reports)
        mismatched["program_commander"]["cards_considered"] = 2
        with self.assertRaisesRegex(
            CompilerCorpusCoverageError, "card counts are inconsistent"
        ):
            validate_reports(mismatched)

    def test_generated_manifest_has_one_owner_and_dependency_order(self):
        specs = load_manifest()
        ordered = [spec.id for spec in topological_order(specs)]
        outputs = all_outputs(specs)

        self.assertEqual(len(outputs), len(set(outputs)))
        self.assertEqual(
            {
                "architecture-audit",
                "capability-evidence",
                "card-unlock-frontier",
                "ci-escape-report",
                "compiler-corpus-coverage",
                "continuous-effect-performance",
                "module-classifications",
                "platform-status",
                "reusable-pieces",
                "rules-scheduler",
            },
            {spec.id for spec in specs},
        )
        self.assertLess(
            ordered.index("compiler-corpus-coverage"),
            ordered.index("card-unlock-frontier"),
        )
        self.assertLess(
            ordered.index("compiler-corpus-coverage"),
            ordered.index("platform-status"),
        )
        self.assertLess(
            ordered.index("platform-status"),
            ordered.index("architecture-audit"),
        )
        self.assertLess(
            ordered.index("architecture-audit"),
            ordered.index("reusable-pieces"),
        )

    def test_generated_manifest_rejects_duplicate_output_and_cycle(self):
        manifest = json.loads(
            (ROOT / "platform" / "generated-artifacts.json").read_text(
                encoding="utf-8"
            )
        )
        duplicate = copy.deepcopy(manifest)
        duplicate["generators"][1]["outputs"].append(
            duplicate["generators"][0]["outputs"][0]
        )
        with self.assertRaisesRegex(
            GeneratedArtifactManifestError, "multiple owners"
        ):
            parse_manifest(duplicate)

        cycle = copy.deepcopy(manifest)
        cycle["generators"][0]["depends_on"] = [
            cycle["generators"][-1]["id"]
        ]
        with self.assertRaisesRegex(GeneratedArtifactManifestError, "cycle"):
            parse_manifest(cycle)

    def test_generated_manifest_rejects_paths_outside_repository(self):
        manifest = json.loads(
            (ROOT / "platform" / "generated-artifacts.json").read_text(
                encoding="utf-8"
            )
        )
        escaped = copy.deepcopy(manifest)
        escaped["generators"][0]["outputs"] = ["../outside.json"]

        with self.assertRaisesRegex(
            GeneratedArtifactManifestError,
            "repository-relative POSIX path",
        ):
            parse_manifest(escaped)

    def test_generated_finalizer_reaches_a_bounded_fixed_point(self):
        with TemporaryDirectory() as raw:
            root = Path(raw)
            specs = (
                GeneratorSpec(
                    id="first",
                    depends_on=(),
                    outputs=("first.txt",),
                    check=("unused.py", "--check"),
                    write=("unused.py", "--write"),
                    write_with_database=None,
                    write_policy="automatic",
                ),
                GeneratorSpec(
                    id="second",
                    depends_on=("first",),
                    outputs=("second.txt",),
                    check=("unused.py", "--check"),
                    write=("unused.py", "--write"),
                    write_with_database=None,
                    write_policy="automatic",
                ),
            )
            calls: list[str] = []

            def runner(generator_id: str, _command: tuple[str, ...]) -> int:
                calls.append(generator_id)
                if generator_id == "first":
                    (root / "first.txt").write_text("first\n", encoding="utf-8")
                else:
                    value = (root / "first.txt").read_text(encoding="utf-8")
                    (root / "second.txt").write_text(value + "second\n", encoding="utf-8")
                return 0

            result = write_until_stable(
                specs,
                database=None,
                include_manual=False,
                max_passes=3,
                root=root,
                runner=runner,
            )

        self.assertEqual(2, result["passes"])
        self.assertEqual(["first", "second", "first", "second"], calls)
        self.assertEqual(
            ("first.txt", "second.txt"),
            result["changed_by_pass"][0],
        )
        self.assertEqual((), result["changed_by_pass"][1])

    def test_generated_finalizer_rebuilds_database_corpus_only_once(self):
        with TemporaryDirectory() as raw:
            root = Path(raw)
            database = root / "cards.sqlite3"
            database.write_bytes(b"fixture")
            spec = GeneratorSpec(
                id="corpus",
                depends_on=(),
                outputs=("corpus.txt",),
                check=("unused.py", "--check"),
                write=("unused.py", "--refresh-derived"),
                write_with_database=(
                    "unused.py",
                    "--write",
                    "--db",
                    "{db}",
                ),
                write_policy="database",
            )
            commands: list[tuple[str, ...]] = []

            def runner(_generator_id: str, command: tuple[str, ...]) -> int:
                commands.append(command)
                (root / "corpus.txt").write_text("stable\n", encoding="utf-8")
                return 0

            result = write_until_stable(
                (spec,),
                database=database,
                include_manual=False,
                max_passes=3,
                root=root,
                runner=runner,
            )

        self.assertEqual(2, result["passes"])
        self.assertIn("--write", commands[0])
        self.assertIn(str(database), commands[0])
        self.assertIn("--refresh-derived", commands[1])
        self.assertNotIn(str(database), commands[1])

    def test_stabilization_reruns_only_changed_owners_and_descendants(self):
        specs = (
            GeneratorSpec(
                id="source",
                depends_on=(),
                outputs=("source.txt",),
                check=("unused.py", "--check"),
                write=("unused.py", "--write"),
                write_with_database=None,
                write_policy="automatic",
            ),
            GeneratorSpec(
                id="consumer",
                depends_on=("source",),
                outputs=("consumer.txt",),
                check=("unused.py", "--check"),
                write=("unused.py", "--write"),
                write_with_database=None,
                write_policy="automatic",
            ),
            GeneratorSpec(
                id="unrelated",
                depends_on=(),
                outputs=("unrelated.txt",),
                check=("unused.py", "--check"),
                write=("unused.py", "--write"),
                write_with_database=None,
                write_policy="automatic",
            ),
        )

        self.assertEqual(
            frozenset({"source", "consumer"}),
            stabilization_ids(specs, ("source.txt",)),
        )

    def test_generated_ci_uses_the_canonical_finalizer_only(self):
        workflow_dir = ROOT / ".github" / "workflows"
        workflows = {
            path.name: path.read_text(encoding="utf-8")
            for path in workflow_dir.glob("*.yml")
        }
        for name in ("ci.yml", "main-smoke.yml", "nightly.yml"):
            self.assertIn(
                "python scripts/finalize_generated.py --check",
                workflows[name],
            )
        combined = "\n".join(workflows.values())
        for spec in load_manifest():
            command = "python " + " ".join(spec.check)
            self.assertNotIn(command, combined)

    def test_generated_pre_push_hook_uses_worktree_python_and_stops_on_changes(self):
        hook = (ROOT / ".githooks" / "pre-push").read_text(
            encoding="utf-8"
        )
        self.assertIn(".venv/bin/python", hook)
        self.assertIn(".venv/Scripts/python.exe", hook)
        self.assertIn("data/scryfall-current.sqlite3", hook)
        self.assertIn('"$ROOT/scripts/test_shards.py" validate', hook)
        self.assertIn("--write --fail-on-change", hook)
        self.assertNotIn("python scripts/finalize_generated.py", hook)

    def test_generated_hook_installer_is_idempotent_and_preserves_foreign_policy(self):
        with TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            tracked = root / ".githooks" / "pre-push"
            tracked.parent.mkdir()
            shutil.copy2(ROOT / ".githooks" / "pre-push", tracked)

            install_hooks(root)
            install_hooks(root)
            check_hooks(root)
            configured = subprocess.check_output(
                ["git", "config", "--local", "--get", "core.hooksPath"],
                cwd=root,
                text=True,
                encoding="utf-8",
            ).strip()
            self.assertEqual(".githooks", configured)

            subprocess.run(
                ["git", "config", "--local", "core.hooksPath", "custom-hooks"],
                cwd=root,
                check=True,
            )
            with self.assertRaisesRegex(
                HookInstallationError, "refusing to replace"
            ):
                install_hooks(root)


if __name__ == "__main__":
    unittest.main()
