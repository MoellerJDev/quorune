---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "0bb2c750e6921b36c7cf71acb614be314a098b8f18ae83517bf7aecc0db0807a"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write"
---

# Architecture debt status

Source fingerprint: `0bb2c750e6921b36c7cf71acb614be314a098b8f18ae83517bf7aecc0db0807a`

## Current top-level state

- Production logical lines: `163491`
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
