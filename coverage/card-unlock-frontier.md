---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "b19ca1c353c949dfefe7f4bc4fbc5e048ea1bea23ba8636d37ceded8a0e05d82"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":3169,"partial":12874,"unresolved":15580}`
- CardProgram states: `{"residual":28454,"trusted":3169}`
- Hard construction failures: 0
- Frontier fingerprint: `b19ca1c353c949dfefe7f4bc4fbc5e048ea1bea23ba8636d37ceded8a0e05d82`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,396 | 7,561 | 3,631 | 9,396 | missing_lowering | very_high |
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
| `activated_effect:tap-state` | 322 | 311 | 82 | 164 | missing_lowering | high |
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
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-611-continuous-effects` | 4,084 | 10,281 | 10,281 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-509-declare-blockers-step` | 4,070 | 10,134 | 10,134 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-509-declare-blockers-step` | 4,065 | 10,327 | 10,327 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-111-tokens` | 4,023 | 10,273 | 10,273 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 4,023 | 10,080 | 10,080 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, mechanic_dependency:cr-111-tokens` | 4,002 | 10,126 | 10,126 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,981 | 9,865 | 9,865 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:typed-spell-additional-cost-clause` | 3,980 | 10,058 | 10,058 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:deal-damage` | 3,970 | 9,987 | 9,987 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:deal-damage` | 3,969 | 10,180 | 10,180 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:exile` | 3,963 | 10,365 | 10,365 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 3,963 | 10,172 | 10,172 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:typed-spell-additional-cost-clause` | 3,962 | 9,911 | 9,911 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,956 | 9,991 | 9,991 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:destroy-target` | 3,955 | 10,184 | 10,184 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:return` | 3,954 | 9,958 | 9,958 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:return` | 3,953 | 10,151 | 10,151 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, activated_effect:tap-state` | 3,953 | 10,099 | 10,137 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,953 | 9,906 | 9,944 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-regenerate-this-creature` | 3,952 | 9,871 | 9,887 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
