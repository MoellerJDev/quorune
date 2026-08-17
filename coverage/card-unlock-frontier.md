---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "f28ef15197518f96bac2aef9525bbce8b3df99bcf229f00d1fae5248a550b64a"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":4849,"partial":12328,"unresolved":14446}`
- CardProgram states: `{"residual":26774,"trusted":4849}`
- Hard construction failures: 0
- Frontier fingerprint: `f28ef15197518f96bac2aef9525bbce8b3df99bcf229f00d1fae5248a550b64a`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 8,884 | 7,169 | 3,728 | 8,884 | missing_lowering | very_high |
| `mechanic_dependency:cr-611-continuous-effects` | 515 | 473 | 244 | 381 | partial | high |
| `replacement:damage-prevention` | 168 | 165 | 21 | 40 | missing_lowering | very_high |
| `keyword_dependency:cascade` | 37 | 37 | 19 | 37 | missing_contract | medium |
| `keyword_dependency:bestow` | 42 | 42 | 17 | 42 | missing_contract | medium |
| `activated_effect:create-token` | 330 | 323 | 16 | 66 | missing_lowering | high |
| `effect_clause:draw` | 495 | 488 | 16 | 62 | missing_lowering | high |
| `effect_clause:life-change` | 557 | 554 | 16 | 44 | missing_lowering | high |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `effect_clause:return` | 640 | 615 | 16 | 28 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 106 | 106 | 16 | 16 | missing_lowering | high |
| `activated_effect:unparsed-surveil-1` | 25 | 25 | 15 | 21 | missing_lowering | high |
| `effect_clause:exile` | 629 | 609 | 14 | 96 | missing_lowering | high |
| `activated_effect:exile` | 376 | 349 | 14 | 41 | missing_lowering | high |
| `activated_effect:put-onto-battlefield` | 288 | 286 | 14 | 32 | missing_lowering | high |
| `mechanic_dependency:cr-400-general` | 26 | 26 | 14 | 26 | partial | high |
| `activated_effect:unparsed-this-creature-can` | 39 | 39 | 14 | 23 | missing_lowering | high |
| `keyword_dependency:changeling` | 62 | 62 | 13 | 62 | missing_contract | medium |
| `effect_clause:sacrifice` | 114 | 114 | 12 | 37 | missing_lowering | high |
| `keyword_dependency:storm` | 33 | 33 | 12 | 33 | missing_contract | medium |
| `activated_effect:unparsed-target-player-mills` | 41 | 40 | 12 | 20 | missing_lowering | high |
| `activated_effect:unparsed-investigate` | 13 | 13 | 12 | 13 | missing_lowering | high |
| `keyword_dependency:evoke` | 30 | 30 | 11 | 30 | missing_contract | medium |
| `keyword_dependency:improvise` | 23 | 23 | 11 | 23 | missing_contract | medium |
| `effect_clause:create-token` | 582 | 566 | 10 | 88 | missing_lowering | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:bestow` | 4,032 | 9,307 | 9,307 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:create-token` | 4,028 | 9,331 | 9,345 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:cascade` | 4,026 | 9,302 | 9,302 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:changeling` | 4,023 | 9,327 | 9,327 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, replacement:damage-prevention` | 4,023 | 9,305 | 9,311 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:start-your-engines` | 4,022 | 9,305 | 9,305 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:exile` | 4,020 | 9,306 | 9,315 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:equip` | 4,019 | 9,290 | 9,290 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:affinity-unsupported-wording` | 4,018 | 9,301 | 9,301 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-this-creature-can` | 4,018 | 9,288 | 9,297 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:draw` | 4,017 | 9,327 | 9,327 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:life-change` | 4,017 | 9,309 | 9,309 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:return` | 4,017 | 9,293 | 9,293 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:unparsed-surveil-1` | 4,017 | 9,286 | 9,290 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:typed-spell-additional-cost-clause` | 4,017 | 9,281 | 9,371 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:storm` | 4,016 | 9,298 | 9,298 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, activated_effect:put-onto-battlefield` | 4,016 | 9,297 | 9,298 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, effect_clause:exile` | 4,015 | 9,361 | 9,361 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, mechanic_dependency:cr-400-general` | 4,015 | 9,291 | 9,291 |
| `continuous_layer:continuous-effect-layers-and-dependencies, mechanic_dependency:cr-611-continuous-effects, keyword_dependency:improvise` | 4,015 | 9,288 | 9,288 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
