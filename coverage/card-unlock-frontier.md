---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "c007cc7a275b78ed6232096e91580be0f0a0d90d593e1b39e455b3aadce40496"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":3677,"partial":12458,"unresolved":15488}`
- CardProgram states: `{"residual":27946,"trusted":3677}`
- Hard construction failures: 0
- Frontier fingerprint: `c007cc7a275b78ed6232096e91580be0f0a0d90d593e1b39e455b3aadce40496`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,180 | 7,389 | 3,627 | 9,180 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 480 | 440 | 204 | 346 | partial | high |
| `mechanic_dependency:cr-111-tokens` | 338 | 333 | 123 | 338 | partial | high |
| `effect_clause:typed-spell-additional-cost-clause` | 123 | 123 | 122 | 123 | missing_lowering | high |
| `effect_clause:deal-damage` | 956 | 925 | 112 | 245 | missing_lowering | high |
| `effect_clause:exile` | 985 | 939 | 105 | 430 | missing_lowering | high |
| `effect_clause:destroy-target` | 572 | 540 | 98 | 249 | missing_lowering | high |
| `effect_clause:return` | 686 | 660 | 96 | 216 | missing_lowering | high |
| `activated_effect:deal-damage` | 479 | 460 | 88 | 139 | missing_lowering | high |
| `activated_effect:tap-state` | 322 | 311 | 84 | 164 | missing_lowering | high |
| `activated_effect:unparsed-regenerate-this-creature` | 149 | 148 | 76 | 129 | missing_lowering | high |
| `effect_clause:intrinsic-basic-land-type-mana-capability` | 106 | 106 | 70 | 106 | missing_lowering | high |
| `effect_clause:tap-state` | 373 | 364 | 69 | 136 | missing_lowering | high |
| `activated_effect:return` | 418 | 417 | 68 | 139 | missing_lowering | high |
| `effect_clause:typed-spell-result-clause` | 66 | 66 | 66 | 66 | missing_lowering | high |
| `activated_effect:unparsed-this-creature-gets` | 131 | 126 | 64 | 86 | missing_lowering | high |
| `effect_clause:look-reveal` | 550 | 546 | 62 | 94 | missing_lowering | high |
| `activated_effect:create-token` | 474 | 463 | 58 | 193 | missing_lowering | high |
| `effect_clause:create-token` | 695 | 679 | 45 | 158 | missing_lowering | high |
| `activated_effect:destroy-target` | 151 | 150 | 42 | 60 | missing_lowering | high |
| `activated_effect:unparsed-until-end-of` | 124 | 122 | 39 | 86 | missing_lowering | high |
| `effect_clause:draw` | 551 | 543 | 38 | 103 | missing_lowering | high |
| `effect_clause:unparsed-until-end-of` | 68 | 68 | 37 | 48 | missing_lowering | high |
| `keyword_dependency:morph` | 141 | 141 | 35 | 141 | missing_contract | medium |
| `activated_effect:exile` | 386 | 357 | 30 | 95 | missing_lowering | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 4,027 | 9,864 | 9,864 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,981 | 9,649 | 9,649 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:deal-damage` | 3,970 | 9,771 | 9,771 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 3,964 | 9,956 | 9,956 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,956 | 9,775 | 9,775 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,955 | 9,690 | 9,728 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:return` | 3,954 | 9,742 | 9,742 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-regenerate-this-creature` | 3,952 | 9,655 | 9,671 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:deal-damage` | 3,948 | 9,665 | 9,709 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:intrinsic-basic-land-type-mana-capability` | 3,943 | 9,632 | 9,632 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:return` | 3,939 | 9,665 | 9,703 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:create-token` | 3,932 | 9,719 | 9,792 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:tap-state` | 3,928 | 9,662 | 9,662 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-this-creature-gets` | 3,924 | 9,612 | 9,625 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-result-clause` | 3,924 | 9,592 | 9,592 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:look-reveal` | 3,920 | 9,620 | 9,620 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-111-tokens, effect_clause:typed-spell-additional-cost-clause` | 3,917 | 9,641 | 9,641 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-111-tokens, effect_clause:exile` | 3,912 | 9,948 | 9,948 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-until-end-of` | 3,911 | 9,612 | 9,622 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-111-tokens, effect_clause:deal-damage` | 3,906 | 9,763 | 9,763 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
