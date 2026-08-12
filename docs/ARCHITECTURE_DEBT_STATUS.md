---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "72e5f43f3ee5d54fd923010de9895808f2dcfa3eda07394b9c4517531adf0c84"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `72e5f43f3ee5d54fd923010de9895808f2dcfa3eda07394b9c4517531adf0c84`

## Current top-level state

- Production logical lines: `144297`
- Engine logical lines: `7994`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `99`
- Registered runtime components: `46`
- Oversized production modules: `5`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3
```
