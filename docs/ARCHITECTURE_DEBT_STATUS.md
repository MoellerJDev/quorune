---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "cc9373799329917c4cbc37b2cc8af39e1fe8261be70658d34d12848afb39a777"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `cc9373799329917c4cbc37b2cc8af39e1fe8261be70658d34d12848afb39a777`

## Current top-level state

- Production logical lines: `173284`
- Engine logical lines: `7096`
- Direct GameState-write heuristic: `82`
- Registered typed semantic handlers: `107`
- Registered runtime components: `81`
- Oversized production modules: `5`

## Top blockers

- None detected by the configured architecture policy.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write
```
