---
title: "Rules dependency queue"
status: "generated"
authoritative_source: "coverage/rules-dependency-queue.json"
verified: "de09106951c97a37b4b57856655e607d0be7dc88495aab04331f5b409d36447b"
audience: "rules, compiler, and engine contributors"
maintenance: "generated"
generated_source: "coverage/rules-dependency-queue.json"
generation_command: ".\.venv\Scripts\python.exe scripts\update_rules_scheduler.py --write"
---

# Rules dependency queue

Source fingerprint: `ebb6a953f9a57dd743d3bd393c0d3e566da4dd95273535e58153d4c920fed614`

## Current top-level state

- Pinned rules: `3300`
- Queued rules: `2916`
- Subsystems: `21`
- Selected subsystem: `replacement-prevention`
- Selected batch: `counter-producer-replacement-closure`
- Selected cross-program work: `frontier:effect_clause:intrinsic-basic-land-type-mana-capability`
- Selected work class: `compiler_harvest`

## Cross-program work selection

The rules batch remains dependency-ready, but final foreground work is reranked with deterministic CI, replay/privacy, architecture, runtime-text, interaction-assurance, compiler, and card-frontier evidence. A larger card gain cannot outrank a higher-priority correctness class.

Priority classes: `ci_correctness` → `replay_privacy_defect` → `architecture_owner_extraction` → `runtime_oracle_removal` → `interaction_assurance` → `compiler_harvest` → `card_family` → `rules_foundation` → `architecture_debt`

| Rank | State | Candidate | Class | Complete cards | Residuals | Runtime text | Direct writes |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | selected | `frontier:effect_clause:intrinsic-basic-land-type-mana-capability` | `compiler_harvest` | 70 | 106 | 0 | 0 |
| 2 | deferred | `frontier:effect_clause:typed-spell-result-clause` | `compiler_harvest` | 66 | 157 | 0 | 0 |
| 3 | deferred | `rules:counter-producer-replacement-closure` | `rules_foundation` | unknown | unknown | 0 | 0 |
| 4 | deferred | `architecture:engine-mutation-and-specificity-debt` | `architecture_debt` | 0 | 0 | 0 | 55 |
| 5 | complete | `ci:compact-card-dependency-closure` | `ci_correctness` | 0 | 0 | 0 | 0 |
| 6 | complete | `correctness:replay-privacy-recovery` | `replay_privacy_defect` | 0 | 0 | 0 | 0 |
| 7 | complete | `architecture:dedicated-owner-extraction` | `architecture_owner_extraction` | 0 | 0 | 0 | 0 |
| 8 | complete | `assurance:critical-interaction-recovery` | `interaction_assurance` | 0 | 0 | 0 | 0 |
| 9 | blocked | `frontier:mechanic_dependency:cr-611-continuous-effects` | `rules_foundation` | 207 | 346 | 0 | 0 |
| 10 | blocked | `frontier:mechanic_dependency:cr-111-tokens` | `rules_foundation` | 123 | 338 | 0 | 0 |

Selected reason: Meets the post-stabilization 50-card threshold but remains behind higher-priority correctness and architecture gates.

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
