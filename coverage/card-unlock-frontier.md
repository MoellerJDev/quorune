---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "8f0137b6c989046c3c639234a95862e8d47410a9fd5d59d1d40bbaf2af488ae7"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":3823,"partial":12422,"unresolved":15378}`
- CardProgram states: `{"residual":27800,"trusted":3823}`
- Hard construction failures: 0
- Frontier fingerprint: `8f0137b6c989046c3c639234a95862e8d47410a9fd5d59d1d40bbaf2af488ae7`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,180 | 7,389 | 3,657 | 9,180 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 480 | 440 | 207 | 346 | partial | high |
| `mechanic_dependency:cr-111-tokens` | 338 | 333 | 123 | 338 | partial | high |
| `effect_clause:typed-spell-result-clause` | 157 | 157 | 66 | 66 | missing_lowering | high |
| `replacement:damage-prevention` | 208 | 203 | 45 | 75 | missing_lowering | very_high |
| `activated_effect:create-token` | 474 | 463 | 36 | 143 | missing_lowering | high |
| `keyword_dependency:morph` | 141 | 141 | 36 | 141 | missing_contract | medium |
| `effect_clause:create-token` | 657 | 641 | 35 | 150 | missing_lowering | high |
| `activated_effect:tap-state` | 322 | 311 | 34 | 55 | missing_lowering | high |
| `activated_effect:deal-damage` | 436 | 420 | 28 | 44 | missing_lowering | high |
| `mechanic_dependency:cr-615-prevention-effects` | 78 | 76 | 28 | 31 | partial | high |
| `activated_effect:unparsed-target-creature-can` | 56 | 56 | 27 | 44 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 123 | 123 | 26 | 26 | missing_lowering | high |
| `activated_effect:return` | 418 | 417 | 25 | 47 | missing_lowering | high |
| `effect_clause:destroy-target` | 569 | 537 | 20 | 129 | missing_lowering | high |
| `effect_clause:life-change` | 601 | 598 | 19 | 60 | missing_lowering | high |
| `keyword_dependency:cascade` | 37 | 37 | 18 | 37 | missing_contract | medium |
| `keyword_dependency:unearth` | 55 | 55 | 17 | 55 | missing_contract | medium |
| `keyword_dependency:bestow` | 42 | 42 | 17 | 42 | missing_contract | medium |
| `effect_clause:exile` | 622 | 602 | 16 | 99 | missing_lowering | high |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `activated_effect:life-change` | 280 | 260 | 16 | 35 | missing_lowering | high |
| `effect_clause:return` | 637 | 612 | 16 | 28 | missing_lowering | high |
| `activated_effect:unparsed-surveil-1` | 25 | 25 | 15 | 21 | missing_lowering | high |
| `activated_effect:exile` | 386 | 357 | 14 | 43 | missing_lowering | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 4,060 | 9,864 | 9,864 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-result-clause` | 3,957 | 9,592 | 9,683 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:create-token` | 3,943 | 9,669 | 9,725 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, replacement:damage-prevention` | 3,937 | 9,601 | 9,613 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:morph` | 3,930 | 9,667 | 9,667 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:create-token` | 3,929 | 9,676 | 9,676 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,928 | 9,581 | 9,597 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:return` | 3,922 | 9,573 | 9,594 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:bestow` | 3,922 | 9,568 | 9,568 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-target-creature-can` | 3,921 | 9,570 | 9,574 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:deal-damage` | 3,920 | 9,570 | 9,600 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-615-prevention-effects` | 3,919 | 9,557 | 9,557 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:unearth` | 3,917 | 9,581 | 9,581 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,917 | 9,552 | 9,649 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:cascade` | 3,916 | 9,563 | 9,563 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:changeling` | 3,913 | 9,588 | 9,588 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,911 | 9,655 | 9,655 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:life-change` | 3,910 | 9,586 | 9,586 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:exile` | 3,910 | 9,569 | 9,578 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:start-your-engines` | 3,910 | 9,566 | 9,566 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
