---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "ecbcdd06ebfdb467363a9995d43a55cf611b9ac6bebd7b10351acda582e7117c"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `ecbcdd06ebfdb467363a9995d43a55cf611b9ac6bebd7b10351acda582e7117c`

## Current top-level state

- Production logical lines: `164835`
- Engine logical lines: `7080`
- Direct GameState-write heuristic: `82`
- Registered typed semantic handlers: `105`
- Registered runtime components: `74`
- Oversized production modules: `4`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
