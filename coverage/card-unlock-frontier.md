---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "608434a8b87579ebe7af4d90585c09611a969702e08ba96f317cdf4f4baebfa7"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":2750,"partial":13088,"unresolved":15785}`
- CardProgram states: `{"residual":28873,"trusted":2750}`
- Hard construction failures: 0
- Frontier fingerprint: `608434a8b87579ebe7af4d90585c09611a969702e08ba96f317cdf4f4baebfa7`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,561 | 7,706 | 3,556 | 9,561 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 480 | 440 | 193 | 346 | partial | high |
| `mechanic_dependency:cr-614-replacement-effects` | 539 | 539 | 183 | 539 | partial | high |
| `effect_clause:typed-spell-additional-cost-clause` | 155 | 155 | 154 | 155 | missing_lowering | high |
| `mechanic_dependency:cr-509-declare-blockers-step` | 428 | 423 | 148 | 392 | partial | high |
| `mechanic_dependency:cr-111-tokens` | 338 | 333 | 113 | 338 | partial | high |
| `effect_clause:return` | 721 | 694 | 111 | 248 | missing_lowering | high |
| `effect_clause:deal-damage` | 956 | 925 | 110 | 245 | missing_lowering | high |
| `effect_clause:exile` | 991 | 945 | 99 | 431 | missing_lowering | high |
| `effect_clause:destroy-target` | 572 | 540 | 97 | 249 | missing_lowering | high |
| `activated_effect:deal-damage` | 479 | 460 | 85 | 139 | missing_lowering | high |
| `activated_effect:return` | 450 | 449 | 83 | 169 | missing_lowering | high |
| `activated_effect:tap-state` | 322 | 311 | 75 | 164 | missing_lowering | high |
| `activated_effect:unparsed-regenerate-this-creature` | 149 | 148 | 72 | 129 | missing_lowering | high |
| `effect_clause:tap-state` | 373 | 364 | 67 | 136 | missing_lowering | high |
| `activated_effect:unparsed-this-creature-gets` | 131 | 126 | 64 | 86 | missing_lowering | high |
| `effect_clause:look-reveal` | 552 | 548 | 60 | 94 | missing_lowering | high |
| `activated_effect:create-token` | 475 | 464 | 54 | 194 | missing_lowering | high |
| `effect_clause:typed-spell-result-clause` | 52 | 52 | 51 | 52 | missing_lowering | high |
| `effect_clause:draw` | 577 | 569 | 47 | 125 | missing_lowering | high |
| `effect_clause:create-token` | 707 | 690 | 43 | 158 | missing_lowering | high |
| `activated_effect:destroy-target` | 151 | 150 | 42 | 60 | missing_lowering | high |
| `mechanic_dependency:cr-508-declare-attackers-step` | 135 | 135 | 39 | 99 | partial | high |
| `keyword_dependency:hexproof` | 89 | 88 | 36 | 85 | missing_contract | medium |
| `effect_clause:unparsed-until-end-of` | 68 | 68 | 36 | 48 | missing_lowering | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-614-replacement-effects` | 3,986 | 10,446 | 10,446 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-509-declare-blockers-step` | 3,985 | 10,299 | 10,299 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-509-declare-blockers-step` | 3,963 | 10,492 | 10,492 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 3,935 | 10,245 | 10,245 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 3,935 | 10,062 | 10,062 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-111-tokens` | 3,918 | 10,438 | 10,438 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:typed-spell-additional-cost-clause` | 3,917 | 10,255 | 10,255 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, mechanic_dependency:cr-509-declare-blockers-step` | 3,912 | 10,108 | 10,108 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, mechanic_dependency:cr-111-tokens` | 3,910 | 10,291 | 10,291 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:return` | 3,892 | 10,155 | 10,155 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:deal-damage` | 3,890 | 10,152 | 10,152 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 3,880 | 10,338 | 10,338 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,877 | 10,156 | 10,156 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:return` | 3,875 | 10,348 | 10,348 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:return` | 3,875 | 10,076 | 10,116 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,873 | 10,071 | 10,109 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:deal-damage` | 3,872 | 10,345 | 10,345 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-regenerate-this-creature` | 3,872 | 10,036 | 10,052 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:return` | 3,869 | 10,201 | 10,201 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:deal-damage` | 3,867 | 10,198 | 10,198 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
