---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "204a90e4504589e358fe75136cd020dbcab6e50f8ba5e01296fd18feeacddb21"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `204a90e4504589e358fe75136cd020dbcab6e50f8ba5e01296fd18feeacddb21`

## Current top-level state

- Production logical lines: `173646`
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
