---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "6c3415d90af0819f8dbf93cdcd2f56037c4c832b509695339eeca3c1e9984bf7"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `6c3415d90af0819f8dbf93cdcd2f56037c4c832b509695339eeca3c1e9984bf7`

## Current top-level state

- Production logical lines: `147067`
- Engine logical lines: `7736`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `99`
- Registered runtime components: `50`
- Oversized production modules: `5`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
