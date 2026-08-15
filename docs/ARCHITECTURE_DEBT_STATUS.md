---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "3cb592ba499fad7845405d4544574dc226fac74ea5c825f610755cba262cabbd"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `3cb592ba499fad7845405d4544574dc226fac74ea5c825f610755cba262cabbd`

## Current top-level state

- Production logical lines: `155400`
- Engine logical lines: `7286`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `101`
- Registered runtime components: `66`
- Oversized production modules: `4`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
