---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "70f3bf1ec1c12e9ebae5bd59d850833cde818eba8b83cab9647ba6d27614bb8c"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":3416,"partial":12719,"unresolved":15488}`
- CardProgram states: `{"residual":28207,"trusted":3416}`
- Hard construction failures: 0
- Frontier fingerprint: `70f3bf1ec1c12e9ebae5bd59d850833cde818eba8b83cab9647ba6d27614bb8c`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,180 | 7,389 | 3,552 | 9,180 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 480 | 440 | 199 | 346 | partial | high |
| `mechanic_dependency:cr-509-declare-blockers-step` | 453 | 447 | 168 | 417 | partial | high |
| `mechanic_dependency:cr-111-tokens` | 338 | 333 | 122 | 338 | partial | high |
| `effect_clause:typed-spell-additional-cost-clause` | 123 | 123 | 122 | 123 | missing_lowering | high |
| `effect_clause:deal-damage` | 956 | 925 | 112 | 245 | missing_lowering | high |
| `effect_clause:exile` | 985 | 939 | 105 | 430 | missing_lowering | high |
| `effect_clause:destroy-target` | 572 | 540 | 98 | 249 | missing_lowering | high |
| `effect_clause:return` | 686 | 660 | 96 | 216 | missing_lowering | high |
| `activated_effect:deal-damage` | 479 | 460 | 87 | 139 | missing_lowering | high |
| `activated_effect:tap-state` | 322 | 311 | 83 | 164 | missing_lowering | high |
| `activated_effect:unparsed-regenerate-this-creature` | 149 | 148 | 75 | 129 | missing_lowering | high |
| `effect_clause:intrinsic-basic-land-type-mana-capability` | 106 | 106 | 70 | 106 | missing_lowering | high |
| `effect_clause:tap-state` | 373 | 364 | 69 | 136 | missing_lowering | high |
| `effect_clause:typed-spell-result-clause` | 66 | 66 | 66 | 66 | missing_lowering | high |
| `activated_effect:return` | 418 | 417 | 65 | 139 | missing_lowering | high |
| `mechanic_dependency:cr-508-declare-attackers-step` | 198 | 198 | 64 | 162 | partial | high |
| `activated_effect:unparsed-this-creature-gets` | 131 | 126 | 64 | 86 | missing_lowering | high |
| `effect_clause:look-reveal` | 550 | 546 | 62 | 94 | missing_lowering | high |
| `activated_effect:create-token` | 474 | 463 | 58 | 193 | missing_lowering | high |
| `effect_clause:create-token` | 695 | 679 | 45 | 158 | missing_lowering | high |
| `activated_effect:destroy-target` | 151 | 150 | 42 | 60 | missing_lowering | high |
| `effect_clause:draw` | 551 | 543 | 38 | 103 | missing_lowering | high |
| `activated_effect:unparsed-until-end-of` | 124 | 122 | 38 | 86 | missing_lowering | high |
| `effect_clause:unparsed-until-end-of` | 68 | 68 | 37 | 48 | missing_lowering | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-509-declare-blockers-step` | 4,003 | 9,943 | 9,943 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 3,946 | 9,864 | 9,864 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, mechanic_dependency:cr-111-tokens` | 3,938 | 9,935 | 9,935 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,901 | 9,649 | 9,649 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:typed-spell-additional-cost-clause` | 3,895 | 9,720 | 9,720 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:deal-damage` | 3,890 | 9,771 | 9,771 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, mechanic_dependency:cr-508-declare-attackers-step` | 3,888 | 9,795 | 9,795 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 3,884 | 9,956 | 9,956 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:deal-damage` | 3,884 | 9,842 | 9,842 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:exile` | 3,878 | 10,027 | 10,027 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,876 | 9,775 | 9,775 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:return` | 3,874 | 9,742 | 9,742 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,874 | 9,690 | 9,728 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-regenerate-this-creature` | 3,871 | 9,655 | 9,671 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:destroy-target` | 3,870 | 9,846 | 9,846 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, activated_effect:tap-state` | 3,869 | 9,761 | 9,799 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:return` | 3,868 | 9,813 | 9,813 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:deal-damage` | 3,867 | 9,665 | 9,709 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:intrinsic-basic-land-type-mana-capability` | 3,863 | 9,632 | 9,632 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, activated_effect:unparsed-regenerate-this-creature` | 3,862 | 9,726 | 9,742 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
