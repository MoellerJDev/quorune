---
title: "Reusable rules piece matrix"
status: "generated"
authoritative_source: "coverage/reusable-piece-matrix.json.gz"
verified: "43cd60d36949b596aa41231fbdca4343d3a13d4d9e2177dc378c4356cffc7618"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Reusable rules piece matrix

Current Oracle IR material ability and residual spans plus all registered capabilities, mechanics, handlers, components, and pinned rule references. This inventories current source relations without claiming universal runtime completion.

Counts official ruling presence by Oracle ID. Ruling prose is not yet behaviorally classified, so these counts are composition evidence rather than coverage claims.

## Snapshot

- Profile: `commander_review`
- Ontology: `reusable-pieces-v1`
- Pieces: 1,366
- Cards indexed: 31,623
- Material abilities classified: 59,601
- Unclassified material spans: 0
- Mapped pinned rules: 809 / 3,300
- Applicable piece pairs: 28,564
- Covered piece pairs: 453

## Ontology classes

| Class | Pieces |
|---|---:|
| `actions_permissions` — Actions, permissions, and prohibitions | 34 |
| `card_forms` — Card types and specialized forms | 4 |
| `choices_continuations` — Modes, targets, choices, and continuations | 9 |
| `combat` — Combat | 22 |
| `compiler_cardprogram` — Compiler and CardProgram pieces | 426 |
| `continuous_effects` — Static abilities and continuous effects | 28 |
| `costs_mana` — Costs and mana | 7 |
| `events_mutations` — Typed events and mutations | 99 |
| `keyword_mechanics` — Keyword actions and keyword abilities | 543 |
| `multiplayer_commander` — Multiplayer, Commander, and profile pieces | 1 |
| `object_identity` — Object identity and lifetime | 27 |
| `one_shot_effects` — One-shot semantic effects | 131 |
| `players_format` — Players, relationships, and format state | 1 |
| `proposals` — Casting and activation proposals | 13 |
| `quantities` — Quantity and value expressions | 1 |
| `references` — References | 1 |
| `replacement_prevention` — Replacement and prevention | 17 |
| `triggers` — Triggers | 2 |

## Universal systems

| System | Status | Pieces | Blocking pieces |
|---|---|---:|---:|
| `action_legality_casting_activation_costs_mana` | `inventoried` | 54 | 6 |
| `combat` | `compositional` | 22 | 0 |
| `derived_characteristics_static_layers` | `inventoried` | 28 | 5 |
| `generic_triggers_stack_placement` | `inventoried` | 2 | 2 |
| `multiplayer_player_leaving_commander` | `represented` | 2 | 0 |
| `objects_identity_zones_faces_copies` | `compositional` | 31 | 0 |
| `replacement_prevention` | `inventoried` | 17 | 3 |
| `state_turn_loops_stabilization` | `inventoried` | 0 | 0 |
| `targets_modes_searches_references_choices` | `inventoried` | 11 | 6 |
| `typed_transactions_events_mutations` | `inventoried` | 230 | 67 |

## Highest current blocker leverage

| Piece | Class | Residuals | Sole blockers | Expected cards | Runtime | Assurance |
|---|---|---:|---:|---:|---|---|
| `residual.continuous_layer.continuous-effect-layers-and-dependencies` | `continuous_effects` | 9,268 | 3,602 | 3,602 | `absent` | `untested` |
| `residual.activated_effect.unparsed-clause-grammar` | `one_shot_effects` | 2,525 | 773 | 773 | `absent` | `untested` |
| `residual.effect_clause.unparsed-clause-grammar` | `one_shot_effects` | 2,612 | 432 | 432 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-611-continuous-effects` | `keyword_mechanics` | 480 | 199 | 199 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-509-declare-blockers-step` | `keyword_mechanics` | 428 | 158 | 158 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-111-tokens` | `keyword_mechanics` | 338 | 122 | 122 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-additional-cost-clause` | `one_shot_effects` | 123 | 122 | 122 | `absent` | `untested` |
| `residual.effect_clause.deal-damage` | `one_shot_effects` | 956 | 112 | 112 | `absent` | `untested` |
| `residual.effect_clause.exile` | `one_shot_effects` | 985 | 105 | 105 | `absent` | `untested` |
| `residual.effect_clause.destroy-target` | `one_shot_effects` | 572 | 98 | 98 | `absent` | `untested` |
| `residual.effect_clause.return` | `one_shot_effects` | 686 | 96 | 96 | `absent` | `untested` |
| `residual.activated_effect.deal-damage` | `one_shot_effects` | 479 | 87 | 87 | `absent` | `untested` |
| `residual.activated_effect.tap-state` | `one_shot_effects` | 322 | 83 | 83 | `absent` | `untested` |
| `residual.effect_clause.intrinsic-basic-land-type-mana-capability` | `one_shot_effects` | 106 | 70 | 70 | `absent` | `untested` |
| `residual.effect_clause.tap-state` | `one_shot_effects` | 373 | 69 | 69 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-result-clause` | `one_shot_effects` | 66 | 66 | 66 | `absent` | `untested` |
| `residual.activated_effect.return` | `one_shot_effects` | 418 | 65 | 65 | `absent` | `untested` |
| `residual.effect_clause.look-reveal` | `one_shot_effects` | 550 | 62 | 62 | `absent` | `untested` |
| `residual.activated_effect.create-token` | `one_shot_effects` | 474 | 58 | 58 | `absent` | `untested` |
| `residual.effect_clause.create-token` | `one_shot_effects` | 695 | 45 | 45 | `absent` | `untested` |
| `residual.activated_effect.destroy-target` | `one_shot_effects` | 151 | 42 | 42 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-508-declare-attackers-step` | `keyword_mechanics` | 135 | 39 | 39 | `absent` | `untested` |
| `residual.effect_clause.draw` | `one_shot_effects` | 551 | 38 | 38 | `absent` | `untested` |
| `residual.keyword_dependency.morph` | `keyword_mechanics` | 141 | 32 | 32 | `absent` | `untested` |
| `residual.activated_effect.exile` | `one_shot_effects` | 386 | 28 | 28 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-615-prevention-effects` | `keyword_mechanics` | 78 | 28 | 28 | `absent` | `untested` |
| `residual.effect_clause.counter` | `one_shot_effects` | 243 | 26 | 26 | `absent` | `untested` |
| `residual.activated_effect.put-counter` | `one_shot_effects` | 323 | 24 | 24 | `absent` | `untested` |
| `residual.activated_effect.draw` | `one_shot_effects` | 379 | 22 | 22 | `absent` | `untested` |
| `residual.activated_effect.put-onto-battlefield` | `one_shot_effects` | 288 | 19 | 19 | `absent` | `untested` |

## Boundary

Inventory and classification are not implementation or trust. Universal systems remain conservatively below snapshot-complete until all required rules, pieces, rulings, and interactions close.
