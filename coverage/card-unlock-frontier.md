---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "983f6f713812cf987516910fd122a94d6c7f2c78d749ce140350feb9dad83ce6"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":3848,"partial":12427,"unresolved":15348}`
- CardProgram states: `{"residual":27775,"trusted":3848}`
- Hard construction failures: 0
- Frontier fingerprint: `983f6f713812cf987516910fd122a94d6c7f2c78d749ce140350feb9dad83ce6`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,123 | 7,371 | 3,639 | 9,123 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 480 | 440 | 207 | 346 | partial | high |
| `mechanic_dependency:cr-111-tokens` | 338 | 333 | 124 | 338 | partial | high |
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
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 4,043 | 9,807 | 9,807 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:create-token` | 3,925 | 9,612 | 9,668 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, replacement:damage-prevention` | 3,919 | 9,544 | 9,556 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:morph` | 3,912 | 9,610 | 9,610 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:create-token` | 3,911 | 9,619 | 9,619 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,910 | 9,524 | 9,540 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:return` | 3,904 | 9,516 | 9,537 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:bestow` | 3,904 | 9,511 | 9,511 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-target-creature-can` | 3,903 | 9,513 | 9,517 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:deal-damage` | 3,902 | 9,513 | 9,543 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-615-prevention-effects` | 3,901 | 9,500 | 9,500 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:unearth` | 3,899 | 9,524 | 9,524 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,899 | 9,495 | 9,592 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:cascade` | 3,898 | 9,506 | 9,506 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:changeling` | 3,895 | 9,531 | 9,531 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,894 | 9,599 | 9,599 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:life-change` | 3,892 | 9,529 | 9,530 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:exile` | 3,892 | 9,512 | 9,521 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:start-your-engines` | 3,892 | 9,509 | 9,509 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:equip` | 3,891 | 9,494 | 9,494 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
