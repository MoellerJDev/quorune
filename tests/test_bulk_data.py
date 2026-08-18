from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from quorune.bulk import (
    ScryfallBulkDataError,
    ScryfallBulkItem,
    _download_bulk_item,
    _prune_managed_bulk_cache,
    build_pinned_scryfall_database,
    fetch_bulk_manifest,
    parse_bulk_manifest,
)
from quorune.carddb import CardDatabase


class _Response(io.BytesIO):
    def __init__(self, value: bytes, headers=None):
        super().__init__(value)
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class ScryfallBulkDataTests(unittest.TestCase):
    def test_pinned_snapshot_build_verifies_archives_counts_and_metadata(self):
        card = {
            "oracle_id": "00000000-0000-4000-8000-000000000001",
            "name": "Pinned Cloud Fixture",
            "mana_cost": "{1}",
            "cmc": 1,
            "type_line": "Artifact",
            "oracle_text": "",
            "colors": [],
            "color_identity": [],
            "keywords": [],
            "produced_mana": [],
            "layout": "normal",
            "released_at": "2026-01-01",
            "legalities": {"commander": "legal"},
        }
        archives = {
            "https://data.scryfall.io/oracle-pinned.jsonl.gz": gzip.compress(
                (json.dumps(card) + "\n").encode("utf-8")
            ),
            "https://data.scryfall.io/rulings-pinned.jsonl.gz": gzip.compress(
                b""
            ),
        }
        snapshot = {
            "available": True,
            "database_schema_version": "2",
            "oracle_bulk": {
                "updated_at": "2026-08-06T09:02:54Z",
                "download_uri": next(iter(archives)),
                "sha256": hashlib.sha256(
                    archives[next(iter(archives))]
                ).hexdigest(),
                "oracle_id_count": 1,
            },
            "rulings_bulk": {
                "updated_at": "2026-08-06T09:00:37Z",
                "download_uri": list(archives)[1],
                "sha256": hashlib.sha256(
                    archives[list(archives)[1]]
                ).hexdigest(),
                "ruling_count": 0,
            },
        }

        def fake_urlopen(request, timeout):
            self.assertEqual(7, timeout)
            payload = archives[request.full_url]
            return _Response(payload, {"Content-Length": str(len(payload))})

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "pinned.sqlite3"
            result = build_pinned_scryfall_database(
                snapshot,
                output,
                download_dir=root / "bulk",
                timeout=7,
                urlopen=fake_urlopen,
            )
            with CardDatabase(output) as database:
                metadata = database.metadata()

        self.assertEqual(1, result["cards"])
        self.assertEqual("rules/manifest.json", result["snapshot_source"])
        self.assertEqual(
            snapshot["oracle_bulk"]["sha256"],
            metadata["oracle_source_sha256"],
        )
        self.assertEqual(
            snapshot["oracle_bulk"]["download_uri"],
            metadata["scryfall_oracle_download_uri"],
        )

    def test_pinned_snapshot_rejects_untrusted_download_host(self):
        with self.assertRaises(ScryfallBulkDataError):
            build_pinned_scryfall_database(
                {
                    "available": True,
                    "database_schema_version": "2",
                    "oracle_bulk": {
                        "updated_at": "now",
                        "download_uri": "https://attacker.invalid/oracle.gz",
                        "sha256": "a" * 64,
                        "oracle_id_count": 1,
                    },
                    "rulings_bulk": {
                        "updated_at": "now",
                        "download_uri": "https://data.scryfall.io/rulings.gz",
                        "sha256": "b" * 64,
                        "ruling_count": 0,
                    },
                },
                "ignored.sqlite3",
                download_dir="ignored-bulk",
            )

    def test_manifest_prefers_streamable_jsonl_and_ignores_untrusted_hosts(self):
        items = parse_bulk_manifest(
            {
                "object": "list",
                "data": [
                    {
                        "type": "oracle_cards",
                        "name": "Oracle Cards",
                        "updated_at": "2026-07-28T20:11:20Z",
                        "download_uri": "https://data.scryfall.io/oracle.json",
                        "jsonl_download_uri": "https://data.scryfall.io/oracle.jsonl.gz",
                        "compressed_size": 123,
                    },
                    {
                        "type": "rulings",
                        "jsonl_download_uri": "https://attacker.invalid/rulings.jsonl.gz",
                    },
                ],
            }
        )
        self.assertEqual("https://data.scryfall.io/oracle.jsonl.gz", items["oracle_cards"].download_uri)
        self.assertEqual(123, items["oracle_cards"].compressed_size)
        self.assertNotIn("rulings", items)

    def test_fetch_manifest_uses_runtime_response(self):
        payload = {
            "object": "list",
            "data": [
                {
                    "type": "rulings",
                    "name": "Rulings",
                    "updated_at": "now",
                    "jsonl_download_uri": "https://data.scryfall.io/rulings-current.jsonl.gz",
                }
            ],
        }
        calls = []

        def fake_urlopen(request, timeout):
            calls.append((request.full_url, timeout, request.get_header("User-agent")))
            return _Response(json.dumps(payload).encode("utf-8"))

        items, returned = fetch_bulk_manifest(timeout=7, urlopen=fake_urlopen)
        self.assertEqual(payload, returned)
        self.assertIn("rulings", items)
        self.assertEqual("https://api.scryfall.com/bulk-data", calls[0][0])
        self.assertEqual(7, calls[0][1])
        self.assertIn("quorune", calls[0][2])

    def test_invalid_manifest_fails_closed(self):
        with self.assertRaises(ScryfallBulkDataError):
            parse_bulk_manifest({"object": "card", "data": []})

    def test_download_validates_http_length_not_inconsistent_manifest_size(self):
        item = ScryfallBulkItem(
            type="rulings",
            name="Rulings",
            updated_at="now",
            download_uri="https://data.scryfall.io/rulings.jsonl.gz",
            compressed_size=999,
        )

        def fake_urlopen(_request, timeout):
            self.assertEqual(3, timeout)
            return _Response(b"abc", {"Content-Length": "3"})

        with tempfile.TemporaryDirectory() as directory:
            path = _download_bulk_item(
                item,
                Path(directory),
                timeout=3,
                force=False,
                urlopen=fake_urlopen,
            )
            self.assertEqual(b"abc", path.read_bytes())

    def test_successful_refresh_retains_only_current_managed_archives(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            current_oracle = root / "oracle-cards-current.jsonl.gz"
            current_rulings = root / "rulings-current.jsonl.gz"
            old_oracle = root / "oracle-cards-old.jsonl.gz"
            old_rulings = root / "rulings-old.jsonl.gz"
            stale_partial = root / "oracle-cards-failed.jsonl.gz.part"
            user_file = root / "custom-card-data.jsonl.gz"
            for path in (
                current_oracle,
                current_rulings,
                old_oracle,
                old_rulings,
                stale_partial,
                user_file,
            ):
                path.write_bytes(b"fixture")

            removed = _prune_managed_bulk_cache(
                root, {current_oracle, current_rulings}
            )

            self.assertEqual(
                {old_oracle, old_rulings, stale_partial}, set(removed)
            )
            self.assertTrue(current_oracle.exists())
            self.assertTrue(current_rulings.exists())
            self.assertTrue(user_file.exists())


if __name__ == "__main__":
    unittest.main()
