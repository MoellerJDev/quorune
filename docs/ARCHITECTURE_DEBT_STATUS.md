---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "bbdad42c5021888e15974e3f9d4613b5a29a518f1d3d0861b2ea5f8dbec7a3f9"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `bbdad42c5021888e15974e3f9d4613b5a29a518f1d3d0861b2ea5f8dbec7a3f9`

## Current top-level state

- Production logical lines: `168446`
- Engine logical lines: `7073`
- Direct GameState-write heuristic: `82`
- Registered typed semantic handlers: `105`
- Registered runtime components: `78`
- Oversized production modules: `4`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
