---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "096d6189628635f5a934374ddc834d0188c87c9f20d3b7c85b2e16390b5cf01e"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":5352,"partial":11928,"unresolved":14343}`
- CardProgram states: `{"residual":26271,"trusted":5352}`
- Hard construction failures: 0
- Frontier fingerprint: `096d6189628635f5a934374ddc834d0188c87c9f20d3b7c85b2e16390b5cf01e`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 8,811 | 7,098 | 3,744 | 8,811 | missing_lowering | very_high |
| `activated_effect:create-token` | 329 | 322 | 22 | 66 | missing_lowering | high |
| `replacement:damage-prevention` | 168 | 165 | 21 | 40 | missing_lowering | very_high |
| `effect_clause:draw` | 492 | 485 | 17 | 62 | missing_lowering | high |
| `keyword_dependency:changeling` | 62 | 62 | 17 | 62 | missing_contract | medium |
| `keyword_dependency:bestow` | 42 | 42 | 17 | 42 | missing_contract | medium |
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
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:bestow` | 3,802 | 8,919 | 8,933 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:changeling, keyword_dependency:bestow` | 3,799 | 8,915 | 8,915 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:start-your-engines` | 3,797 | 8,893 | 8,893 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, keyword_dependency:bestow` | 3,797 | 8,893 | 8,899 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:changeling` | 3,795 | 8,939 | 8,953 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:exile` | 3,794 | 8,894 | 8,903 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:start-your-engines` | 3,793 | 8,917 | 8,931 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, replacement:damage-prevention` | 3,793 | 8,917 | 8,937 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:equip` | 3,793 | 8,878 | 8,878 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:unparsed-this-creature-can` | 3,793 | 8,876 | 8,885 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:draw, keyword_dependency:bestow` | 3,792 | 8,915 | 8,915 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, mechanic_dependency:affinity-unsupported-wording` | 3,792 | 8,889 | 8,889 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:life-change` | 3,791 | 8,897 | 8,897 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, keyword_dependency:storm` | 3,791 | 8,886 | 8,886 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, activated_effect:put-onto-battlefield` | 3,791 | 8,885 | 8,886 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:return` | 3,791 | 8,881 | 8,881 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, mechanic_dependency:cr-400-general` | 3,791 | 8,879 | 8,879 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:typed-spell-additional-cost-clause` | 3,791 | 8,869 | 8,959 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:bestow, effect_clause:exile` | 3,790 | 8,949 | 8,949 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:exile` | 3,790 | 8,918 | 8,941 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
