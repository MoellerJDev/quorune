---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "0874a074eabe988c27a3c732091a1c5e8baf89145712601935a310d30f80ee7b"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `0874a074eabe988c27a3c732091a1c5e8baf89145712601935a310d30f80ee7b`

## Current top-level state

- Production logical lines: `157712`
- Engine logical lines: `7286`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `101`
- Registered runtime components: `68`
- Oversized production modules: `4`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
