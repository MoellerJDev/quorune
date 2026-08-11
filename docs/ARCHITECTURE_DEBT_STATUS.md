---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "806a1d97a97068b24a10e147baa1dd572c3232f0184cacaa980b24e7a88bf93e"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `806a1d97a97068b24a10e147baa1dd572c3232f0184cacaa980b24e7a88bf93e`

## Current top-level state

- Production logical lines: `134688`
- Engine logical lines: `11744`
- Direct GameState-write heuristic: `128`
- Registered typed semantic handlers: `97`
- Registered runtime components: `38`
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
