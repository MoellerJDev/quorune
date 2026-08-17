---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "4b332ad03c72dd600553ee47c948cb6bcf493843b12ee9bb3b46ebb02a4ea731"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":5200,"partial":11977,"unresolved":14446}`
- CardProgram states: `{"residual":26423,"trusted":5200}`
- Hard construction failures: 0
- Frontier fingerprint: `4b332ad03c72dd600553ee47c948cb6bcf493843b12ee9bb3b46ebb02a4ea731`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 8,884 | 7,169 | 3,774 | 8,884 | missing_lowering | very_high |
| `replacement:damage-prevention` | 168 | 165 | 21 | 40 | missing_lowering | very_high |
| `keyword_dependency:changeling` | 62 | 62 | 17 | 62 | missing_contract | medium |
| `keyword_dependency:bestow` | 42 | 42 | 17 | 42 | missing_contract | medium |
| `activated_effect:create-token` | 330 | 323 | 16 | 66 | missing_lowering | high |
| `effect_clause:draw` | 495 | 488 | 16 | 62 | missing_lowering | high |
| `effect_clause:life-change` | 557 | 554 | 16 | 44 | missing_lowering | high |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `effect_clause:return` | 640 | 615 | 16 | 28 | missing_lowering | high |
| `mechanic_dependency:cr-400-general` | 26 | 26 | 16 | 26 | partial | high |
| `effect_clause:typed-spell-additional-cost-clause` | 106 | 106 | 16 | 16 | missing_lowering | high |
| `activated_effect:unparsed-this-creature-can` | 39 | 39 | 15 | 23 | missing_lowering | high |
| `activated_effect:unparsed-surveil-1` | 25 | 25 | 15 | 21 | missing_lowering | high |
| `effect_clause:exile` | 629 | 609 | 14 | 96 | missing_lowering | high |
| `activated_effect:exile` | 376 | 349 | 14 | 41 | missing_lowering | high |
| `activated_effect:put-onto-battlefield` | 288 | 286 | 14 | 32 | missing_lowering | high |
| `effect_clause:sacrifice` | 114 | 114 | 12 | 37 | missing_lowering | high |
| `keyword_dependency:storm` | 33 | 33 | 12 | 33 | missing_contract | medium |
| `keyword_dependency:improvise` | 23 | 23 | 12 | 23 | missing_contract | medium |
| `activated_effect:unparsed-target-player-mills` | 41 | 40 | 12 | 20 | missing_lowering | high |
| `activated_effect:unparsed-investigate` | 13 | 13 | 12 | 13 | missing_lowering | high |
| `keyword_dependency:evoke` | 30 | 30 | 11 | 30 | missing_contract | medium |
| `effect_clause:create-token` | 582 | 566 | 10 | 88 | missing_lowering | high |
| `effect_clause:unparsed-target-player-discards` | 41 | 41 | 10 | 29 | missing_lowering | high |
| `keyword_dependency:delve` | 28 | 28 | 10 | 28 | missing_contract | medium |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:create-token` | 3,832 | 8,992 | 9,006 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:changeling, keyword_dependency:bestow` | 3,829 | 8,988 | 8,988 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, keyword_dependency:bestow` | 3,827 | 8,966 | 8,972 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:start-your-engines` | 3,826 | 8,966 | 8,966 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:changeling, activated_effect:create-token` | 3,825 | 9,012 | 9,026 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:exile` | 3,824 | 8,967 | 8,976 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, activated_effect:create-token` | 3,823 | 8,990 | 9,010 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:equip` | 3,823 | 8,951 | 8,951 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:start-your-engines` | 3,822 | 8,990 | 9,004 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, mechanic_dependency:affinity-unsupported-wording` | 3,822 | 8,962 | 8,962 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:unparsed-this-creature-can` | 3,822 | 8,949 | 8,958 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:draw` | 3,821 | 8,988 | 8,988 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:life-change` | 3,821 | 8,970 | 8,970 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:return` | 3,821 | 8,954 | 8,954 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, mechanic_dependency:cr-400-general` | 3,821 | 8,952 | 8,952 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:unparsed-surveil-1` | 3,821 | 8,947 | 8,951 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:typed-spell-additional-cost-clause` | 3,821 | 8,942 | 9,032 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:exile` | 3,820 | 8,991 | 9,014 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, keyword_dependency:changeling` | 3,820 | 8,986 | 8,992 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:storm` | 3,820 | 8,959 | 8,959 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
