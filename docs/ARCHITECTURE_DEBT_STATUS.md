---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "d37e9e616a6ce9ee91b34b3ef95588588f40dacb546fe67e5e651b97cdd813ce"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `d37e9e616a6ce9ee91b34b3ef95588588f40dacb546fe67e5e651b97cdd813ce`

## Current top-level state

- Production logical lines: `163494`
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
