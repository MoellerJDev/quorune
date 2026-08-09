---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "66375acc429cbfce6bfe55d27e7c35fffaf6430dd68953221bf3d929c24e1997"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":2637,"partial":13136,"unresolved":15850}`
- CardProgram states: `{"residual":28986,"trusted":2637}`
- Hard construction failures: 0
- Frontier fingerprint: `66375acc429cbfce6bfe55d27e7c35fffaf6430dd68953221bf3d929c24e1997`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,561 | 7,706 | 3,540 | 9,561 | missing_lowering | very_high |
| `effect_clause:typed-spell-additional-cost-clause` | 237 | 237 | 235 | 237 | missing_lowering | high |
| `mechanic_dependency:cr-611-continuous-effects` | 480 | 440 | 192 | 346 | partial | high |
| `mechanic_dependency:cr-614-replacement-effects` | 539 | 539 | 171 | 539 | partial | high |
| `mechanic_dependency:cr-509-declare-blockers-step` | 428 | 423 | 147 | 392 | partial | high |
| `mechanic_dependency:cr-111-tokens` | 337 | 332 | 112 | 337 | partial | high |
| `effect_clause:return` | 721 | 694 | 111 | 248 | missing_lowering | high |
| `effect_clause:deal-damage` | 956 | 925 | 110 | 245 | missing_lowering | high |
| `effect_clause:exile` | 991 | 945 | 98 | 431 | missing_lowering | high |
| `effect_clause:destroy-target` | 572 | 540 | 97 | 249 | missing_lowering | high |
| `activated_effect:return` | 450 | 449 | 83 | 169 | missing_lowering | high |
| `activated_effect:deal-damage` | 479 | 460 | 83 | 139 | missing_lowering | high |
| `activated_effect:tap-state` | 322 | 311 | 75 | 164 | missing_lowering | high |
| `activated_effect:unparsed-regenerate-this-creature` | 149 | 148 | 72 | 129 | missing_lowering | high |
| `effect_clause:tap-state` | 373 | 364 | 67 | 136 | missing_lowering | high |
| `activated_effect:unparsed-this-creature-gets` | 131 | 126 | 64 | 86 | missing_lowering | high |
| `effect_clause:look-reveal` | 552 | 548 | 60 | 94 | missing_lowering | high |
| `activated_effect:create-token` | 475 | 464 | 54 | 194 | missing_lowering | high |
| `effect_clause:draw` | 577 | 569 | 46 | 125 | missing_lowering | high |
| `effect_clause:create-token` | 707 | 690 | 43 | 158 | missing_lowering | high |
| `activated_effect:destroy-target` | 151 | 150 | 42 | 60 | missing_lowering | high |
| `mechanic_dependency:scry` | 107 | 107 | 40 | 107 | missing_contract | high |
| `mechanic_dependency:cr-508-declare-attackers-step` | 135 | 135 | 39 | 99 | partial | high |
| `activated_effect:put-counter` | 347 | 335 | 36 | 108 | missing_lowering | high |
| `effect_clause:unparsed-until-end-of` | 68 | 68 | 36 | 48 | missing_lowering | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, mechanic_dependency:cr-611-continuous-effects` | 3,999 | 10,144 | 10,144 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, mechanic_dependency:cr-509-declare-blockers-step` | 3,976 | 10,190 | 10,190 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, mechanic_dependency:cr-614-replacement-effects` | 3,971 | 10,337 | 10,337 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-509-declare-blockers-step` | 3,967 | 10,299 | 10,299 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-614-replacement-effects` | 3,957 | 10,446 | 10,446 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-509-declare-blockers-step` | 3,934 | 10,492 | 10,492 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, mechanic_dependency:cr-111-tokens` | 3,928 | 10,135 | 10,135 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 3,917 | 10,244 | 10,244 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, mechanic_dependency:cr-111-tokens` | 3,892 | 10,290 | 10,290 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-111-tokens` | 3,889 | 10,437 | 10,437 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, effect_clause:return` | 3,888 | 10,046 | 10,046 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, effect_clause:deal-damage` | 3,886 | 10,043 | 10,043 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, effect_clause:exile` | 3,875 | 10,229 | 10,229 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:return` | 3,875 | 10,155 | 10,155 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:deal-damage` | 3,873 | 10,152 | 10,152 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, effect_clause:destroy-target` | 3,873 | 10,047 | 10,047 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, activated_effect:return` | 3,871 | 9,967 | 10,007 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, activated_effect:tap-state` | 3,869 | 9,962 | 10,000 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:typed-spell-additional-cost-clause, activated_effect:unparsed-regenerate-this-creature` | 3,865 | 9,927 | 9,943 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 3,862 | 10,338 | 10,338 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
