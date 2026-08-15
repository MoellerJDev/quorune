---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "1f481469db9e7a466e308530584825ecbb7ae764dcf31da67ddcc86c8a18c31e"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":3944,"partial":12570,"unresolved":15109}`
- CardProgram states: `{"residual":27679,"trusted":3944}`
- Hard construction failures: 0
- Frontier fingerprint: `1f481469db9e7a466e308530584825ecbb7ae764dcf31da67ddcc86c8a18c31e`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,049 | 7,303 | 3,660 | 9,049 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 515 | 473 | 234 | 381 | partial | high |
| `mechanic_dependency:cr-111-tokens` | 338 | 333 | 127 | 338 | partial | high |
| `replacement:damage-prevention` | 209 | 204 | 45 | 75 | missing_lowering | very_high |
| `activated_effect:create-token` | 473 | 462 | 36 | 143 | missing_lowering | high |
| `keyword_dependency:morph` | 141 | 141 | 36 | 141 | missing_contract | medium |
| `effect_clause:create-token` | 672 | 656 | 35 | 150 | missing_lowering | high |
| `activated_effect:tap-state` | 318 | 308 | 34 | 55 | missing_lowering | high |
| `activated_effect:deal-damage` | 436 | 420 | 28 | 44 | missing_lowering | high |
| `mechanic_dependency:cr-615-prevention-effects` | 78 | 76 | 28 | 31 | partial | high |
| `activated_effect:unparsed-target-creature-can` | 56 | 56 | 27 | 44 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 123 | 123 | 26 | 26 | missing_lowering | high |
| `activated_effect:return` | 417 | 416 | 25 | 47 | missing_lowering | high |
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
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 4,094 | 9,768 | 9,768 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:create-token` | 3,975 | 9,573 | 9,629 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, replacement:damage-prevention` | 3,969 | 9,505 | 9,517 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:morph` | 3,962 | 9,571 | 9,571 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:create-token` | 3,961 | 9,580 | 9,580 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,960 | 9,485 | 9,501 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:return` | 3,954 | 9,477 | 9,498 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:bestow` | 3,954 | 9,472 | 9,472 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-target-creature-can` | 3,953 | 9,474 | 9,478 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:deal-damage` | 3,952 | 9,474 | 9,504 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-615-prevention-effects` | 3,951 | 9,461 | 9,461 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:unearth` | 3,949 | 9,485 | 9,485 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,949 | 9,456 | 9,553 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:cascade` | 3,948 | 9,467 | 9,467 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:changeling` | 3,945 | 9,492 | 9,492 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,944 | 9,560 | 9,560 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:life-change` | 3,942 | 9,490 | 9,491 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:exile` | 3,942 | 9,473 | 9,482 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:start-your-engines` | 3,942 | 9,470 | 9,470 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:equip` | 3,941 | 9,455 | 9,455 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
