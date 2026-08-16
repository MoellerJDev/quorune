---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "6604534e1b395e7b27613ef4aceab4c22f72100a66704d8a86edb7527cfe6b41"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `6604534e1b395e7b27613ef4aceab4c22f72100a66704d8a86edb7527cfe6b41`

## Current top-level state

- Production logical lines: `159481`
- Engine logical lines: `7275`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `103`
- Registered runtime components: `68`
- Oversized production modules: `4`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
