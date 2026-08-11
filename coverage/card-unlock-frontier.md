---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "ba2a894266cc56fa11b5016acf225ded8d99e2dd8d4ffd973ddceb8e6d5a187e"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":3162,"partial":12861,"unresolved":15600}`
- CardProgram states: `{"residual":28461,"trusted":3162}`
- Hard construction failures: 0
- Frontier fingerprint: `ba2a894266cc56fa11b5016acf225ded8d99e2dd8d4ffd973ddceb8e6d5a187e`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,492 | 7,643 | 3,638 | 9,492 | missing_lowering | very_high |
| `mechanic_dependency:cr-614-replacement-effects` | 539 | 539 | 203 | 539 | partial | high |
| `mechanic_dependency:cr-611-continuous-effects` | 480 | 440 | 197 | 346 | partial | high |
| `mechanic_dependency:cr-509-declare-blockers-step` | 428 | 423 | 157 | 392 | partial | high |
| `effect_clause:typed-spell-additional-cost-clause` | 123 | 123 | 122 | 123 | missing_lowering | high |
| `mechanic_dependency:cr-111-tokens` | 338 | 333 | 119 | 338 | partial | high |
| `effect_clause:deal-damage` | 956 | 925 | 112 | 245 | missing_lowering | high |
| `effect_clause:exile` | 985 | 939 | 104 | 430 | missing_lowering | high |
| `effect_clause:destroy-target` | 572 | 540 | 98 | 249 | missing_lowering | high |
| `effect_clause:return` | 686 | 660 | 96 | 216 | missing_lowering | high |
| `activated_effect:deal-damage` | 479 | 460 | 86 | 139 | missing_lowering | high |
| `activated_effect:tap-state` | 322 | 311 | 77 | 164 | missing_lowering | high |
| `activated_effect:unparsed-regenerate-this-creature` | 149 | 148 | 75 | 129 | missing_lowering | high |
| `effect_clause:tap-state` | 373 | 364 | 68 | 136 | missing_lowering | high |
| `effect_clause:typed-spell-result-clause` | 66 | 66 | 65 | 66 | missing_lowering | high |
| `activated_effect:return` | 418 | 417 | 64 | 139 | missing_lowering | high |
| `activated_effect:unparsed-this-creature-gets` | 131 | 126 | 64 | 86 | missing_lowering | high |
| `effect_clause:look-reveal` | 550 | 546 | 60 | 94 | missing_lowering | high |
| `activated_effect:create-token` | 474 | 463 | 55 | 193 | missing_lowering | high |
| `effect_clause:create-token` | 695 | 679 | 44 | 158 | missing_lowering | high |
| `activated_effect:destroy-target` | 151 | 150 | 42 | 60 | missing_lowering | high |
| `mechanic_dependency:cr-508-declare-attackers-step` | 135 | 135 | 39 | 99 | partial | high |
| `effect_clause:draw` | 551 | 543 | 38 | 103 | missing_lowering | high |
| `effect_clause:unparsed-until-end-of` | 68 | 68 | 36 | 48 | missing_lowering | high |
| `keyword_dependency:morph` | 141 | 141 | 32 | 141 | missing_contract | medium |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-611-continuous-effects` | 4,091 | 10,377 | 10,377 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-509-declare-blockers-step` | 4,077 | 10,230 | 10,230 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-509-declare-blockers-step` | 4,072 | 10,423 | 10,423 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-111-tokens` | 4,030 | 10,369 | 10,369 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 4,030 | 10,176 | 10,176 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, mechanic_dependency:cr-111-tokens` | 4,009 | 10,222 | 10,222 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,988 | 9,961 | 9,961 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:typed-spell-additional-cost-clause` | 3,987 | 10,154 | 10,154 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:deal-damage` | 3,977 | 10,083 | 10,083 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:deal-damage` | 3,976 | 10,276 | 10,276 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:exile` | 3,970 | 10,461 | 10,461 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 3,970 | 10,268 | 10,268 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:typed-spell-additional-cost-clause` | 3,969 | 10,007 | 10,007 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,963 | 10,087 | 10,087 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:destroy-target` | 3,962 | 10,280 | 10,280 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:return` | 3,961 | 10,054 | 10,054 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:return` | 3,960 | 10,247 | 10,247 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, activated_effect:tap-state` | 3,960 | 10,195 | 10,233 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,960 | 10,002 | 10,040 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-regenerate-this-creature` | 3,959 | 9,967 | 9,983 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
