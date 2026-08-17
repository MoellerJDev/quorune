---
title: "Reusable rules piece matrix"
status: "generated"
authoritative_source: "coverage/reusable-piece-matrix.json.gz"
verified: "76e63bbcf4784c7861d83fd42416008396d09cbd8e05ffaa514ef0037b13ff68"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Reusable rules piece matrix

Current Oracle IR material ability and residual spans plus all registered capabilities, mechanics, handlers, components, and pinned rule references. This inventories current source relations without claiming universal runtime completion.

Counts official ruling presence by Oracle ID. Ruling prose is not yet behaviorally classified, so these counts are composition evidence rather than coverage claims.

## Snapshot

- Profile: `commander_review`
- Ontology: `reusable-pieces-v1`
- Pieces: 1,625
- Cards indexed: 31,623
- Material abilities classified: 59,571
- Unclassified material spans: 0
- Mapped pinned rules: 859 / 3,300
- Applicable piece pairs: 38,333
- Covered piece pairs: 660

## Ontology classes

| Class | Pieces |
|---|---:|
| `actions_permissions` — Actions, permissions, and prohibitions | 43 |
| `card_forms` — Card types and specialized forms | 4 |
| `choices_continuations` — Modes, targets, choices, and continuations | 13 |
| `combat` — Combat | 24 |
| `compiler_cardprogram` — Compiler and CardProgram pieces | 622 |
| `continuous_effects` — Static abilities and continuous effects | 36 |
| `costs_mana` — Costs and mana | 8 |
| `events_mutations` — Typed events and mutations | 108 |
| `keyword_mechanics` — Keyword actions and keyword abilities | 554 |
| `multiplayer_commander` — Multiplayer, Commander, and profile pieces | 1 |
| `object_identity` — Object identity and lifetime | 27 |
| `one_shot_effects` — One-shot semantic effects | 143 |
| `players_format` — Players, relationships, and format state | 1 |
| `proposals` — Casting and activation proposals | 17 |
| `quantities` — Quantity and value expressions | 1 |
| `references` — References | 1 |
| `replacement_prevention` — Replacement and prevention | 20 |
| `triggers` — Triggers | 2 |

## Universal systems

| System | Status | Pieces | Blocking pieces |
|---|---|---:|---:|
| `action_legality_casting_activation_costs_mana` | `inventoried` | 68 | 6 |
| `combat` | `compositional` | 24 | 0 |
| `derived_characteristics_static_layers` | `inventoried` | 36 | 7 |
| `generic_triggers_stack_placement` | `inventoried` | 2 | 2 |
| `multiplayer_player_leaving_commander` | `represented` | 2 | 0 |
| `objects_identity_zones_faces_copies` | `compositional` | 31 | 0 |
| `replacement_prevention` | `inventoried` | 20 | 4 |
| `state_turn_loops_stabilization` | `inventoried` | 0 | 0 |
| `targets_modes_searches_references_choices` | `inventoried` | 15 | 10 |
| `typed_transactions_events_mutations` | `inventoried` | 251 | 73 |

## Highest current blocker leverage

| Piece | Class | Residuals | Sole blockers | Expected cards | Runtime | Assurance |
|---|---|---:|---:|---:|---|---|
| `residual.continuous_layer.continuous-effect-layers-and-dependencies` | `continuous_effects` | 8,908 | 3,710 | 3,710 | `absent` | `untested` |
| `residual.effect_clause.unparsed-clause-grammar` | `one_shot_effects` | 2,904 | 294 | 294 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-611-continuous-effects` | `keyword_mechanics` | 515 | 241 | 241 | `absent` | `untested` |
| `residual.activated_effect.unparsed-clause-grammar` | `one_shot_effects` | 2,114 | 167 | 167 | `absent` | `untested` |
| `residual.replacement.damage-prevention` | `replacement_prevention` | 208 | 45 | 45 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-615-prevention-effects` | `keyword_mechanics` | 78 | 28 | 28 | `absent` | `untested` |
| `residual.activated_effect.return` | `one_shot_effects` | 417 | 26 | 26 | `absent` | `untested` |
| `residual.effect_clause.life-change` | `one_shot_effects` | 575 | 20 | 20 | `absent` | `untested` |
| `residual.keyword_dependency.unearth` | `keyword_mechanics` | 55 | 20 | 20 | `absent` | `untested` |
| `residual.keyword_dependency.cascade` | `keyword_mechanics` | 37 | 19 | 19 | `absent` | `untested` |
| `residual.activated_effect.life-change` | `one_shot_effects` | 269 | 18 | 18 | `absent` | `untested` |
| `residual.keyword_dependency.bestow` | `keyword_mechanics` | 42 | 17 | 17 | `absent` | `untested` |
| `residual.effect_clause.return` | `one_shot_effects` | 640 | 16 | 16 | `absent` | `untested` |
| `residual.effect_clause.draw` | `one_shot_effects` | 496 | 16 | 16 | `absent` | `untested` |
| `residual.activated_effect.create-token` | `one_shot_effects` | 330 | 16 | 16 | `absent` | `untested` |
| `residual.mechanic_dependency.affinity-unsupported-wording` | `keyword_mechanics` | 36 | 16 | 16 | `absent` | `untested` |
| `residual.activated_effect.exile` | `one_shot_effects` | 376 | 14 | 14 | `absent` | `untested` |
| `residual.activated_effect.put-onto-battlefield` | `one_shot_effects` | 288 | 14 | 14 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-additional-cost-clause` | `one_shot_effects` | 106 | 14 | 14 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-400-general` | `keyword_mechanics` | 26 | 14 | 14 | `absent` | `untested` |
| `residual.effect_clause.exile` | `one_shot_effects` | 629 | 13 | 13 | `absent` | `untested` |
| `residual.keyword_dependency.changeling` | `keyword_mechanics` | 62 | 13 | 13 | `absent` | `untested` |
| `residual.keyword_dependency.storm` | `keyword_mechanics` | 33 | 12 | 12 | `absent` | `untested` |
| `residual.effect_clause.sacrifice` | `one_shot_effects` | 114 | 11 | 11 | `absent` | `untested` |
| `residual.keyword_dependency.evoke` | `keyword_mechanics` | 30 | 11 | 11 | `absent` | `untested` |
| `residual.keyword_dependency.improvise` | `keyword_mechanics` | 23 | 11 | 11 | `absent` | `untested` |
| `residual.effect_clause.create-token` | `one_shot_effects` | 582 | 10 | 10 | `absent` | `untested` |
| `residual.keyword_dependency.delve` | `keyword_mechanics` | 28 | 10 | 10 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-725-the-monarch` | `keyword_mechanics` | 38 | 9 | 9 | `absent` | `untested` |
| `residual.keyword_dependency.banding` | `keyword_mechanics` | 13 | 9 | 9 | `absent` | `untested` |

## Boundary

Inventory and classification are not implementation or trust. Universal systems remain conservatively below snapshot-complete until all required rules, pieces, rulings, and interactions close.
