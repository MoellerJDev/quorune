---
title: "Rules dependency queue"
status: "generated"
authoritative_source: "coverage/rules-dependency-queue.json"
verified: "43c82ff015371aa3d8e9e3db613a2cc6154d5908515c97da98f29f0715f6ee5c"
audience: "rules, compiler, and engine contributors"
maintenance: "generated"
generated_source: "coverage/rules-dependency-queue.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write"
---

# Rules dependency queue

Source fingerprint: `1f93874a52154f9c85ee8d63b02280e1c33a5bd8932656c3e480aeab261d82c2`

## Current top-level state

- Pinned rules: `3300`
- Queued rules: `2953`
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
