---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "c84996bf12b3aabd62dade0cba0c527032e90da7d6f8bcd8445a2b9582cf3c47"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `c84996bf12b3aabd62dade0cba0c527032e90da7d6f8bcd8445a2b9582cf3c47`

## Current top-level state

- Production logical lines: `161198`
- Engine logical lines: `7257`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `103`
- Registered runtime components: `69`
- Oversized production modules: `4`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
