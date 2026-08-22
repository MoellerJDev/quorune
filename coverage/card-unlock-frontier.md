---
title: "Commander card-unlock frontier"
status: "generated"
authoritative_source: "coverage/card-unlock-frontier.json.gz"
verified: "4115fe57c550ef4746036e143f0c1e0940f317653a1e4f820fdad90f78666cb4"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Commander card-unlock frontier

This generated report ranks minimum known compiler and rules blockers for the pinned Commander-legal card snapshot. It is not a claim of complete Comprehensive Rules coverage.

## Snapshot

- Cards considered: 31,623
- Oracle states: `{"exact":5792,"partial":12045,"unresolved":13786}`
- CardProgram states: `{"residual":25831,"trusted":5792}`
- Hard construction failures: 0
- Frontier fingerprint: `4115fe57c550ef4746036e143f0c1e0940f317653a1e4f820fdad90f78666cb4`

## Highest-leverage single families

| Family | Occurrences | Cards | Sole-blocker cards | Exact abilities | Readiness | Risk |
|---|---:|---:|---:|---:|---|---|
| `continuous_layer:continuous-effect-layers-and-dependencies` | 8,496 | 6,842 | 3,793 | 8,496 | missing_lowering | very_high |
| `activated_effect:create-token` | 327 | 320 | 22 | 66 | missing_lowering | high |
| `replacement:damage-prevention` | 168 | 165 | 21 | 40 | missing_lowering | very_high |
| `effect_clause:create-token` | 577 | 561 | 17 | 87 | missing_lowering | high |
| `effect_clause:typed-spell-additional-cost-clause` | 106 | 106 | 17 | 17 | missing_lowering | high |
| `effect_clause:life-change` | 553 | 550 | 16 | 44 | missing_lowering | high |
| `mechanic_dependency:affinity-unsupported-wording` | 36 | 36 | 16 | 36 | missing_contract | high |
| `activated_effect:unparsed-this-creature-can` | 39 | 39 | 16 | 23 | missing_lowering | high |
| `activated_effect:put-onto-battlefield` | 221 | 219 | 14 | 32 | missing_lowering | high |
| `keyword_dependency:evoke` | 30 | 30 | 13 | 30 | missing_contract | medium |
| `keyword_dependency:delve` | 28 | 28 | 12 | 28 | missing_contract | medium |
| `keyword_dependency:improvise` | 23 | 23 | 12 | 23 | missing_contract | medium |
| `activated_effect:unparsed-investigate` | 13 | 13 | 12 | 13 | missing_lowering | high |
| `effect_clause:exile` | 604 | 584 | 11 | 84 | missing_lowering | high |
| `effect_clause:sacrifice` | 110 | 110 | 11 | 34 | missing_lowering | high |
| `effect_clause:return` | 626 | 601 | 11 | 23 | missing_lowering | high |
| `effect_clause:unparsed-splice-onto-arcane` | 22 | 22 | 11 | 22 | missing_lowering | high |
| `keyword_dependency:rebound` | 34 | 34 | 10 | 34 | missing_contract | medium |
| `effect_clause:unparsed-buyback-3` | 17 | 17 | 10 | 17 | missing_lowering | high |
| `effect_clause:unparsed-target-creature-can` | 17 | 17 | 10 | 13 | missing_lowering | high |
| `keyword_dependency:banding` | 13 | 13 | 10 | 13 | missing_contract | medium |
| `keyword_dependency:start-your-engines` | 40 | 40 | 8 | 40 | missing_contract | medium |
| `keyword_dependency:living-weapon` | 19 | 19 | 8 | 19 | missing_contract | medium |
| `activated_effect:life-change` | 221 | 209 | 8 | 18 | missing_lowering | high |
| `keyword_dependency:retrace` | 17 | 17 | 8 | 17 | missing_contract | medium |

## Highest-leverage bounded bundles

| Families | Exact cards | Exact abilities | Residuals |
|---|---:|---:|---:|
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:start-your-engines` | 3,845 | 8,602 | 8,616 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, replacement:damage-prevention` | 3,844 | 8,602 | 8,622 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:create-token` | 3,840 | 8,649 | 8,663 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:equip` | 3,840 | 8,587 | 8,601 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:unparsed-this-creature-can` | 3,840 | 8,585 | 8,608 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, mechanic_dependency:affinity-unsupported-wording` | 3,839 | 8,598 | 8,612 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:typed-spell-additional-cost-clause` | 3,839 | 8,579 | 8,682 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, effect_clause:life-change` | 3,838 | 8,606 | 8,620 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:put-onto-battlefield` | 3,838 | 8,594 | 8,609 |
| `continuous_layer:continuous-effect-layers-and-dependencies, replacement:damage-prevention, keyword_dependency:start-your-engines` | 3,838 | 8,576 | 8,582 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:delve` | 3,836 | 8,590 | 8,604 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:improvise` | 3,836 | 8,585 | 8,599 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:living-weapon` | 3,836 | 8,581 | 8,595 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:evoke` | 3,835 | 8,592 | 8,606 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:myriad` | 3,835 | 8,585 | 8,599 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, keyword_dependency:umbra-armor` | 3,835 | 8,577 | 8,591 |
| `continuous_layer:continuous-effect-layers-and-dependencies, effect_clause:create-token, keyword_dependency:start-your-engines` | 3,834 | 8,623 | 8,623 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:create-token, activated_effect:unparsed-investigate` | 3,834 | 8,575 | 8,589 |
| `continuous_layer:continuous-effect-layers-and-dependencies, keyword_dependency:start-your-engines, keyword_dependency:equip` | 3,834 | 8,561 | 8,561 |
| `continuous_layer:continuous-effect-layers-and-dependencies, activated_effect:unparsed-this-creature-can, keyword_dependency:start-your-engines` | 3,834 | 8,559 | 8,568 |

## Hard construction failures

- None in the pinned Commander-legal snapshot.

## Boundary

This is a minimum-known-blocker frontier for the pinned Commander-legal snapshot. It does not prove complete Comprehensive Rules behavior.
The JSON artifact contains every card, every represented material ability, canonical blocker sets, dependency categories, and the bounded one/two/three-family evaluation.
