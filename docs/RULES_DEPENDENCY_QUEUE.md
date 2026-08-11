---
title: "Rules dependency queue"
status: "generated"
authoritative_source: "coverage/rules-dependency-queue.json"
verified: "a1e9e69e7d47bf68ea926123d7e015228f5079164e67b5bbd40a9e455638c761"
audience: "rules, compiler, and engine contributors"
maintenance: "generated"
generated_source: "coverage/rules-dependency-queue.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write"
---

# Rules dependency queue

Source fingerprint: `1f841f9ad7bfe0d5667c6dcbd406f3eb30e8e7c47d9dd451f043e6c1dcead9d6`

## Current top-level state

- Pinned rules: `3300`
- Queued rules: `2927`
- Subsystems: `21`
- Selected subsystem: `replacement-prevention`
- Selected batch: `counter-producer-replacement-closure`

## Top blockers

- Inventory every represented permanent- and player-counter producer and identify which paths still bypass the canonical counter-placement owner.
- Route one coherent reusable producer family through the immutable resumable counter-placement transaction without adding direct GameState writes.
- Preserve cost timing, entry timing, simultaneous APNAP ordering, rollback, privacy, and exact replay for migrated producers.
- Add generic CardProgram lowering and precise source spans where the migrated family originates in Oracle text.
- Add focused positive, negative, interaction, multiplayer, rollback, replay, and killed implementation-mutation evidence for the migrated boundary.

Complete rule, subsystem, dependency, classification, and selected-batch data is in the [machine-readable rules queue](../coverage/rules-dependency-queue.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write
```
