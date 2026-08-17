---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "06f4b62a7057ba1abe4364ce3268800f707dbb5b2d749c51604afd82c07d22b8"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `06f4b62a7057ba1abe4364ce3268800f707dbb5b2d749c51604afd82c07d22b8`

## Current top-level state

- Production logical lines: `165772`
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
