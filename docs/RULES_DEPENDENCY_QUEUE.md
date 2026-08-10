---
title: "Rules dependency queue"
status: "generated"
authoritative_source: "coverage/rules-dependency-queue.json"
verified: "c8d97d40edef6b62cc2b28d3896c386f76e0082d706c3f6846071a3b0a2939bc"
audience: "rules, compiler, and engine contributors"
maintenance: "generated"
generated_source: "coverage/rules-dependency-queue.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write"
---

# Rules dependency queue

Source fingerprint: `7e94b4093dba22cfe446ad44c67d5bd0f71bae6882dc1eb5c443cda1c77c2a36`

## Current top-level state

- Pinned rules: `3300`
- Queued rules: `2948`
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
