---
title: "Rules dependency queue"
status: "generated"
authoritative_source: "coverage/rules-dependency-queue.json"
verified: "a27913f303e8ebd11d2e12f26f4ba15f1f0fe170f61bc3365c6b87c038fe4788"
audience: "rules, compiler, and engine contributors"
maintenance: "generated"
generated_source: "coverage/rules-dependency-queue.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write"
---

# Rules dependency queue

Source fingerprint: `b5e92c086a216d130b6528891dfa753f8f617b23f2669e27ac3c96df69a4a030`

## Current top-level state

- Pinned rules: `3300`
- Queued rules: `2920`
- Subsystems: `21`
- Selected subsystem: `replacement-prevention`
- Selected batch: `counter-producer-replacement-closure`
- Selected cross-program work: `architecture:runtime-oracle-text-removal:casting_activation_and_costs`
- Selected work class: `runtime_oracle_removal`

## Cross-program work selection

The rules batch remains dependency-ready, but final foreground work is reranked with deterministic CI, replay/privacy, architecture, runtime-text, interaction-assurance, compiler, and card-frontier evidence. A larger card gain cannot outrank a higher-priority correctness class.

Priority classes: `ci_correctness` → `replay_privacy_defect` → `architecture_owner_extraction` → `runtime_oracle_removal` → `interaction_assurance` → `architecture_debt` → `rules_foundation` → `compiler_harvest` → `card_family`

| Rank | State | Candidate | Class | Complete cards | Residuals | Runtime text | Direct writes |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | selected | `architecture:runtime-oracle-text-removal:casting_activation_and_costs` | `runtime_oracle_removal` | 0 | 0 | 7 | 0 |
| 2 | deferred | `architecture:runtime-oracle-text-removal:replacement_and_prevention` | `runtime_oracle_removal` | 0 | 0 | 3 | 0 |
| 3 | deferred | `architecture:runtime-oracle-text-removal:semantic_effect_execution` | `runtime_oracle_removal` | 0 | 0 | 3 | 0 |
| 4 | deferred | `architecture:runtime-oracle-text-removal:tokens_and_token_creation` | `runtime_oracle_removal` | 0 | 0 | 3 | 0 |
| 5 | deferred | `architecture:runtime-oracle-text-removal:combat` | `runtime_oracle_removal` | 0 | 0 | 1 | 0 |
| 6 | deferred | `architecture:runtime-oracle-text-removal:damage_results_life_and_counters` | `runtime_oracle_removal` | 0 | 0 | 1 | 0 |
| 7 | deferred | `architecture:runtime-oracle-text-removal:state_based_actions` | `runtime_oracle_removal` | 0 | 0 | 1 | 0 |
| 8 | deferred | `architecture:runtime-oracle-text-removal:turn_priority_and_decisions` | `runtime_oracle_removal` | 0 | 0 | 1 | 0 |
| 9 | deferred | `architecture:runtime-oracle-text-subsystem-attribution` | `runtime_oracle_removal` | 0 | 0 | 30 | 0 |
| 10 | deferred | `architecture:engine-mutation-and-specificity-debt` | `architecture_debt` | 0 | 0 | 0 | 55 |
| 11 | deferred | `rules:counter-producer-replacement-closure` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 12 | deferred | `frontier:effect_clause:typed-spell-additional-cost-clause` | `compiler_harvest` | 122 | 123 | 0 | 0 |
| 13 | complete | `ci:compact-card-dependency-closure` | `ci_correctness` | 0 | 0 | 0 | 0 |
| 14 | complete | `correctness:replay-privacy-recovery` | `replay_privacy_defect` | 0 | 0 | 0 | 0 |
| 15 | complete | `architecture:dedicated-owner-extraction` | `architecture_owner_extraction` | 0 | 0 | 0 | 0 |
| 16 | complete | `assurance:high-risk-interaction-recovery` | `interaction_assurance` | 0 | 0 | 0 | 0 |
| 17 | blocked | `frontier:mechanic_dependency:cr-611-continuous-effects` | `rules_foundation` | 197 | 346 | 0 | 0 |
| 18 | blocked | `frontier:mechanic_dependency:cr-614-replacement-effects` | `rules_foundation` | 196 | 539 | 0 | 0 |
| 19 | blocked | `frontier:mechanic_dependency:cr-509-declare-blockers-step` | `rules_foundation` | 157 | 392 | 0 | 0 |
| 20 | blocked | `frontier:mechanic_dependency:cr-111-tokens` | `rules_foundation` | 117 | 338 | 0 | 0 |

Selected reason: 7 prohibited runtime-text accesses remain in the existing casting_activation_and_costs typed owner and outrank card expansion.

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
