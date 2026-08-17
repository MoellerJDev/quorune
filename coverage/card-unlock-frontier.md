---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "c0d13b08b807d8754496cfe2656d90ed1d062d73e1fd1c8e640cc0fd2a6e9a5c"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":5306,"partial":11972,"unresolved":14345}`
- CardProgram states: `{"residual":26317,"trusted":5306}`
- Hard construction failures: 0
- Frontier fingerprint: `c0d13b08b807d8754496cfe2656d90ed1d062d73e1fd1c8e640cc0fd2a6e9a5c`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 8,884 | 7,169 | 3,790 | 8,884 | missing_lowering | very_high |
| `replacement:damage-prevention` | 168 | 165 | 21 | 40 | missing_lowering | very_high |
| `effect_clause:draw` | 492 | 485 | 17 | 62 | missing_lowering | high |
| `keyword_dependency:changeling` | 62 | 62 | 17 | 62 | missing_contract | medium |
| `keyword_dependency:bestow` | 42 | 42 | 17 | 42 | missing_contract | medium |
| `activated_effect:create-token` | 329 | 322 | 16 | 66 | missing_lowering | high |
| `effect_clause:life-change` | 557 | 554 | 16 | 44 | missing_lowering | high |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `effect_clause:return` | 637 | 612 | 16 | 28 | missing_lowering | high |
| `mechanic_dependency:cr-400-general` | 26 | 26 | 16 | 26 | partial | high |
| `activated_effect:unparsed-this-creature-can` | 39 | 39 | 16 | 23 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 106 | 106 | 16 | 16 | missing_lowering | high |
| `effect_clause:exile` | 628 | 608 | 15 | 96 | missing_lowering | high |
| `activated_effect:exile` | 376 | 349 | 14 | 41 | missing_lowering | high |
| `activated_effect:put-onto-battlefield` | 288 | 286 | 14 | 32 | missing_lowering | high |
| `keyword_dependency:storm` | 33 | 33 | 13 | 33 | missing_contract | medium |
| `effect_clause:sacrifice` | 114 | 114 | 12 | 37 | missing_lowering | high |
| `keyword_dependency:improvise` | 23 | 23 | 12 | 23 | missing_contract | medium |
| `activated_effect:unparsed-investigate` | 13 | 13 | 12 | 13 | missing_lowering | high |
| `keyword_dependency:evoke` | 30 | 30 | 11 | 30 | missing_contract | medium |
| `effect_clause:unparsed-splice-onto-arcane` | 22 | 22 | 11 | 22 | missing_lowering | high |
| `effect_clause:create-token` | 581 | 565 | 10 | 88 | missing_lowering | high |
| `effect_clause:unparsed-target-player-discards` | 41 | 41 | 10 | 29 | missing_lowering | high |
| `keyword_dependency:delve` | 28 | 28 | 10 | 28 | missing_contract | medium |
| `effect_clause:unparsed-buyback-3` | 17 | 17 | 10 | 17 | missing_lowering | high |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:create-token` | 3,848 | 8,992 | 9,006 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:changeling, keyword_dependency:bestow` | 3,845 | 8,988 | 8,988 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:start-your-engines` | 3,843 | 8,966 | 8,966 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, keyword_dependency:bestow` | 3,843 | 8,966 | 8,972 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:changeling, activated_effect:create-token` | 3,841 | 9,012 | 9,026 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:exile` | 3,840 | 8,967 | 8,976 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:start-your-engines` | 3,839 | 8,990 | 9,004 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, activated_effect:create-token` | 3,839 | 8,990 | 9,010 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:equip` | 3,839 | 8,951 | 8,951 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:unparsed-this-creature-can` | 3,839 | 8,949 | 8,958 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:draw, keyword_dependency:bestow` | 3,838 | 8,988 | 8,988 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, mechanic_dependency:affinity-unsupported-wording` | 3,838 | 8,962 | 8,962 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:life-change` | 3,837 | 8,970 | 8,970 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:storm` | 3,837 | 8,959 | 8,959 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:put-onto-battlefield` | 3,837 | 8,958 | 8,959 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:return` | 3,837 | 8,954 | 8,954 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, mechanic_dependency:cr-400-general` | 3,837 | 8,952 | 8,952 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:typed-spell-additional-cost-clause` | 3,837 | 8,942 | 9,032 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:exile` | 3,836 | 9,022 | 9,022 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:exile` | 3,836 | 8,991 | 9,014 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
