---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "15aacfa0d5343b94c613c50c7a013efc7060a75e67ce752fb98717c18038244f"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":2371,"partial":13271,"unresolved":15981}`
- CardProgram states: `{"residual":29252,"trusted":2371}`
- Hard construction failures: 0
- Frontier fingerprint: `15aacfa0d5343b94c613c50c7a013efc7060a75e67ce752fb98717c18038244f`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 9,561 | 7,706 | 3,366 | 9,561 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 567 | 520 | 189 | 346 | partial | high |
| `mechanic_dependency:cr-614-replacement-effects` | 539 | 539 | 167 | 539 | partial | high |
| `mechanic_dependency:cr-509-declare-blockers-step` | 428 | 423 | 146 | 392 | partial | high |
| `effect_clause:deal-damage` | 1,007 | 976 | 115 | 253 | missing_lowering | high |
| `mechanic_dependency:cr-111-tokens` | 338 | 333 | 112 | 338 | partial | high |
| `effect_clause:return` | 740 | 713 | 111 | 250 | missing_lowering | high |
| `effect_clause:destroy-target` | 588 | 555 | 96 | 253 | missing_lowering | high |
| `effect_clause:exile` | 1,038 | 989 | 91 | 451 | missing_lowering | high |
| `mechanic_dependency:cr-115-targets` | 298 | 282 | 86 | 163 | missing_contract | high |
| `activated_effect:return` | 450 | 449 | 83 | 169 | missing_lowering | high |
| `activated_effect:deal-damage` | 479 | 460 | 83 | 139 | missing_lowering | high |
| `activated_effect:tap-state` | 322 | 311 | 75 | 164 | missing_lowering | high |
| `activated_effect:unparsed-regenerate-this-creature` | 149 | 148 | 72 | 129 | missing_lowering | high |
| `effect_clause:tap-state` | 387 | 378 | 69 | 144 | missing_lowering | high |
| `effect_clause:unparsed-target-creature-gets` | 216 | 213 | 67 | 140 | missing_lowering | high |
| `activated_effect:unparsed-this-creature-gets` | 131 | 126 | 64 | 86 | missing_lowering | high |
| `effect_clause:look-reveal` | 574 | 569 | 60 | 113 | missing_lowering | high |
| `activated_effect:create-token` | 475 | 464 | 54 | 194 | missing_lowering | high |
| `activated_effect:unparsed-target-creature-gains` | 98 | 94 | 51 | 81 | missing_lowering | high |
| `effect_clause:create-token` | 723 | 706 | 43 | 158 | missing_lowering | high |
| `effect_clause:draw` | 599 | 591 | 43 | 128 | missing_lowering | high |
| `activated_effect:put-counter` | 356 | 344 | 42 | 117 | missing_lowering | high |
| `effect_clause:sacrifice` | 387 | 383 | 41 | 131 | missing_lowering | high |
| `activated_effect:destroy-target` | 151 | 150 | 41 | 60 | missing_lowering | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-509-declare-blockers-step` | 3,789 | 10,299 | 10,299 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-614-replacement-effects` | 3,776 | 10,446 | 10,446 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-509-declare-blockers-step` | 3,755 | 10,492 | 10,492 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-111-tokens` | 3,740 | 10,245 | 10,245 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-115-targets` | 3,723 | 10,157 | 10,157 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, mechanic_dependency:cr-111-tokens` | 3,717 | 10,291 | 10,291 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, mechanic_dependency:cr-111-tokens` | 3,711 | 10,438 | 10,438 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:deal-damage` | 3,701 | 10,160 | 10,160 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:return` | 3,698 | 10,157 | 10,157 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:destroy-target` | 3,682 | 10,160 | 10,160 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:return` | 3,681 | 10,076 | 10,116 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:deal-damage` | 3,680 | 10,206 | 10,206 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:tap-state` | 3,679 | 10,071 | 10,109 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 3,678 | 10,358 | 10,358 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-regenerate-this-creature` | 3,678 | 10,036 | 10,052 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, effect_clause:return` | 3,677 | 10,203 | 10,203 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:deal-damage` | 3,671 | 10,353 | 10,353 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:deal-damage` | 3,671 | 10,046 | 10,090 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-614-replacement-effects, effect_clause:return` | 3,669 | 10,350 | 10,350 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-509-declare-blockers-step, activated_effect:return` | 3,662 | 10,122 | 10,162 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
