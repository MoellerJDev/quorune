---
title: "Reusable rules piece matrix"
status: "generated"
authoritative_source: "coverage/reusable-piece-matrix.json.gz"
verified: "9abebbaf6198fa3e6a53d5af851c15c45ac5343a4015a26c9137254e181cb308"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Reusable rules piece matrix

Current Oracle IR material ability and residual spans plus all registered capabilities, mechanics, handlers, components, and pinned rule references. This inventories current source relations without claiming universal runtime completion.

Counts official ruling presence by Oracle ID. Ruling prose is not yet behaviorally classified, so these counts are composition evidence rather than coverage claims.

## Snapshot

- Profile: `commander_review`
- Ontology: `reusable-pieces-v1`
- Pieces: 1,202
- Cards indexed: 31,623
- Material abilities classified: 59,562
- Unclassified material spans: 0
- Mapped pinned rules: 735 / 3,300
- Applicable piece pairs: 25,008
- Covered piece pairs: 258

## Ontology classes

| Class | Pieces |
|---|---:|
| `actions_permissions` — Actions, permissions, and prohibitions | 12 |
| `card_forms` — Card types and specialized forms | 4 |
| `choices_continuations` — Modes, targets, choices, and continuations | 6 |
| `combat` — Combat | 22 |
| `compiler_cardprogram` — Compiler and CardProgram pieces | 337 |
| `continuous_effects` — Static abilities and continuous effects | 16 |
| `costs_mana` — Costs and mana | 7 |
| `events_mutations` — Typed events and mutations | 85 |
| `keyword_mechanics` — Keyword actions and keyword abilities | 551 |
| `multiplayer_commander` — Multiplayer, Commander, and profile pieces | 1 |
| `object_identity` — Object identity and lifetime | 26 |
| `one_shot_effects` — One-shot semantic effects | 109 |
| `players_format` — Players, relationships, and format state | 1 |
| `proposals` — Casting and activation proposals | 6 |
| `quantities` — Quantity and value expressions | 1 |
| `references` — References | 1 |
| `replacement_prevention` — Replacement and prevention | 15 |
| `triggers` — Triggers | 2 |

## Universal systems

| System | Status | Pieces | Blocking pieces |
|---|---|---:|---:|
| `action_legality_casting_activation_costs_mana` | `inventoried` | 25 | 5 |
| `combat` | `compositional` | 22 | 0 |
| `derived_characteristics_static_layers` | `inventoried` | 16 | 5 |
| `generic_triggers_stack_placement` | `inventoried` | 2 | 2 |
| `multiplayer_player_leaving_commander` | `represented` | 2 | 0 |
| `objects_identity_zones_faces_copies` | `compositional` | 30 | 0 |
| `replacement_prevention` | `inventoried` | 15 | 3 |
| `state_turn_loops_stabilization` | `inventoried` | 0 | 0 |
| `targets_modes_searches_references_choices` | `inventoried` | 8 | 6 |
| `typed_transactions_events_mutations` | `inventoried` | 194 | 62 |

## Highest current blocker leverage

| Piece | Class | Residuals | Sole blockers | Expected cards | Runtime | Assurance |
|---|---|---:|---:|---:|---|---|
| `residual.continuous_layer.continuous-effect-layers-and-dependencies` | `continuous_effects` | 9,561 | 3,542 | 3,542 | `absent` | `untested` |
| `residual.activated_effect.unparsed-clause-grammar` | `one_shot_effects` | 2,592 | 720 | 720 | `absent` | `untested` |
| `residual.effect_clause.unparsed-clause-grammar` | `one_shot_effects` | 2,642 | 425 | 425 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-611-continuous-effects` | `keyword_mechanics` | 480 | 193 | 193 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-614-replacement-effects` | `keyword_mechanics` | 539 | 182 | 182 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-additional-cost-clause` | `one_shot_effects` | 155 | 154 | 154 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-509-declare-blockers-step` | `keyword_mechanics` | 428 | 148 | 148 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-111-tokens` | `keyword_mechanics` | 338 | 113 | 113 | `absent` | `untested` |
| `residual.effect_clause.return` | `one_shot_effects` | 721 | 111 | 111 | `absent` | `untested` |
| `residual.effect_clause.deal-damage` | `one_shot_effects` | 956 | 110 | 110 | `absent` | `untested` |
| `residual.effect_clause.exile` | `one_shot_effects` | 991 | 98 | 98 | `absent` | `untested` |
| `residual.effect_clause.destroy-target` | `one_shot_effects` | 572 | 97 | 97 | `absent` | `untested` |
| `residual.activated_effect.deal-damage` | `one_shot_effects` | 479 | 84 | 84 | `absent` | `untested` |
| `residual.activated_effect.return` | `one_shot_effects` | 450 | 83 | 83 | `absent` | `untested` |
| `residual.activated_effect.tap-state` | `one_shot_effects` | 322 | 75 | 75 | `absent` | `untested` |
| `residual.effect_clause.tap-state` | `one_shot_effects` | 373 | 67 | 67 | `absent` | `untested` |
| `residual.effect_clause.look-reveal` | `one_shot_effects` | 552 | 60 | 60 | `absent` | `untested` |
| `residual.activated_effect.create-token` | `one_shot_effects` | 475 | 54 | 54 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-result-clause` | `one_shot_effects` | 52 | 51 | 51 | `absent` | `untested` |
| `residual.effect_clause.draw` | `one_shot_effects` | 577 | 46 | 46 | `absent` | `untested` |
| `residual.effect_clause.create-token` | `one_shot_effects` | 707 | 43 | 43 | `absent` | `untested` |
| `residual.activated_effect.destroy-target` | `one_shot_effects` | 151 | 42 | 42 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-508-declare-attackers-step` | `keyword_mechanics` | 135 | 39 | 39 | `absent` | `untested` |
| `residual.activated_effect.put-counter` | `one_shot_effects` | 347 | 36 | 36 | `absent` | `untested` |
| `residual.keyword_dependency.hexproof` | `keyword_mechanics` | 89 | 35 | 35 | `absent` | `untested` |
| `residual.keyword_dependency.indestructible` | `keyword_mechanics` | 145 | 32 | 32 | `absent` | `untested` |
| `residual.keyword_dependency.morph` | `keyword_mechanics` | 141 | 31 | 31 | `absent` | `untested` |
| `residual.activated_effect.draw` | `one_shot_effects` | 412 | 30 | 30 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-119-life` | `keyword_mechanics` | 76 | 30 | 30 | `absent` | `untested` |
| `residual.keyword_dependency.first-strike` | `keyword_mechanics` | 42 | 30 | 30 | `absent` | `untested` |

## Boundary

Inventory and classification are not implementation or trust. Universal systems remain conservatively below snapshot-complete until all required rules, pieces, rulings, and interactions close.
