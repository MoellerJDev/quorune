---
title: "Rules dependency queue"
status: "generated"
authoritative_source: "coverage/rules-dependency-queue.json"
verified: "010770135bf2283af0f570489837911d52af79aa04bb05f11fbaa289dc56bcfc"
audience: "rules, compiler, and engine contributors"
maintenance: "generated"
generated_source: "coverage/rules-dependency-queue.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write"
---

# Rules dependency queue

Source fingerprint: `d118f6683a0280a4aebde045c5709b9f3421f7bb0b86f12daa2c0989977c4e98`

## Current top-level state

- Pinned rules: `3309`
- Queued rules: `2903`
- Subsystems: `21`
- Selected subsystem: `replacement-prevention`
- Selected batch: `counter-producer-replacement-closure`
- Selected cross-program work: `interaction-implementation:residual.replacement.replacement-applicability`
- Selected work class: `rules_foundation`

## Cross-program work selection

The rules batch remains dependency-ready, but final foreground work is reranked with deterministic CI, replay/privacy, architecture, runtime-text, interaction-assurance, compiler, and card-frontier evidence. A larger card gain cannot outrank a higher-priority correctness class.

Priority classes: `ci_correctness` → `replay_privacy_defect` → `architecture_owner_extraction` → `runtime_oracle_removal` → `interaction_assurance` → `rules_foundation` → `compiler_harvest` → `card_family` → `architecture_debt`

| Rank | State | Candidate | Class | Complete cards | Residuals | Runtime text | Direct writes |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | selected | `interaction-implementation:residual.replacement.replacement-applicability` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 2 | deferred | `interaction-implementation:residual.replacement.self-replacement-and-prevention-ordering` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 3 | deferred | `interaction-implementation:residual.replacement.damage-prevention` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 4 | deferred | `interaction-implementation:residual.replacement.regeneration` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 5 | deferred | `interaction-implementation:residual.continuous_layer.affected-player-ordering` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 6 | deferred | `interaction-implementation:residual.continuous_layer.continuous-effect-layers-and-dependencies` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 7 | deferred | `interaction-implementation:residual.duration.until-end-of-turn` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 8 | deferred | `interaction-implementation:residual.target_or_choice.target-predicate` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 9 | deferred | `interaction-implementation:residual.target_or_choice.conditional-effect` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 10 | deferred | `interaction-implementation:residual.event_binding.intervening-if-and-reflexive-trigger-grammar` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 11 | deferred | `interaction-implementation:residual.event_binding.normalized-event-binding` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 12 | deferred | `interaction-implementation:residual.activated_cost.complete-alternate-additional-cost-grammar` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 13 | deferred | `interaction-implementation:residual.activated_cost.restricted-payment-predicates` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 14 | deferred | `interaction-implementation:residual.static_clause.broader-evasion-and-group-constraints` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 15 | deferred | `interaction-implementation:residual.static_clause.conditional-declaration-predicates` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 16 | deferred | `interaction-implementation:residual.static_clause.temporary-declaration-restrictions` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 17 | deferred | `interaction-implementation:residual.target_or_choice.multiple-targets` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 18 | deferred | `interaction-implementation:residual.target_or_choice.divided-damage-allocation` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 19 | deferred | `interaction-implementation:residual.target_or_choice.multiple-damage-recipients` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 20 | deferred | `interaction-implementation:residual.target_or_choice.random-outcome` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 21 | deferred | `interaction-implementation:residual.target_or_choice.typed-enchant-restriction` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 22 | deferred | `architecture:engine-mutation-and-specificity-debt` | `architecture_debt` | 0 | 0 | 0 | 54 |
| 23 | complete | `ci:compact-card-dependency-closure` | `ci_correctness` | 0 | 0 | 0 | 0 |
| 24 | complete | `correctness:replay-privacy-recovery` | `replay_privacy_defect` | 0 | 0 | 0 | 0 |
| 25 | complete | `architecture:dedicated-owner-extraction` | `architecture_owner_extraction` | 0 | 0 | 0 | 0 |
| 26 | complete | `assurance:critical-interaction-recovery` | `interaction_assurance` | 0 | 0 | 0 | 0 |
| 27 | blocked | `frontier:target_or_choice:typed-enchant-restriction` | `rules_foundation` | 5 | 111 | 0 | 0 |
| 28 | blocked | `rules:counter-producer-replacement-closure` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 29 | blocked | `frontier:effect_clause:typed-spell-additional-cost-clause` | `compiler_harvest` | 16 | 106 | 0 | 0 |
| 30 | blocked | `frontier:effect_clause:unparsed-choose-one` | `compiler_harvest` | 0 | 263 | 0 | 0 |

Selected reason: 41 applicable high-risk pairs touching up to 1247 corpus cards are currently safe only because at least one side, including residual.replacement.replacement-applicability, is rejected. Implement this shared boundary and replace eligible fail-closed edges with real behavioral tests.

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
