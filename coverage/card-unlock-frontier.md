---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "b950189558872277b8548334166529b10b1e13d84b608c9f3a96a74f9606b269"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":5244,"partial":11996,"unresolved":14383}`
- CardProgram states: `{"residual":26379,"trusted":5244}`
- Hard construction failures: 0
- Frontier fingerprint: `b950189558872277b8548334166529b10b1e13d84b608c9f3a96a74f9606b269`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 8,884 | 7,169 | 3,785 | 8,884 | missing_lowering | very_high |
| `replacement:damage-prevention` | 168 | 165 | 21 | 40 | missing_lowering | very_high |
| `effect_clause:draw` | 492 | 485 | 17 | 62 | missing_lowering | high |
| `keyword_dependency:changeling` | 62 | 62 | 17 | 62 | missing_contract | medium |
| `keyword_dependency:bestow` | 42 | 42 | 17 | 42 | missing_contract | medium |
| `activated_effect:create-token` | 329 | 322 | 16 | 66 | missing_lowering | high |
| `effect_clause:life-change` | 557 | 554 | 16 | 44 | missing_lowering | high |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `effect_clause:return` | 640 | 615 | 16 | 28 | missing_lowering | high |
| `mechanic_dependency:cr-400-general` | 26 | 26 | 16 | 26 | partial | high |
| `activated_effect:unparsed-this-creature-can` | 39 | 39 | 16 | 23 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 106 | 106 | 16 | 16 | missing_lowering | high |
| `effect_clause:exile` | 629 | 609 | 15 | 96 | missing_lowering | high |
| `activated_effect:unparsed-surveil-1` | 25 | 25 | 15 | 21 | missing_lowering | high |
| `activated_effect:exile` | 376 | 349 | 14 | 41 | missing_lowering | high |
| `activated_effect:put-onto-battlefield` | 288 | 286 | 14 | 32 | missing_lowering | high |
| `keyword_dependency:storm` | 33 | 33 | 13 | 33 | missing_contract | medium |
| `effect_clause:sacrifice` | 114 | 114 | 12 | 37 | missing_lowering | high |
| `keyword_dependency:improvise` | 23 | 23 | 12 | 23 | missing_contract | medium |
| `activated_effect:unparsed-investigate` | 13 | 13 | 12 | 13 | missing_lowering | high |
| `keyword_dependency:evoke` | 30 | 30 | 11 | 30 | missing_contract | medium |
| `effect_clause:unparsed-splice-onto-arcane` | 22 | 22 | 11 | 22 | missing_lowering | high |
| `effect_clause:create-token` | 582 | 566 | 10 | 88 | missing_lowering | high |
| `effect_clause:unparsed-target-player-discards` | 41 | 41 | 10 | 29 | missing_lowering | high |
| `keyword_dependency:delve` | 28 | 28 | 10 | 28 | missing_contract | medium |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:create-token` | 3,843 | 8,992 | 9,006 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:changeling, keyword_dependency:bestow` | 3,840 | 8,988 | 8,988 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, keyword_dependency:bestow` | 3,838 | 8,966 | 8,972 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:start-your-engines` | 3,837 | 8,966 | 8,966 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:changeling, activated_effect:create-token` | 3,836 | 9,012 | 9,026 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:exile` | 3,835 | 8,967 | 8,976 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, activated_effect:create-token` | 3,834 | 8,990 | 9,010 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:equip` | 3,834 | 8,951 | 8,951 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:unparsed-this-creature-can` | 3,834 | 8,949 | 8,958 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:start-your-engines` | 3,833 | 8,990 | 9,004 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:draw, keyword_dependency:bestow` | 3,833 | 8,988 | 8,988 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, mechanic_dependency:affinity-unsupported-wording` | 3,833 | 8,962 | 8,962 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:life-change` | 3,832 | 8,970 | 8,970 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:storm` | 3,832 | 8,959 | 8,959 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:return` | 3,832 | 8,954 | 8,954 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, mechanic_dependency:cr-400-general` | 3,832 | 8,952 | 8,952 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:unparsed-surveil-1` | 3,832 | 8,947 | 8,951 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:typed-spell-additional-cost-clause` | 3,832 | 8,942 | 9,032 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:exile` | 3,831 | 9,022 | 9,022 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:exile` | 3,831 | 8,991 | 9,014 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
