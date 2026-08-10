---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "f0900b1c50e4be4b14461fe67ff058ebe6d6a11398b07a65ac75c12fab047999"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `f0900b1c50e4be4b14461fe67ff058ebe6d6a11398b07a65ac75c12fab047999`

## Current top-level state

- Production logical lines: `127432`
- Engine logical lines: `12080`
- Direct GameState-write heuristic: `128`
- Registered typed semantic handlers: `93`
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
