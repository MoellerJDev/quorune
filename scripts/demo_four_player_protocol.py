from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quorune import (
    CardDatabase,
    CommanderSession,
    DeckLoader,
    ProjectedClientView,
    StateProjector,
)


EXPECTED_OUTPUT_NAMES = frozenset(
    {
        "SMOKE_TEST.md",
        "pilot-a-after-declaration-delta.json",
        "pilot-a-bootstrap.json",
        "pilot-a-unchanged-delta.json",
        "token-benchmark.json",
    }
)


def public_fixture_packet(packet: dict) -> dict:
    """Return a documentation-safe packet with bearer capabilities redacted."""

    sanitized = copy.deepcopy(packet)
    decision = sanitized.get("decision")
    if isinstance(decision, dict) and "cap" in decision:
        decision["cap"] = "<redacted-capability>"
    return sanitized


def _validate_capabilities(value: object, *, path: Path) -> None:
    if isinstance(value, dict):
        capability = value.get("cap")
        if capability is not None and capability != "<redacted-capability>":
            raise ValueError(
                f"Protocol demo contains an unredacted capability: {path}"
            )
        for child in value.values():
            _validate_capabilities(child, path=path)
    elif isinstance(value, list):
        for child in value:
            _validate_capabilities(child, path=path)


def validate_protocol_output(out: Path) -> dict[str, object]:
    actual = {path.name for path in out.iterdir() if path.is_file()}
    if actual != EXPECTED_OUTPUT_NAMES:
        raise ValueError(
            "Protocol demo output inventory is stale: "
            f"missing={sorted(EXPECTED_OUTPUT_NAMES - actual)}, "
            f"unexpected={sorted(actual - EXPECTED_OUTPUT_NAMES)}"
        )
    for name in sorted(EXPECTED_OUTPUT_NAMES - {"SMOKE_TEST.md"}):
        path = out / name
        value = json.loads(path.read_text(encoding="utf-8"))
        _validate_capabilities(value, path=path)
    smoke = (out / "SMOKE_TEST.md").read_text(encoding="utf-8")
    if not smoke.startswith("---\n") or 'status: "generated"' not in smoke[:512]:
        raise ValueError("Protocol demo documentation metadata is missing")
    benchmark = json.loads(
        (out / "token-benchmark.json").read_text(encoding="utf-8")
    )
    return {
        "ok": True,
        "outputs": sorted(EXPECTED_OUTPUT_NAMES),
        "protocol": benchmark["protocol"],
        "players": benchmark["players"],
        "seed": benchmark["seed"],
        "raw_capabilities": "absent",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/scryfall-20260728-compact.sqlite3")
    parser.add_argument("--out", default="demo")
    parser.add_argument("--seed", type=int, default=20260728)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    root = ROOT
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    if args.check:
        print(json.dumps(validate_protocol_output(out), indent=2, sort_keys=True))
        return 0
    out.mkdir(parents=True, exist_ok=True)

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = root / db_path
    db = CardDatabase(db_path)
    try:
        loader = DeckLoader(db)
        mishra = loader.load(root / "examples/mishra-eminent-one.txt", commander="Mishra, Eminent One")
        zimone = loader.load(root / "examples/zimone-and-dina.txt", commander="Zimone and Dina")
        session = CommanderSession.create(
            db,
            {"A": mishra, "B": zimone, "C": mishra, "D": zimone},
            first_player="A",
            seed=args.seed,
        )
        client = ProjectedClientView("pilot:A")

        full = session.packet("pilot:A", full=True)
        client.ingest(full)
        unchanged = session.packet("pilot:A")
        client.ingest(unchanged)
        session.act("pilot:A", {"a": "mulligan"})
        after_declaration = session.packet("pilot:A")
        client.ingest(after_declaration)

        public_full = public_fixture_packet(full)
        public_unchanged = public_fixture_packet(unchanged)
        public_after_declaration = public_fixture_packet(after_declaration)

        (out / "pilot-a-bootstrap.json").write_text(
            json.dumps(public_full, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (out / "pilot-a-unchanged-delta.json").write_text(
            json.dumps(public_unchanged, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (out / "pilot-a-after-declaration-delta.json").write_text(
            json.dumps(public_after_declaration, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        measures = {
            "bootstrap": StateProjector.measure(full),
            "unchanged_live_decision": StateProjector.measure(unchanged),
            "after_declaration": StateProjector.measure(after_declaration),
            "ratios": {
                "unchanged_vs_bootstrap": round(
                    StateProjector.measure(unchanged)["compact_chars"]
                    / StateProjector.measure(full)["compact_chars"],
                    4,
                ),
                "declaration_vs_bootstrap": round(
                    StateProjector.measure(after_declaration)["compact_chars"]
                    / StateProjector.measure(full)["compact_chars"],
                    4,
                ),
            },
            "protocol": full["v"],
            "players": 4,
            "seed": args.seed,
        }
        (out / "token-benchmark.json").write_text(
            json.dumps(measures, indent=2), encoding="utf-8"
        )

        summary = f"""---
title: "Four-player protocol smoke test"
status: "generated"
authoritative_source: "scripts/demo_four_player_protocol.py"
verified: "2026-08-01"
audience: "protocol and projection contributors"
maintenance: "generated"
---

# Four-player protocol smoke test

- Protocol: `{full['v']}`
- Seats: A Mishra, B Zimone/Dina, C Mishra, D Zimone/Dina
- Initial pending principal: `pilot:A`
- After A declares a mulligan, the next principal is `{session.pending_principals()[0]}`.
  This demonstrates turn-order declarations rather than concurrent declarations.
- Pilot A still has seven cards until every player in the round has declared;
  redraws are applied together after the last declaration.
- Bootstrap estimate: {measures['bootstrap']['estimated_tokens']} tokens
- Repeated live-decision delta: {measures['unchanged_live_decision']['estimated_tokens']} tokens
- A's declaration delta: {measures['after_declaration']['estimated_tokens']} tokens
- Client reducer hash after the final packet: `{client.current_hash}`

The demo intentionally stops before B declares. It tests protocol routing,
least-privilege seat projection, turn-order mulligan input, hash-checked patches,
and token measurement without requiring card semantics.
"""
        (out / "SMOKE_TEST.md").write_text(summary, encoding="utf-8")
        print(json.dumps(measures, indent=2))
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
