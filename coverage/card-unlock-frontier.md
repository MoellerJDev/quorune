---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "c894abb7ded56bd90cc383192603a405c410636f822217441b8e6f9be1ed30dd"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":4421,"partial":12529,"unresolved":14673}`
- CardProgram states: `{"residual":27202,"trusted":4421}`
- Hard construction failures: 0
- Frontier fingerprint: `c894abb7ded56bd90cc383192603a405c410636f822217441b8e6f9be1ed30dd`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 8,908 | 7,188 | 3,688 | 8,908 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 515 | 473 | 240 | 381 | partial | high |
| `replacement:damage-prevention` | 209 | 204 | 45 | 75 | missing_lowering | very_high |
| `keyword_dependency:morph` | 141 | 141 | 36 | 141 | missing_contract | medium |
| `activated_effect:tap-state` | 318 | 308 | 35 | 55 | missing_lowering | high |
| `activated_effect:deal-damage` | 428 | 413 | 28 | 44 | missing_lowering | high |
| `mechanic_dependency:cr-615-prevention-effects` | 78 | 76 | 28 | 31 | partial | high |
| `activated_effect:unparsed-target-creature-can` | 56 | 56 | 27 | 44 | missing_lowering | high |
| `activated_effect:return` | 417 | 416 | 26 | 47 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 123 | 123 | 26 | 26 | missing_lowering | high |
| `effect_clause:life-change` | 579 | 576 | 20 | 60 | missing_lowering | high |
| `keyword_dependency:unearth` | 55 | 55 | 19 | 55 | missing_contract | medium |
| `keyword_dependency:cascade` | 37 | 37 | 19 | 37 | missing_contract | medium |
| `activated_effect:life-change` | 270 | 254 | 18 | 35 | missing_lowering | high |
| `effect_clause:exile` | 636 | 616 | 17 | 100 | missing_lowering | high |
| `keyword_dependency:bestow` | 42 | 42 | 17 | 42 | missing_contract | medium |
| `activated_effect:create-token` | 331 | 324 | 16 | 66 | missing_lowering | high |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `effect_clause:return` | 643 | 618 | 16 | 28 | missing_lowering | high |
| `effect_clause:create-token` | 597 | 581 | 15 | 101 | missing_lowering | high |
| `activated_effect:exile` | 386 | 357 | 15 | 43 | missing_lowering | high |
| `activated_effect:unparsed-surveil-1` | 25 | 25 | 15 | 21 | missing_lowering | high |
| `activated_effect:put-onto-battlefield` | 288 | 286 | 14 | 32 | missing_lowering | high |
| `mechanic_dependency:cr-400-general` | 26 | 26 | 14 | 26 | partial | high |
| `activated_effect:unparsed-this-creature-can` | 39 | 39 | 14 | 23 | missing_lowering | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, replacement:damage-prevention` | 4,003 | 9,364 | 9,376 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:morph` | 3,996 | 9,430 | 9,430 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,995 | 9,344 | 9,360 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:return` | 3,989 | 9,336 | 9,357 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:bestow` | 3,988 | 9,331 | 9,331 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-target-creature-can` | 3,987 | 9,333 | 9,337 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:deal-damage` | 3,986 | 9,333 | 9,363 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:unearth` | 3,985 | 9,344 | 9,344 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-615-prevention-effects` | 3,985 | 9,320 | 9,320 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:create-token` | 3,984 | 9,355 | 9,369 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,983 | 9,315 | 9,412 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:cascade` | 3,982 | 9,326 | 9,326 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:changeling` | 3,979 | 9,351 | 9,351 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:start-your-engines` | 3,978 | 9,329 | 9,329 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:life-change` | 3,977 | 9,349 | 9,350 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:exile` | 3,977 | 9,332 | 9,341 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:life-change` | 3,975 | 9,324 | 9,332 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:equip` | 3,975 | 9,314 | 9,314 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 3,974 | 9,389 | 9,389 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:affinity-unsupported-wording` | 3,974 | 9,325 | 9,325 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
