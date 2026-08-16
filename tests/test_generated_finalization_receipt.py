from __future__ import annotations

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from scripts.generated_artifacts import GeneratorSpec
from scripts.generated_finalization_receipt import (
    GeneratedFinalizationReceiptError,
    database_identity,
    finalization_receipt_path,
    verify_finalization_receipt,
    write_finalization_receipt,
)


class GeneratedFinalizationReceiptTests(unittest.TestCase):
    def test_receipt_survives_commit_and_rejects_every_input_drift(self):
        with TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Generated Test"],
                cwd=root,
                check=True,
            )
            source = root / "source.py"
            source.write_text("VALUE = 1\n", encoding="utf-8")
            coverage = root / "coverage"
            coverage.mkdir()
            output = coverage / "owned.json"
            output.write_text("{}\n", encoding="utf-8")
            database = root / "cards.sqlite3"
            database.write_bytes(b"database-v1")
            subprocess.run(
                ["git", "add", "source.py", "coverage/owned.json"],
                cwd=root,
                check=True,
            )
            spec = GeneratorSpec(
                id="owned",
                depends_on=(),
                outputs=("coverage/owned.json",),
                check=("unused.py", "--check"),
                write=("unused.py", "--write"),
                write_with_database=None,
                write_policy="automatic",
            )

            with self.assertRaisesRegex(
                GeneratedFinalizationReceiptError,
                "missing or malformed",
            ):
                verify_finalization_receipt(
                    (spec,), database=database, root=root
                )
            path, written = write_finalization_receipt(
                (spec,),
                database=database,
                root=root,
            )
            self.assertEqual(finalization_receipt_path(root), path)
            self.assertTrue(path.is_file())
            self.assertIn(".git", path.parts)
            self.assertFalse(
                (root / "generated-finalization-receipt.json").exists()
            )
            subprocess.run(
                ["git", "commit", "-qm", "fixture"],
                cwd=root,
                check=True,
            )
            _path, observed = verify_finalization_receipt(
                (spec,),
                database=database,
                root=root,
            )
            self.assertEqual(written, observed)
            _path, inferred = verify_finalization_receipt(
                (spec,),
                database=None,
                root=root,
            )
            self.assertEqual(written, inferred)

            malformed = written.to_dict()
            malformed["unexpected"] = True
            path.write_text(
                json.dumps(malformed, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                GeneratedFinalizationReceiptError,
                "incomplete or unknown",
            ):
                verify_finalization_receipt(
                    (spec,), database=database, root=root
                )
            path.write_text(
                json.dumps(written.to_dict(), sort_keys=True) + "\n",
                encoding="utf-8",
            )

            invalid_version = written.to_dict()
            invalid_version["schema_version"] = True
            path.write_text(
                json.dumps(invalid_version, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                GeneratedFinalizationReceiptError,
                "schema is unsupported",
            ):
                verify_finalization_receipt(
                    (spec,), database=database, root=root
                )
            path.write_text(
                json.dumps(written.to_dict(), sort_keys=True) + "\n",
                encoding="utf-8",
            )

            wal = Path(str(database) + "-wal")
            wal.write_bytes(b"pending-pages")
            with self.assertRaisesRegex(
                GeneratedFinalizationReceiptError,
                "database_fingerprint",
            ):
                verify_finalization_receipt(
                    (spec,), database=database, root=root
                )
            with self.assertRaisesRegex(
                GeneratedFinalizationReceiptError,
                "database_fingerprint",
            ):
                verify_finalization_receipt(
                    (spec,), database=None, root=root
                )
            wal.unlink()

            source.write_text("VALUE = 2\n", encoding="utf-8")
            with self.assertRaisesRegex(
                GeneratedFinalizationReceiptError,
                "source_tree_fingerprint",
            ):
                verify_finalization_receipt(
                    (spec,), database=database, root=root
                )
            source.write_text("VALUE = 1\n", encoding="utf-8")

            output.write_text('{"changed": true}\n', encoding="utf-8")
            with self.assertRaisesRegex(
                GeneratedFinalizationReceiptError,
                "generated_outputs_fingerprint",
            ):
                verify_finalization_receipt(
                    (spec,), database=database, root=root
                )
            output.write_text("{}\n", encoding="utf-8")

            initial_database_identity = database_identity(database)
            database.write_bytes(b"database-v2-is-different")
            with self.assertRaisesRegex(
                GeneratedFinalizationReceiptError,
                "database_fingerprint",
            ):
                verify_finalization_receipt(
                    (spec,), database=database, root=root
                )
            with self.assertRaisesRegex(
                GeneratedFinalizationReceiptError,
                "changed while generators were running",
            ):
                write_finalization_receipt(
                    (spec,),
                    database=database,
                    root=root,
                    expected_database_identity=initial_database_identity,
                )


if __name__ == "__main__":
    unittest.main()
