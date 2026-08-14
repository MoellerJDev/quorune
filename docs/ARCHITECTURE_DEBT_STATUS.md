---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "e6c0b5517a28f8c0efa13c294fe54318257e761a72d68cd4a044ac0170e76093"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `e6c0b5517a28f8c0efa13c294fe54318257e761a72d68cd4a044ac0170e76093`

## Current top-level state

- Production logical lines: `152452`
- Engine logical lines: `7286`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `100`
- Registered runtime components: `65`
- Oversized production modules: `4`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
