---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "d5b0f950fa60efe9a76729067a81d5783a1e186c8441bf70f1fcd8e2982035ad"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `d5b0f950fa60efe9a76729067a81d5783a1e186c8441bf70f1fcd8e2982035ad`

## Current top-level state

- Production logical lines: `147065`
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
