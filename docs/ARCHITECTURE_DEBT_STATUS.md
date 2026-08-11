---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "0f2350ce67331ff38d9fa816d65553b5e04b180236b922124e2f64382833c8ed"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `0f2350ce67331ff38d9fa816d65553b5e04b180236b922124e2f64382833c8ed`

## Current top-level state

- Production logical lines: `142242`
- Engine logical lines: `8003`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `98`
- Registered runtime components: `44`
- Oversized production modules: `5`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3
```
