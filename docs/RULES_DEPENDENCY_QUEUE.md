---
title: "Rules dependency queue"
status: "generated"
authoritative_source: "coverage/rules-dependency-queue.json"
verified: "a54ed182bc4858bea0e67a582bfcd729dbb4d4643dd0573cf8621c64877387bb"
audience: "rules, compiler, and engine contributors"
maintenance: "generated"
generated_source: "coverage/rules-dependency-queue.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write"
---

# Rules dependency queue

Source fingerprint: `0f78dfcbb3fc31cc416a30aba3f092650be3769408e7b7698aff2c27c824726f`

## Current top-level state

- Pinned rules: `3300`
- Queued rules: `2919`
- Subsystems: `21`
- Selected subsystem: `replacement-prevention`
- Selected batch: `counter-producer-replacement-closure`
- Selected cross-program work: `architecture:runtime-oracle-text-removal:continuous_effects`
- Selected work class: `runtime_oracle_removal`

## Cross-program work selection

The rules batch remains dependency-ready, but final foreground work is reranked with deterministic CI, replay/privacy, architecture, runtime-text, interaction-assurance, compiler, and card-frontier evidence. A larger card gain cannot outrank a higher-priority correctness class.

Priority classes: `ci_correctness` → `replay_privacy_defect` → `architecture_owner_extraction` → `runtime_oracle_removal` → `interaction_assurance` → `architecture_debt` → `rules_foundation` → `compiler_harvest` → `card_family`

| Rank | State | Candidate | Class | Complete cards | Residuals | Runtime text | Direct writes |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | selected | `architecture:runtime-oracle-text-removal:continuous_effects` | `runtime_oracle_removal` | 0 | 0 | 4 | 0 |
| 2 | deferred | `architecture:runtime-oracle-text-removal:casting_activation_and_costs` | `runtime_oracle_removal` | 0 | 0 | 3 | 0 |
| 3 | deferred | `architecture:runtime-oracle-text-removal:combat` | `runtime_oracle_removal` | 0 | 0 | 3 | 0 |
| 4 | deferred | `architecture:runtime-oracle-text-removal:semantic_effect_execution` | `runtime_oracle_removal` | 0 | 0 | 3 | 0 |
| 5 | deferred | `architecture:runtime-oracle-text-removal:application_session` | `runtime_oracle_removal` | 0 | 0 | 2 | 0 |
| 6 | deferred | `assurance:critical-interaction-recovery` | `interaction_assurance` | 0 | 0 | 0 | 0 |
| 7 | deferred | `architecture:engine-mutation-and-specificity-debt` | `architecture_debt` | 0 | 0 | 0 | 55 |
| 8 | deferred | `rules:counter-producer-replacement-closure` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 9 | deferred | `frontier:effect_clause:typed-spell-additional-cost-clause` | `compiler_harvest` | 122 | 123 | 0 | 0 |
| 10 | deferred | `frontier:effect_clause:deal-damage` | `compiler_harvest` | 112 | 245 | 0 | 0 |
| 11 | complete | `ci:compact-card-dependency-closure` | `ci_correctness` | 0 | 0 | 0 | 0 |
| 12 | complete | `correctness:replay-privacy-recovery` | `replay_privacy_defect` | 0 | 0 | 0 | 0 |
| 13 | complete | `architecture:dedicated-owner-extraction` | `architecture_owner_extraction` | 0 | 0 | 0 | 0 |
| 14 | blocked | `frontier:mechanic_dependency:cr-611-continuous-effects` | `rules_foundation` | 199 | 346 | 0 | 0 |
| 15 | blocked | `frontier:mechanic_dependency:cr-509-declare-blockers-step` | `rules_foundation` | 157 | 392 | 0 | 0 |
| 16 | blocked | `frontier:mechanic_dependency:cr-111-tokens` | `rules_foundation` | 122 | 338 | 0 | 0 |

Selected reason: 4 prohibited runtime-text accesses remain in the existing continuous_effects typed owner and outrank card expansion.

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
