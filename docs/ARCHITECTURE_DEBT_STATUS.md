---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "75fb6f80e1b071a12be3e3fb88cd46ca33e5eff9b0f54b13981ac8e13a9ca275"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `75fb6f80e1b071a12be3e3fb88cd46ca33e5eff9b0f54b13981ac8e13a9ca275`

## Current top-level state

- Production logical lines: `150347`
- Engine logical lines: `7286`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `100`
- Registered runtime components: `63`
- Oversized production modules: `4`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
