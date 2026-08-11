---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "ce7e3a60dd175f43f1d6e906d296d25afd3fb3cd4f85308b69c5a3e1ae3f9677"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `ce7e3a60dd175f43f1d6e906d296d25afd3fb3cd4f85308b69c5a3e1ae3f9677`

## Current top-level state

- Production logical lines: `139800`
- Engine logical lines: `11522`
- Direct GameState-write heuristic: `127`
- Registered typed semantic handlers: `98`
- Registered runtime components: `44`
- Oversized production modules: `5`

## Top blockers

- Missing dedicated owner: `turn_priority_and_decisions`.
- Missing dedicated owner: `zones_and_object_identity`.
- Missing dedicated owner: `search_target_and_choice`.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3
```
