---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "6cebdd6d14bce77534e36aaea2a22a3cbeae13fc66a87e8283287b94b91c2d80"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `6cebdd6d14bce77534e36aaea2a22a3cbeae13fc66a87e8283287b94b91c2d80`

## Current top-level state

- Production logical lines: `143043`
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
