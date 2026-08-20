---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "5178decd0fe5b107b778c90351c106d9e2f4dd7a5fb4db78b44f281f55c4815d"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `5178decd0fe5b107b778c90351c106d9e2f4dd7a5fb4db78b44f281f55c4815d`

## Current top-level state

- Production logical lines: `168378`
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
