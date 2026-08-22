---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "1b9d8fe5e2e5b8afaa328e755950609398c99f493fff6371bde5fb00c4f725c1"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":5616,"partial":11984,"unresolved":14023}`
- CardProgram states: `{"residual":26007,"trusted":5616}`
- Hard construction failures: 0
- Frontier fingerprint: `1b9d8fe5e2e5b8afaa328e755950609398c99f493fff6371bde5fb00c4f725c1`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 8,807 | 7,097 | 3,832 | 8,807 | missing_lowering | very_high |
| `activated_effect:create-token` | 327 | 320 | 22 | 66 | missing_lowering | high |
| `replacement:damage-prevention` | 168 | 165 | 21 | 40 | missing_lowering | very_high |
| `effect_clause:create-token` | 577 | 561 | 17 | 87 | missing_lowering | high |
| `effect_clause:life-change` | 554 | 551 | 16 | 44 | missing_lowering | high |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `mechanic_dependency:cr-400-general` | 26 | 26 | 16 | 26 | partial | high |
| `activated_effect:unparsed-this-creature-can` | 39 | 39 | 16 | 23 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 106 | 106 | 16 | 16 | missing_lowering | high |
| `activated_effect:put-onto-battlefield` | 288 | 286 | 14 | 32 | missing_lowering | high |
| `keyword_dependency:evoke` | 30 | 30 | 13 | 30 | missing_contract | medium |
| `keyword_dependency:delve` | 28 | 28 | 12 | 28 | missing_contract | medium |
| `keyword_dependency:improvise` | 23 | 23 | 12 | 23 | missing_contract | medium |
| `activated_effect:unparsed-investigate` | 13 | 13 | 12 | 13 | missing_lowering | high |
| `effect_clause:exile` | 604 | 584 | 11 | 84 | missing_lowering | high |
| `effect_clause:sacrifice` | 110 | 110 | 11 | 34 | missing_lowering | high |
| `effect_clause:return` | 626 | 601 | 11 | 23 | missing_lowering | high |
| `effect_clause:unparsed-splice-onto-arcane` | 22 | 22 | 11 | 22 | missing_lowering | high |
| `effect_clause:unparsed-buyback-3` | 17 | 17 | 10 | 17 | missing_lowering | high |
| `effect_clause:unparsed-target-creature-can` | 17 | 17 | 10 | 13 | missing_lowering | high |
| `keyword_dependency:banding` | 13 | 13 | 10 | 13 | missing_contract | medium |
| `mechanic_dependency:cr-725-the-monarch` | 38 | 38 | 9 | 38 | partial | high |
| `keyword_dependency:rebound` | 34 | 34 | 9 | 34 | missing_contract | medium |
| `keyword_dependency:start-your-engines` | 40 | 40 | 8 | 40 | missing_contract | medium |
| `keyword_dependency:living-weapon` | 19 | 19 | 8 | 19 | missing_contract | medium |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:start-your-engines` | 3,884 | 8,913 | 8,927 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, replacement:damage-prevention` | 3,883 | 8,913 | 8,933 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:create-token` | 3,879 | 8,960 | 8,974 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:equip` | 3,879 | 8,898 | 8,912 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:unparsed-this-creature-can` | 3,879 | 8,896 | 8,919 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, mechanic_dependency:affinity-unsupported-wording` | 3,878 | 8,909 | 8,923 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:life-change` | 3,877 | 8,917 | 8,931 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:put-onto-battlefield` | 3,877 | 8,905 | 8,920 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, mechanic_dependency:cr-400-general` | 3,877 | 8,899 | 8,913 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:typed-spell-additional-cost-clause` | 3,877 | 8,889 | 8,993 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, keyword_dependency:start-your-engines` | 3,877 | 8,887 | 8,893 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:delve` | 3,875 | 8,901 | 8,915 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:improvise` | 3,875 | 8,896 | 8,910 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:living-weapon` | 3,875 | 8,892 | 8,906 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:evoke` | 3,874 | 8,903 | 8,917 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:myriad` | 3,874 | 8,896 | 8,910 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:umbra-armor` | 3,874 | 8,888 | 8,902 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:create-token, keyword_dependency:start-your-engines` | 3,873 | 8,934 | 8,934 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, mechanic_dependency:cr-725-the-monarch` | 3,873 | 8,911 | 8,925 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:unparsed-investigate` | 3,873 | 8,886 | 8,900 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
