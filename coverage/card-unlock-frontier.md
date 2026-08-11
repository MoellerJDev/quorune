---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "4981bee32dc915411286ab237a411ca652372caa2e9f52502d82dd8551768d97"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":3000,"partial":12953,"unresolved":15670}`
- CardProgram states: `{"residual":28623,"trusted":3000}`
- Hard construction failures: 0
- Frontier fingerprint: `4981bee32dc915411286ab237a411ca652372caa2e9f52502d82dd8551768d97`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,495 | 7,644 | 3,576 | 9,495 | missing_lowering | very_high |
| `mechanic_dependency:cr-614-replacement-effects` | 539 | 539 | 196 | 539 | partial | high |
| `mechanic_dependency:cr-611-continuous-effects` | 480 | 440 | 195 | 346 | partial | high |
| `mechanic_dependency:cr-509-declare-blockers-step` | 428 | 423 | 157 | 392 | partial | high |
| `effect_clause:typed-spell-additional-cost-clause` | 123 | 123 | 122 | 123 | missing_lowering | high |
| `mechanic_dependency:cr-111-tokens` | 338 | 333 | 117 | 338 | partial | high |
| `effect_clause:deal-damage` | 956 | 925 | 112 | 245 | missing_lowering | high |
| `effect_clause:exile` | 988 | 942 | 102 | 430 | missing_lowering | high |
| `effect_clause:destroy-target` | 572 | 540 | 98 | 249 | missing_lowering | high |
| `effect_clause:return` | 686 | 660 | 96 | 216 | missing_lowering | high |
| `activated_effect:deal-damage` | 479 | 460 | 85 | 139 | missing_lowering | high |
| `activated_effect:tap-state` | 322 | 311 | 75 | 164 | missing_lowering | high |
| `activated_effect:unparsed-regenerate-this-creature` | 149 | 148 | 74 | 129 | missing_lowering | high |
| `effect_clause:tap-state` | 373 | 364 | 68 | 136 | missing_lowering | high |
| `effect_clause:typed-spell-result-clause` | 66 | 66 | 65 | 66 | missing_lowering | high |
| `activated_effect:return` | 418 | 417 | 64 | 139 | missing_lowering | high |
| `activated_effect:unparsed-this-creature-gets` | 131 | 126 | 64 | 86 | missing_lowering | high |
| `effect_clause:look-reveal` | 552 | 548 | 60 | 94 | missing_lowering | high |
| `activated_effect:create-token` | 475 | 464 | 55 | 194 | missing_lowering | high |
| `effect_clause:draw` | 577 | 569 | 47 | 124 | missing_lowering | high |
| `effect_clause:create-token` | 707 | 690 | 44 | 158 | missing_lowering | high |
| `activated_effect:destroy-target` | 151 | 150 | 42 | 60 | missing_lowering | high |
| `mechanic_dependency:cr-508-declare-attackers-step` | 135 | 135 | 39 | 99 | partial | high |
| `effect_clause:unparsed-until-end-of` | 68 | 68 | 36 | 48 | missing_lowering | high |
| `keyword_dependency:morph` | 141 | 141 | 32 | 141 | missing_contract | medium |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-611-continuous-effects` | 4,020 | 10,380 | 10,380 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-509-declare-blockers-step` | 4,012 | 10,233 | 10,233 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-509-declare-blockers-step` | 4,002 | 10,426 | 10,426 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 3,962 | 10,179 | 10,179 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-111-tokens` | 3,957 | 10,372 | 10,372 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, mechanic_dependency:cr-111-tokens` | 3,942 | 10,225 | 10,225 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,924 | 9,964 | 9,964 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:typed-spell-additional-cost-clause` | 3,918 | 10,157 | 10,157 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:deal-damage` | 3,913 | 10,086 | 10,086 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:deal-damage` | 3,907 | 10,279 | 10,279 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:typed-spell-additional-cost-clause` | 3,906 | 10,010 | 10,010 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 3,904 | 10,271 | 10,271 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:exile` | 3,899 | 10,464 | 10,464 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,899 | 10,090 | 10,090 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:return` | 3,897 | 10,057 | 10,057 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:deal-damage` | 3,895 | 10,132 | 10,132 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,894 | 10,005 | 10,043 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-regenerate-this-creature` | 3,894 | 9,970 | 9,986 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:destroy-target` | 3,893 | 10,283 | 10,283 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:return` | 3,891 | 10,250 | 10,250 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
