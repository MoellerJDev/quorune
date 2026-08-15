---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "fbf0f3c41e96e8166b5acd90c2efb3ee62a00e0a2fd92f4756d695045af7b9fd"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":3924,"partial":12558,"unresolved":15141}`
- CardProgram states: `{"residual":27699,"trusted":3924}`
- Hard construction failures: 0
- Frontier fingerprint: `fbf0f3c41e96e8166b5acd90c2efb3ee62a00e0a2fd92f4756d695045af7b9fd`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,049 | 7,303 | 3,652 | 9,049 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 480 | 440 | 207 | 346 | partial | high |
| `mechanic_dependency:cr-111-tokens` | 338 | 333 | 126 | 338 | partial | high |
| `replacement:damage-prevention` | 209 | 204 | 45 | 75 | missing_lowering | very_high |
| `activated_effect:create-token` | 474 | 463 | 36 | 143 | missing_lowering | high |
| `keyword_dependency:morph` | 141 | 141 | 36 | 141 | missing_contract | medium |
| `effect_clause:create-token` | 672 | 656 | 35 | 150 | missing_lowering | high |
| `activated_effect:tap-state` | 322 | 311 | 34 | 55 | missing_lowering | high |
| `activated_effect:deal-damage` | 436 | 420 | 28 | 44 | missing_lowering | high |
| `mechanic_dependency:cr-615-prevention-effects` | 78 | 76 | 28 | 31 | partial | high |
| `activated_effect:unparsed-target-creature-can` | 56 | 56 | 27 | 44 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 123 | 123 | 26 | 26 | missing_lowering | high |
| `activated_effect:return` | 418 | 417 | 25 | 47 | missing_lowering | high |
| `effect_clause:destroy-target` | 582 | 550 | 21 | 130 | missing_lowering | high |
| `effect_clause:life-change` | 621 | 618 | 19 | 60 | missing_lowering | high |
| `keyword_dependency:cascade` | 37 | 37 | 18 | 37 | missing_contract | medium |
| `effect_clause:exile` | 638 | 618 | 17 | 100 | missing_lowering | high |
| `keyword_dependency:unearth` | 55 | 55 | 17 | 55 | missing_contract | medium |
| `keyword_dependency:bestow` | 42 | 42 | 17 | 42 | missing_contract | medium |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `activated_effect:life-change` | 278 | 259 | 16 | 35 | missing_lowering | high |
| `effect_clause:return` | 650 | 625 | 16 | 28 | missing_lowering | high |
| `activated_effect:unparsed-surveil-1` | 25 | 25 | 15 | 21 | missing_lowering | high |
| `activated_effect:exile` | 386 | 357 | 14 | 43 | missing_lowering | high |
| `activated_effect:put-onto-battlefield` | 288 | 286 | 14 | 32 | missing_lowering | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 4,056 | 9,733 | 9,733 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:create-token` | 3,938 | 9,538 | 9,594 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, replacement:damage-prevention` | 3,932 | 9,470 | 9,482 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:morph` | 3,925 | 9,536 | 9,536 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:create-token` | 3,924 | 9,545 | 9,545 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,923 | 9,450 | 9,466 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:return` | 3,917 | 9,442 | 9,463 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:bestow` | 3,917 | 9,437 | 9,437 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-target-creature-can` | 3,916 | 9,439 | 9,443 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:deal-damage` | 3,915 | 9,439 | 9,469 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-615-prevention-effects` | 3,914 | 9,426 | 9,426 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:unearth` | 3,912 | 9,450 | 9,450 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,912 | 9,421 | 9,518 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:cascade` | 3,911 | 9,432 | 9,432 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:changeling` | 3,908 | 9,457 | 9,457 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,907 | 9,525 | 9,525 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:life-change` | 3,905 | 9,455 | 9,456 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:exile` | 3,905 | 9,438 | 9,447 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:start-your-engines` | 3,905 | 9,435 | 9,435 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:equip` | 3,904 | 9,420 | 9,420 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
