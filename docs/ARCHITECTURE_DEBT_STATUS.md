---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "914293499151710a70cef35d16ba72b4d9d3478a9c7597142cbaf7d92ea65c17"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `914293499151710a70cef35d16ba72b4d9d3478a9c7597142cbaf7d92ea65c17`

## Current top-level state

- Production logical lines: `144604`
- Engine logical lines: `7994`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `99`
- Registered runtime components: `47`
- Oversized production modules: `5`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3
```
