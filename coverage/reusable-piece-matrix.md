---
title: "Reusable rules piece matrix"
status: "generated"
authoritative_source: "coverage/reusable-piece-matrix.json.gz"
verified: "428ba420444d83ef8fd41d63b36997681147648d980cc8eb265e52a0e52ae696"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Reusable rules piece matrix

Current Oracle IR material ability and residual spans plus all registered capabilities, mechanics, handlers, components, and pinned rule references. This inventories current source relations without claiming universal runtime completion.

Counts official ruling presence by Oracle ID. Ruling prose is not yet behaviorally classified, so these counts are composition evidence rather than coverage claims.

## Snapshot

- Profile: `commander_review`
- Ontology: `reusable-pieces-v1`
- Pieces: 1,472
- Cards indexed: 31,623
- Material abilities classified: 59,649
- Unclassified material spans: 0
- Mapped pinned rules: 840 / 3,300
- Applicable piece pairs: 35,044
- Covered piece pairs: 629

## Ontology classes

| Class | Pieces |
|---|---:|
| `actions_permissions` — Actions, permissions, and prohibitions | 39 |
| `card_forms` — Card types and specialized forms | 4 |
| `choices_continuations` — Modes, targets, choices, and continuations | 13 |
| `combat` — Combat | 24 |
| `compiler_cardprogram` — Compiler and CardProgram pieces | 482 |
| `continuous_effects` — Static abilities and continuous effects | 33 |
| `costs_mana` — Costs and mana | 8 |
| `events_mutations` — Typed events and mutations | 106 |
| `keyword_mechanics` — Keyword actions and keyword abilities | 553 |
| `multiplayer_commander` — Multiplayer, Commander, and profile pieces | 1 |
| `object_identity` — Object identity and lifetime | 27 |
| `one_shot_effects` — One-shot semantic effects | 140 |
| `players_format` — Players, relationships, and format state | 1 |
| `proposals` — Casting and activation proposals | 17 |
| `quantities` — Quantity and value expressions | 1 |
| `references` — References | 1 |
| `replacement_prevention` — Replacement and prevention | 20 |
| `triggers` — Triggers | 2 |

## Universal systems

| System | Status | Pieces | Blocking pieces |
|---|---|---:|---:|
| `action_legality_casting_activation_costs_mana` | `inventoried` | 64 | 6 |
| `combat` | `compositional` | 24 | 0 |
| `derived_characteristics_static_layers` | `inventoried` | 33 | 7 |
| `generic_triggers_stack_placement` | `inventoried` | 2 | 2 |
| `multiplayer_player_leaving_commander` | `represented` | 2 | 0 |
| `objects_identity_zones_faces_copies` | `compositional` | 31 | 0 |
| `replacement_prevention` | `inventoried` | 20 | 4 |
| `state_turn_loops_stabilization` | `inventoried` | 0 | 0 |
| `targets_modes_searches_references_choices` | `inventoried` | 15 | 10 |
| `typed_transactions_events_mutations` | `inventoried` | 246 | 73 |

## Highest current blocker leverage

| Piece | Class | Residuals | Sole blockers | Expected cards | Runtime | Assurance |
|---|---|---:|---:|---:|---|---|
| `residual.continuous_layer.continuous-effect-layers-and-dependencies` | `continuous_effects` | 9,049 | 3,743 | 3,743 | `absent` | `untested` |
| `residual.effect_clause.unparsed-clause-grammar` | `one_shot_effects` | 2,955 | 283 | 283 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-611-continuous-effects` | `keyword_mechanics` | 515 | 237 | 237 | `absent` | `untested` |
| `residual.activated_effect.unparsed-clause-grammar` | `one_shot_effects` | 2,154 | 185 | 185 | `absent` | `untested` |
| `residual.replacement.damage-prevention` | `replacement_prevention` | 209 | 45 | 45 | `absent` | `untested` |
| `residual.keyword_dependency.morph` | `keyword_mechanics` | 141 | 36 | 36 | `absent` | `untested` |
| `residual.activated_effect.tap-state` | `one_shot_effects` | 318 | 34 | 34 | `absent` | `untested` |
| `residual.activated_effect.deal-damage` | `one_shot_effects` | 428 | 28 | 28 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-615-prevention-effects` | `keyword_mechanics` | 78 | 28 | 28 | `absent` | `untested` |
| `residual.activated_effect.return` | `one_shot_effects` | 417 | 26 | 26 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-additional-cost-clause` | `one_shot_effects` | 123 | 26 | 26 | `absent` | `untested` |
| `residual.effect_clause.destroy-target` | `one_shot_effects` | 553 | 21 | 21 | `absent` | `untested` |
| `residual.effect_clause.life-change` | `one_shot_effects` | 585 | 19 | 19 | `absent` | `untested` |
| `residual.keyword_dependency.unearth` | `keyword_mechanics` | 55 | 19 | 19 | `absent` | `untested` |
| `residual.keyword_dependency.cascade` | `keyword_mechanics` | 37 | 18 | 18 | `absent` | `untested` |
| `residual.effect_clause.exile` | `one_shot_effects` | 636 | 17 | 17 | `absent` | `untested` |
| `residual.activated_effect.life-change` | `one_shot_effects` | 270 | 17 | 17 | `absent` | `untested` |
| `residual.keyword_dependency.bestow` | `keyword_mechanics` | 42 | 17 | 17 | `absent` | `untested` |
| `residual.effect_clause.return` | `one_shot_effects` | 643 | 16 | 16 | `absent` | `untested` |
| `residual.activated_effect.create-token` | `one_shot_effects` | 332 | 16 | 16 | `absent` | `untested` |
| `residual.mechanic_dependency.affinity-unsupported-wording` | `keyword_mechanics` | 36 | 16 | 16 | `absent` | `untested` |
| `residual.effect_clause.create-token` | `one_shot_effects` | 598 | 15 | 15 | `absent` | `untested` |
| `residual.activated_effect.exile` | `one_shot_effects` | 386 | 15 | 15 | `absent` | `untested` |
| `residual.activated_effect.put-onto-battlefield` | `one_shot_effects` | 288 | 14 | 14 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-400-general` | `keyword_mechanics` | 26 | 14 | 14 | `absent` | `untested` |
| `residual.effect_clause.draw` | `one_shot_effects` | 499 | 13 | 13 | `absent` | `untested` |
| `residual.keyword_dependency.changeling` | `keyword_mechanics` | 62 | 13 | 13 | `absent` | `untested` |
| `residual.activated_effect.destroy-target` | `one_shot_effects` | 147 | 12 | 12 | `absent` | `untested` |
| `residual.keyword_dependency.storm` | `keyword_mechanics` | 33 | 12 | 12 | `absent` | `untested` |
| `residual.effect_clause.sacrifice` | `one_shot_effects` | 114 | 11 | 11 | `absent` | `untested` |

## Boundary

Inventory and classification are not implementation or trust. Universal systems remain conservatively below snapshot-complete until all required rules, pieces, rulings, and interactions close.
