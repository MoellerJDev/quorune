---
title: "Rules dependency queue"
status: "generated"
authoritative_source: "coverage/rules-dependency-queue.json"
verified: "26011f8aa2d787beeca522638654498c8afbc8decb1a888a9e17e753c9756f54"
audience: "rules, compiler, and engine contributors"
maintenance: "generated"
generated_source: "coverage/rules-dependency-queue.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write"
---

# Rules dependency queue

Source fingerprint: `99df957d2eaa287b7dc28ccbf4a1ecb5c824c09ee23653ea09f8d96e92431f81`

## Current top-level state

- Pinned rules: `3309`
- Queued rules: `2900`
- Subsystems: `21`
- Selected subsystem: `replacement-prevention`
- Selected batch: `counter-producer-replacement-closure`
- Selected cross-program work: `bundle:fixed-token-creation-contexts`
- Selected work class: `compiler_harvest`

## Cross-program work selection

The rules batch remains dependency-ready, but final foreground work is reranked with deterministic CI, replay/privacy, architecture, runtime-text, interaction-assurance, compiler, and card-frontier evidence. A larger card gain cannot outrank a higher-priority correctness class.

Priority classes: `ci_correctness` → `replay_privacy_defect` → `architecture_owner_extraction` → `runtime_oracle_removal` → `interaction_assurance` → `rules_foundation` → `compiler_harvest` → `card_family` → `architecture_debt`

| Rank | State | Candidate | Class | Members | Contexts | Complete cards | Residuals | Cards/hour | Runtime text | Direct writes |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | selected | `bundle:fixed-token-creation-contexts` | `compiler_harvest` | 2 | 4 | 39 | 167 | 2.294118 | 0 | 0 |
| 2 | deferred | `bundle:fixed-exile-contexts` | `compiler_harvest` | 2 | 4 | 14 | 106 | 0.933333 | 0 | 0 |
| 3 | deferred | `frontier:effect_clause:typed-spell-additional-cost-clause` | `compiler_harvest` | 1 | 3 | 16 | 106 | 0.761905 | 0 | 0 |
| 4 | complete | `ci:compact-card-dependency-closure` | `ci_correctness` | 1 | 0 | 0 | 0 | unknown | 0 | 0 |
| 5 | complete | `correctness:replay-privacy-recovery` | `replay_privacy_defect` | 1 | 0 | 0 | 0 | unknown | 0 | 0 |
| 6 | complete | `architecture:dedicated-owner-extraction` | `architecture_owner_extraction` | 1 | 0 | 0 | 0 | unknown | 0 | 0 |
| 7 | complete | `assurance:critical-interaction-recovery` | `interaction_assurance` | 1 | 0 | 0 | 0 | unknown | 0 | 0 |
| 8 | blocked | `interaction-implementation:residual.replacement.replacement-applicability` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 9 | blocked | `interaction-implementation:residual.replacement.self-replacement-and-prevention-ordering` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 10 | blocked | `interaction-implementation:residual.replacement.damage-prevention` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 11 | blocked | `interaction-implementation:residual.continuous_layer.affected-player-ordering` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 12 | blocked | `interaction-implementation:residual.replacement.regeneration` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 13 | blocked | `interaction-implementation:residual.continuous_layer.continuous-effect-layers-and-dependencies` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 14 | blocked | `interaction-implementation:residual.duration.until-end-of-turn` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 15 | blocked | `interaction-implementation:residual.target_or_choice.target-predicate` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 16 | blocked | `interaction-implementation:residual.target_or_choice.conditional-effect` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 17 | blocked | `interaction-implementation:residual.event_binding.intervening-if-and-reflexive-trigger-grammar` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 18 | blocked | `interaction-implementation:residual.event_binding.normalized-event-binding` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 19 | blocked | `interaction-implementation:residual.static_clause.broader-evasion-and-group-constraints` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 20 | blocked | `interaction-implementation:residual.static_clause.conditional-declaration-predicates` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 21 | blocked | `interaction-implementation:residual.static_clause.temporary-declaration-restrictions` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 22 | blocked | `interaction-implementation:residual.activated_cost.complete-alternate-additional-cost-grammar` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 23 | blocked | `interaction-implementation:residual.activated_cost.restricted-payment-predicates` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 24 | blocked | `interaction-implementation:residual.target_or_choice.multiple-targets` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 25 | blocked | `interaction-implementation:residual.target_or_choice.divided-damage-allocation` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 26 | blocked | `interaction-implementation:residual.target_or_choice.multiple-damage-recipients` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 27 | blocked | `interaction-implementation:residual.target_or_choice.random-outcome` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 28 | blocked | `rules:counter-producer-replacement-closure` | `rules_foundation` | 1 | 0 | unknown | unknown | unknown | 0 | 0 |
| 29 | blocked | `frontier:effect_clause:unparsed-choose-one` | `compiler_harvest` | 1 | 3 | 0 | 261 | 0.0 | 0 | 0 |
| 30 | blocked | `architecture:engine-mutation-and-specificity-debt` | `architecture_debt` | 1 | 0 | 0 | 0 | unknown | 0 | 54 |

Selected reason: Meets the measured major exact-ability floor inside one reusable grammar boundary. The bundle shares 2 canonical owners across 4 source contexts and is predicted at 2.294118 complete cards per cycle hour.

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
