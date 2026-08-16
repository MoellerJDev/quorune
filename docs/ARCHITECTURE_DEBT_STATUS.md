---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "90c8233b19dd4a7abc9d860a171395720c500afebf2e00d73b2425573ece4530"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `90c8233b19dd4a7abc9d860a171395720c500afebf2e00d73b2425573ece4530`

## Current top-level state

- Production logical lines: `159206`
- Engine logical lines: `7286`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `103`
- Registered runtime components: `68`
- Oversized production modules: `4`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
