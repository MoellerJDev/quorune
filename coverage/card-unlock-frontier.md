---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "419576e3d0c33b0be8176e004e93c7bbb887de6d6babf52c6c5bd9bc0314b8d5"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":5411,"partial":11895,"unresolved":14317}`
- CardProgram states: `{"residual":26212,"trusted":5411}`
- Hard construction failures: 0
- Frontier fingerprint: `419576e3d0c33b0be8176e004e93c7bbb887de6d6babf52c6c5bd9bc0314b8d5`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 8,811 | 7,098 | 3,776 | 8,811 | missing_lowering | very_high |
| `activated_effect:create-token` | 329 | 322 | 22 | 66 | missing_lowering | high |
| `replacement:damage-prevention` | 168 | 165 | 21 | 40 | missing_lowering | very_high |
| `effect_clause:exile` | 628 | 608 | 16 | 96 | missing_lowering | high |
| `effect_clause:life-change` | 557 | 554 | 16 | 44 | missing_lowering | high |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `effect_clause:return` | 637 | 612 | 16 | 28 | missing_lowering | high |
| `mechanic_dependency:cr-400-general` | 26 | 26 | 16 | 26 | partial | high |
| `activated_effect:unparsed-this-creature-can` | 39 | 39 | 16 | 23 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 106 | 106 | 16 | 16 | missing_lowering | high |
| `activated_effect:exile` | 377 | 350 | 14 | 41 | missing_lowering | high |
| `activated_effect:put-onto-battlefield` | 288 | 286 | 14 | 32 | missing_lowering | high |
| `keyword_dependency:storm` | 33 | 33 | 13 | 33 | missing_contract | medium |
| `effect_clause:sacrifice` | 114 | 114 | 12 | 37 | missing_lowering | high |
| `keyword_dependency:improvise` | 23 | 23 | 12 | 23 | missing_contract | medium |
| `activated_effect:unparsed-investigate` | 13 | 13 | 12 | 13 | missing_lowering | high |
| `keyword_dependency:evoke` | 30 | 30 | 11 | 30 | missing_contract | medium |
| `effect_clause:unparsed-target-player-discards` | 41 | 41 | 11 | 29 | missing_lowering | high |
| `effect_clause:unparsed-splice-onto-arcane` | 22 | 22 | 11 | 22 | missing_lowering | high |
| `effect_clause:create-token` | 581 | 565 | 10 | 88 | missing_lowering | high |
| `keyword_dependency:delve` | 28 | 28 | 10 | 28 | missing_contract | medium |
| `effect_clause:unparsed-buyback-3` | 17 | 17 | 10 | 17 | missing_lowering | high |
| `keyword_dependency:banding` | 13 | 13 | 10 | 13 | missing_contract | medium |
| `mechanic_dependency:cr-725-the-monarch` | 38 | 38 | 9 | 38 | partial | high |
| `keyword_dependency:rebound` | 34 | 34 | 9 | 34 | missing_contract | medium |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:start-your-engines` | 3,827 | 8,917 | 8,931 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, replacement:damage-prevention` | 3,827 | 8,917 | 8,937 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:exile` | 3,824 | 8,918 | 8,941 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:equip` | 3,823 | 8,902 | 8,916 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:unparsed-this-creature-can` | 3,823 | 8,900 | 8,923 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, mechanic_dependency:affinity-unsupported-wording` | 3,822 | 8,913 | 8,927 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:exile` | 3,821 | 8,973 | 8,987 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:life-change` | 3,821 | 8,921 | 8,935 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:storm` | 3,821 | 8,910 | 8,924 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:put-onto-battlefield` | 3,821 | 8,909 | 8,924 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:return` | 3,821 | 8,905 | 8,919 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, mechanic_dependency:cr-400-general` | 3,821 | 8,903 | 8,917 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:typed-spell-additional-cost-clause` | 3,821 | 8,893 | 8,997 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, keyword_dependency:start-your-engines` | 3,820 | 8,891 | 8,897 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:improvise` | 3,819 | 8,900 | 8,914 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:living-weapon` | 3,819 | 8,896 | 8,910 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:myriad` | 3,818 | 8,900 | 8,914 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:umbra-armor` | 3,818 | 8,892 | 8,906 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, mechanic_dependency:cr-725-the-monarch` | 3,817 | 8,915 | 8,929 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:sacrifice` | 3,817 | 8,914 | 8,928 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
