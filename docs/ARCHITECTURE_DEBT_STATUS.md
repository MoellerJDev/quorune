---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "0ea14751dab8ac980184072048009f92af1a2eae578b042528f9952b5eb0f7db"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `0ea14751dab8ac980184072048009f92af1a2eae578b042528f9952b5eb0f7db`

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
