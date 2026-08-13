---
title: "Rules dependency queue"
status: "generated"
authoritative_source: "coverage/rules-dependency-queue.json"
verified: "530cfadbc65c3726b5fe26a70f42da25f859f76270d95e86b31a0f4b7104fa29"
audience: "rules, compiler, and engine contributors"
maintenance: "generated"
generated_source: "coverage/rules-dependency-queue.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write"
---

# Rules dependency queue

Source fingerprint: `4050183890f2c60dfd6f2d41ce6f48162e49dbc9870063fa7c03a27d325ca174`

## Current top-level state

- Pinned rules: `3300`
- Queued rules: `2919`
- Subsystems: `21`
- Selected subsystem: `replacement-prevention`
- Selected batch: `counter-producer-replacement-closure`
- Selected cross-program work: `assurance:critical-interaction-recovery`
- Selected work class: `interaction_assurance`

## Cross-program work selection

The rules batch remains dependency-ready, but final foreground work is reranked with deterministic CI, replay/privacy, architecture, runtime-text, interaction-assurance, compiler, and card-frontier evidence. A larger card gain cannot outrank a higher-priority correctness class.

Priority classes: `ci_correctness` → `replay_privacy_defect` → `architecture_owner_extraction` → `runtime_oracle_removal` → `interaction_assurance` → `architecture_debt` → `rules_foundation` → `compiler_harvest` → `card_family`

| Rank | State | Candidate | Class | Complete cards | Residuals | Runtime text | Direct writes |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | selected | `assurance:critical-interaction-recovery` | `interaction_assurance` | 0 | 0 | 0 | 0 |
| 2 | deferred | `architecture:engine-mutation-and-specificity-debt` | `architecture_debt` | 0 | 0 | 0 | 55 |
| 3 | deferred | `rules:counter-producer-replacement-closure` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 4 | deferred | `frontier:effect_clause:typed-spell-additional-cost-clause` | `compiler_harvest` | 122 | 123 | 0 | 0 |
| 5 | deferred | `frontier:effect_clause:deal-damage` | `compiler_harvest` | 112 | 245 | 0 | 0 |
| 6 | complete | `ci:compact-card-dependency-closure` | `ci_correctness` | 0 | 0 | 0 | 0 |
| 7 | complete | `correctness:replay-privacy-recovery` | `replay_privacy_defect` | 0 | 0 | 0 | 0 |
| 8 | complete | `architecture:dedicated-owner-extraction` | `architecture_owner_extraction` | 0 | 0 | 0 | 0 |
| 9 | blocked | `frontier:mechanic_dependency:cr-611-continuous-effects` | `rules_foundation` | 199 | 346 | 0 | 0 |
| 10 | blocked | `frontier:mechanic_dependency:cr-509-declare-blockers-step` | `rules_foundation` | 168 | 417 | 0 | 0 |
| 11 | blocked | `frontier:mechanic_dependency:cr-111-tokens` | `rules_foundation` | 122 | 338 | 0 | 0 |

Selected reason: Uncovered high-risk interactions have not fallen below the verified stabilization baseline.

## Top blockers

- Inventory every represented permanent- and player-counter producer and identify which paths still bypass the canonical counter-placement owner.
- Route one coherent reusable producer family through the immutable resumable counter-placement transaction without adding direct GameState writes.
- Preserve cost timing, entry timing, simultaneous APNAP ordering, rollback, privacy, and exact replay for migrated producers.
- Add generic CardProgram lowering and precise source spans where the migrated family originates in Oracle text.
- Add focused positive, negative, interaction, multiplayer, rollback, replay, and killed implementation-mutation evidence for the migrated boundary.

Complete rule, subsystem, dependency, classification, and selected-batch data plus complete readiness, blocker-card, architecture, interaction, and reranking fields for every serious candidate are in the [machine-readable rules queue](../coverage/rules-dependency-queue.json).

Exact generation command:

```powershell
.\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write
```
