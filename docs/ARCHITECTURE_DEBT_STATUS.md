---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "7da3ab564012ddee3aa7a104b1c05f6e8d353a02478de25b1441e1e9ec77f91c"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `7da3ab564012ddee3aa7a104b1c05f6e8d353a02478de25b1441e1e9ec77f91c`

## Current top-level state

- Production logical lines: `127844`
- Engine logical lines: `12080`
- Direct GameState-write heuristic: `128`
- Registered typed semantic handlers: `94`
- Registered runtime components: `35`
- Oversized production modules: `5`

## Top blockers

- Missing dedicated owner: `turn_priority_and_decisions`.
- Missing dedicated owner: `zones_and_object_identity`.
- Missing dedicated owner: `search_target_and_choice`.
- Missing dedicated owner: `trigger_processing`.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3
```
