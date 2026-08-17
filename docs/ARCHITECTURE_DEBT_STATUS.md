---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "d7aff047a1fc394623ff15a3c495ad20eb3e4d24f81b0172592c8b43bd89b2f0"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `d7aff047a1fc394623ff15a3c495ad20eb3e4d24f81b0172592c8b43bd89b2f0`

## Current top-level state

- Production logical lines: `163237`
- Engine logical lines: `7257`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `105`
- Registered runtime components: `73`
- Oversized production modules: `4`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
