---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "f685096401095ef85d1b77814a8833fdd5503fdfdb43ed1aa3ae6835078ffdcf"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":4198,"partial":12501,"unresolved":14924}`
- CardProgram states: `{"residual":27425,"trusted":4198}`
- Hard construction failures: 0
- Frontier fingerprint: `f685096401095ef85d1b77814a8833fdd5503fdfdb43ed1aa3ae6835078ffdcf`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,049 | 7,303 | 3,743 | 9,049 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 515 | 473 | 237 | 381 | partial | high |
| `replacement:damage-prevention` | 209 | 204 | 45 | 75 | missing_lowering | very_high |
| `keyword_dependency:morph` | 141 | 141 | 36 | 141 | missing_contract | medium |
| `activated_effect:tap-state` | 318 | 308 | 34 | 55 | missing_lowering | high |
| `activated_effect:deal-damage` | 436 | 420 | 28 | 44 | missing_lowering | high |
| `mechanic_dependency:cr-615-prevention-effects` | 78 | 76 | 28 | 31 | partial | high |
| `activated_effect:unparsed-target-creature-can` | 56 | 56 | 27 | 44 | missing_lowering | high |
| `activated_effect:return` | 417 | 416 | 26 | 47 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 123 | 123 | 26 | 26 | missing_lowering | high |
| `effect_clause:destroy-target` | 582 | 550 | 21 | 130 | missing_lowering | high |
| `effect_clause:life-change` | 621 | 618 | 19 | 60 | missing_lowering | high |
| `keyword_dependency:unearth` | 55 | 55 | 19 | 55 | missing_contract | medium |
| `keyword_dependency:cascade` | 37 | 37 | 18 | 37 | missing_contract | medium |
| `effect_clause:exile` | 638 | 618 | 17 | 100 | missing_lowering | high |
| `keyword_dependency:bestow` | 42 | 42 | 17 | 42 | missing_contract | medium |
| `activated_effect:life-change` | 278 | 259 | 17 | 35 | missing_lowering | high |
| `activated_effect:create-token` | 341 | 334 | 16 | 66 | missing_lowering | high |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `effect_clause:return` | 650 | 625 | 16 | 28 | missing_lowering | high |
| `effect_clause:create-token` | 623 | 607 | 15 | 101 | missing_lowering | high |
| `activated_effect:exile` | 386 | 357 | 15 | 43 | missing_lowering | high |
| `activated_effect:unparsed-surveil-1` | 25 | 25 | 15 | 21 | missing_lowering | high |
| `activated_effect:put-onto-battlefield` | 288 | 286 | 14 | 32 | missing_lowering | high |
| `mechanic_dependency:cr-400-general` | 26 | 26 | 14 | 26 | partial | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, replacement:damage-prevention` | 4,055 | 9,505 | 9,517 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:morph` | 4,048 | 9,571 | 9,571 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 4,046 | 9,485 | 9,501 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:return` | 4,041 | 9,477 | 9,498 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:bestow` | 4,040 | 9,472 | 9,472 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-target-creature-can` | 4,039 | 9,474 | 9,478 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:deal-damage` | 4,038 | 9,474 | 9,504 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:unearth` | 4,037 | 9,485 | 9,485 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-615-prevention-effects` | 4,037 | 9,461 | 9,461 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:create-token` | 4,035 | 9,496 | 9,510 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 4,035 | 9,456 | 9,553 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:cascade` | 4,034 | 9,467 | 9,467 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:changeling` | 4,031 | 9,492 | 9,492 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 4,030 | 9,560 | 9,560 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:start-your-engines` | 4,030 | 9,470 | 9,470 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:exile` | 4,029 | 9,473 | 9,482 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:life-change` | 4,028 | 9,490 | 9,491 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:equip` | 4,027 | 9,455 | 9,455 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 4,026 | 9,530 | 9,530 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:affinity-unsupported-wording` | 4,026 | 9,466 | 9,466 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
