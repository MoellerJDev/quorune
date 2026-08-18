from __future__ import annotations

import json
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .carddb import CardDatabase, build_card_database, file_sha256
from .util import stable_json
from .version import __version__

SCRYFALL_BULK_DATA_URL = "https://api.scryfall.com/bulk-data"
SCRYFALL_USER_AGENT = f"quorune/{__version__} (local bulk-data importer)"
ALLOWED_DOWNLOAD_HOSTS = frozenset({"data.scryfall.io"})


class ScryfallBulkDataError(RuntimeError):
    pass


def _prune_managed_bulk_cache(download_path: Path, retained: set[Path]) -> tuple[Path, ...]:
    removed: list[Path] = []
    retained_resolved = {path.resolve() for path in retained}
    for candidate in download_path.iterdir():
        resolved_candidate = candidate.resolve()
        managed_archive = (
            candidate.is_file()
            and (
                candidate.name.startswith("oracle-cards-")
                or candidate.name.startswith("rulings-")
            )
            and candidate.name.endswith(".jsonl.gz")
        )
        stale_partial = candidate.is_file() and candidate.name.endswith(".jsonl.gz.part")
        if resolved_candidate not in retained_resolved and (managed_archive or stale_partial):
            candidate.unlink()
            removed.append(candidate)
    return tuple(removed)


@dataclass(frozen=True, slots=True)
class ScryfallBulkItem:
    type: str
    name: str
    updated_at: str
    download_uri: str
    compressed_size: int | None = None


def parse_bulk_manifest(payload: Mapping[str, Any]) -> dict[str, ScryfallBulkItem]:
    if payload.get("object") != "list" or not isinstance(payload.get("data"), list):
        raise ScryfallBulkDataError("Scryfall bulk-data response is not a list")

    items: dict[str, ScryfallBulkItem] = {}
    for raw in payload["data"]:
        if not isinstance(raw, Mapping):
            continue
        item_type = str(raw.get("type") or "")
        download_uri = str(
            raw.get("jsonl_download_uri") or raw.get("download_uri") or ""
        )
        parsed_uri = urllib.parse.urlparse(download_uri)
        if (
            not item_type
            or parsed_uri.scheme.casefold() != "https"
            or (parsed_uri.hostname or "").casefold() not in ALLOWED_DOWNLOAD_HOSTS
        ):
            continue
        raw_size = raw.get("compressed_size")
        if raw_size is None and str(raw.get("content_encoding") or "").casefold() == "gzip":
            raw_size = raw.get("size")
        items[item_type] = ScryfallBulkItem(
            type=item_type,
            name=str(raw.get("name") or item_type),
            updated_at=str(raw.get("updated_at") or ""),
            download_uri=download_uri,
            compressed_size=int(raw_size) if raw_size is not None else None,
        )
    return items


def fetch_bulk_manifest(
    *,
    url: str = SCRYFALL_BULK_DATA_URL,
    timeout: float = 30,
    urlopen: Callable[..., Any] = urllib.request.urlopen,
) -> tuple[dict[str, ScryfallBulkItem], dict[str, Any]]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": SCRYFALL_USER_AGENT,
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (OSError, urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise ScryfallBulkDataError(f"Unable to read {url}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ScryfallBulkDataError("Scryfall bulk-data response must be a JSON object")
    return parse_bulk_manifest(payload), payload


def _download_bulk_item(
    item: ScryfallBulkItem,
    destination_dir: Path,
    *,
    timeout: float,
    force: bool,
    urlopen: Callable[..., Any] = urllib.request.urlopen,
) -> Path:
    filename = Path(urllib.parse.urlparse(item.download_uri).path).name
    if not filename:
        raise ScryfallBulkDataError(f"Bulk item {item.type!r} has no filename")
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / filename
    if destination.exists() and not force and destination.stat().st_size > 0:
        return destination

    temporary = destination.with_name(destination.name + ".part")
    if temporary.exists():
        temporary.unlink()
    request = urllib.request.Request(
        item.download_uri,
        headers={
            "Accept": "application/json,application/gzip,application/octet-stream",
            "User-Agent": SCRYFALL_USER_AGENT,
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response, temporary.open("wb") as output:
            content_length = response.headers.get("Content-Length")
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        if content_length is not None and temporary.stat().st_size != int(content_length):
            raise ScryfallBulkDataError(
                f"{item.type} download has {temporary.stat().st_size} bytes; "
                f"HTTP response declared {content_length}"
            )
        temporary.replace(destination)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise
    return destination


def refresh_scryfall_database(
    output_path: str | Path,
    *,
    download_dir: str | Path,
    manifest_url: str = SCRYFALL_BULK_DATA_URL,
    timeout: float = 60,
    force_download: bool = False,
) -> dict[str, Any]:
    """Discover current Oracle/rulings exports and atomically rebuild SQLite.

    Network access is confined to this explicit pre-game import operation.
    Running games continue to use only the resulting local database.
    """

    items, manifest_payload = fetch_bulk_manifest(url=manifest_url, timeout=timeout)
    missing = [item_type for item_type in ("oracle_cards", "rulings") if item_type not in items]
    if missing:
        raise ScryfallBulkDataError(
            "Scryfall manifest omitted required bulk item(s): " + ", ".join(missing)
        )

    download_path = Path(download_dir)
    oracle_path = _download_bulk_item(
        items["oracle_cards"],
        download_path,
        timeout=timeout,
        force=force_download,
    )
    rulings_path = _download_bulk_item(
        items["rulings"],
        download_path,
        timeout=timeout,
        force=force_download,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".building")
    if temporary.exists():
        temporary.unlink()
    try:
        result = build_card_database(
            oracle_path,
            rulings_path,
            temporary,
            overwrite=True,
        )
        connection = sqlite3.connect(temporary)
        try:
            connection.executemany(
                "INSERT OR REPLACE INTO metadata(key, value) VALUES (?, ?)",
                [
                    ("bulk_manifest_url", manifest_url),
                    ("scryfall_oracle_updated_at", items["oracle_cards"].updated_at),
                    (
                        "scryfall_oracle_download_uri",
                        items["oracle_cards"].download_uri,
                    ),
                    ("scryfall_rulings_updated_at", items["rulings"].updated_at),
                    (
                        "scryfall_rulings_download_uri",
                        items["rulings"].download_uri,
                    ),
                ],
            )
            connection.commit()
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            connection.execute("PRAGMA journal_mode=DELETE")
        finally:
            connection.close()
        temporary.replace(output)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise

    manifest_path = download_path / "bulk-manifest.json"
    manifest_path.write_text(stable_json(manifest_payload), encoding="utf-8")
    retained = {oracle_path, rulings_path, manifest_path}
    # The directory is a managed cache. Keep the active Oracle/rulings pair and
    # discard only timestamped Scryfall archives or stale partials, never an
    # arbitrary neighboring file supplied by the user.
    _prune_managed_bulk_cache(download_path, retained)

    with CardDatabase(output) as database:
        metadata = database.metadata()
    result.update(
        {
            "database": str(output),
            "oracle_updated_at": metadata["scryfall_oracle_updated_at"],
            "rulings_updated_at": metadata["scryfall_rulings_updated_at"],
            "oracle_sha256": metadata["oracle_source_sha256"],
            "rulings_sha256": metadata["rulings_source_sha256"],
            "oracle_download": str(oracle_path),
            "rulings_download": str(rulings_path),
        }
    )
    return result


def _pinned_bulk_snapshot(
    snapshot: Mapping[str, Any],
) -> tuple[
    str,
    dict[str, ScryfallBulkItem],
    dict[str, str],
    dict[str, int],
]:
    if not isinstance(snapshot, Mapping) or snapshot.get("available") is not True:
        raise ScryfallBulkDataError("Pinned card-data snapshot is unavailable")
    expected_schema_version = str(snapshot.get("database_schema_version") or "")
    if not expected_schema_version:
        raise ScryfallBulkDataError(
            "Pinned card-data database schema version is unavailable"
        )
    item_specs = {
        "oracle_cards": ("oracle_bulk", "oracle_id_count"),
        "rulings": ("rulings_bulk", "ruling_count"),
    }
    items: dict[str, ScryfallBulkItem] = {}
    expected_hashes: dict[str, str] = {}
    expected_counts: dict[str, int] = {}
    for item_type, (field, count_field) in item_specs.items():
        raw = snapshot.get(field)
        if not isinstance(raw, Mapping):
            raise ScryfallBulkDataError(f"Pinned snapshot has no {field}")
        uri = str(raw.get("download_uri") or "")
        parsed = urllib.parse.urlparse(uri)
        if (
            parsed.scheme.casefold() != "https"
            or (parsed.hostname or "").casefold() not in ALLOWED_DOWNLOAD_HOSTS
        ):
            raise ScryfallBulkDataError(
                f"Pinned {item_type} download must use trusted Scryfall HTTPS"
            )
        digest = str(raw.get("sha256") or "")
        if len(digest) != 64 or any(
            value not in "0123456789abcdef" for value in digest
        ):
            raise ScryfallBulkDataError(
                f"Pinned {item_type} SHA-256 is missing or malformed"
            )
        count = raw.get(count_field)
        if type(count) is not int or count < 0:
            raise ScryfallBulkDataError(
                f"Pinned {item_type} count is missing or malformed"
            )
        items[item_type] = ScryfallBulkItem(
            type=item_type,
            name=item_type,
            updated_at=str(raw.get("updated_at") or ""),
            download_uri=uri,
        )
        expected_hashes[item_type] = digest
        expected_counts[item_type] = count
    return expected_schema_version, items, expected_hashes, expected_counts


def _download_pinned_bulk_items(
    items: Mapping[str, ScryfallBulkItem],
    expected_hashes: Mapping[str, str],
    download_path: Path,
    *,
    timeout: float,
    force_download: bool,
    urlopen: Callable[..., Any],
) -> dict[str, Path]:
    downloaded: dict[str, Path] = {}
    for item_type, item in items.items():
        path = _download_bulk_item(
            item,
            download_path,
            timeout=timeout,
            force=force_download,
            urlopen=urlopen,
        )
        if file_sha256(path) != expected_hashes[item_type]:
            path = _download_bulk_item(
                item,
                download_path,
                timeout=timeout,
                force=True,
                urlopen=urlopen,
            )
        if file_sha256(path) != expected_hashes[item_type]:
            raise ScryfallBulkDataError(
                f"Pinned {item_type} archive does not match its SHA-256"
            )
        downloaded[item_type] = path
    return downloaded


def _build_pinned_database_file(
    output: Path,
    downloaded: Mapping[str, Path],
    items: Mapping[str, ScryfallBulkItem],
    expected_counts: Mapping[str, int],
    expected_schema_version: str,
) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".building")
    if temporary.exists():
        temporary.unlink()
    try:
        result = build_card_database(
            downloaded["oracle_cards"],
            downloaded["rulings"],
            temporary,
            overwrite=True,
        )
        connection = sqlite3.connect(temporary)
        try:
            connection.executemany(
                "INSERT OR REPLACE INTO metadata(key, value) VALUES (?, ?)",
                [
                    ("bulk_manifest_url", "rules/manifest.json"),
                    (
                        "scryfall_oracle_updated_at",
                        items["oracle_cards"].updated_at,
                    ),
                    (
                        "scryfall_oracle_download_uri",
                        items["oracle_cards"].download_uri,
                    ),
                    (
                        "scryfall_rulings_updated_at",
                        items["rulings"].updated_at,
                    ),
                    (
                        "scryfall_rulings_download_uri",
                        items["rulings"].download_uri,
                    ),
                ],
            )
            connection.commit()
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            connection.execute("PRAGMA journal_mode=DELETE")
        finally:
            connection.close()
        with CardDatabase(temporary) as database:
            metadata = database.metadata()
        observed_counts = {
            "oracle_cards": int(metadata.get("card_count") or -1),
            "rulings": int(metadata.get("ruling_count") or -1),
        }
        if observed_counts != expected_counts:
            raise ScryfallBulkDataError(
                "Pinned database counts do not match the rules manifest: "
                f"expected={expected_counts}, observed={observed_counts}"
            )
        if metadata.get("schema_version") != expected_schema_version:
            raise ScryfallBulkDataError(
                "Pinned database schema does not match the rules manifest: "
                f"expected={expected_schema_version}, "
                f"observed={metadata.get('schema_version')}"
            )
        temporary.replace(output)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise
    return result


def build_pinned_scryfall_database(
    snapshot: Mapping[str, Any],
    output_path: str | Path,
    *,
    download_dir: str | Path,
    timeout: float = 60,
    force_download: bool = False,
    urlopen: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    """Rebuild the exact card database pinned by the rules manifest."""

    (
        expected_schema_version,
        items,
        expected_hashes,
        expected_counts,
    ) = _pinned_bulk_snapshot(snapshot)
    download_path = Path(download_dir)
    downloaded = _download_pinned_bulk_items(
        items,
        expected_hashes,
        download_path,
        timeout=timeout,
        force_download=force_download,
        urlopen=urlopen,
    )
    output = Path(output_path)
    result = _build_pinned_database_file(
        output,
        downloaded,
        items,
        expected_counts,
        expected_schema_version,
    )

    _prune_managed_bulk_cache(
        download_path,
        {downloaded["oracle_cards"], downloaded["rulings"]},
    )
    result.update(
        {
            "database": str(output),
            "database_sha256": file_sha256(output),
            "oracle_sha256": expected_hashes["oracle_cards"],
            "rulings_sha256": expected_hashes["rulings"],
            "oracle_download": str(downloaded["oracle_cards"]),
            "rulings_download": str(downloaded["rulings"]),
            "snapshot_source": "rules/manifest.json",
        }
    )
    return result
