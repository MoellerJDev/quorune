---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "2d73cf25dd338a6332dcb32ad3b47a93f5d5dddfb47fe8e870381ce6a90baa47"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `2d73cf25dd338a6332dcb32ad3b47a93f5d5dddfb47fe8e870381ce6a90baa47`

## Current top-level state

- Production logical lines: `145992`
- Engine logical lines: `7825`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `99`
- Registered runtime components: `49`
- Oversized production modules: `5`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3
```
