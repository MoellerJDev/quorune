---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "a95f61e1fd32f596ae1e549d8961eca0725db07d218366aef2338a015bd19b21"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `a95f61e1fd32f596ae1e549d8961eca0725db07d218366aef2338a015bd19b21`

## Current top-level state

- Production logical lines: `138735`
- Engine logical lines: `11696`
- Direct GameState-write heuristic: `128`
- Registered typed semantic handlers: `98`
- Registered runtime components: `42`
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
