---
title: "Architecture debt status"
status: "generated"
authoritative_source: "coverage/architecture-audit.json"
verified: "23ae81117142b2685be9e6b8a3d524bed088df4b5796a4d71a87fce5ddf86bad"
audience: "maintainers and rules contributors"
maintenance: "generated"
generated_source: "coverage/architecture-audit.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3"
---

# Architecture debt status

Source fingerprint: `23ae81117142b2685be9e6b8a3d524bed088df4b5796a4d71a87fce5ddf86bad`

## Current top-level state

- Production logical lines: `140732`
- Engine logical lines: `10244`
- Direct GameState-write heuristic: `83`
- Registered typed semantic handlers: `98`
- Registered runtime components: `44`
- Oversized production modules: `5`

## Top blockers

- Missing dedicated owner: `search_target_and_choice`.

Complete module, symbol, ownership, test, and documentation inventories are in the [machine-readable architecture audit](../coverage/architecture-audit.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_architecture_audit.py --write --card-db data\scryfall-current.sqlite3
```
