---
title: "Reusable rules piece matrix"
status: "generated"
authoritative_source: "coverage/reusable-piece-matrix.json.gz"
verified: "727d231a526ef81bb4fa4dd8871996a3e15bc362f0a8ab6b7414c717cec54617"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Reusable rules piece matrix

Current Oracle IR material ability and residual spans plus all registered capabilities, mechanics, handlers, components, and pinned rule references. This inventories current source relations without claiming universal runtime completion.

Counts official ruling presence by Oracle ID. Ruling prose is not yet behaviorally classified, so these counts are composition evidence rather than coverage claims.

## Snapshot

- Profile: `commander_review`
- Ontology: `reusable-pieces-v1`
- Pieces: 1,385
- Cards indexed: 31,623
- Material abilities classified: 59,601
- Unclassified material spans: 0
- Mapped pinned rules: 812 / 3,300
- Applicable piece pairs: 30,316
- Covered piece pairs: 457

## Ontology classes

| Class | Pieces |
|---|---:|
| `actions_permissions` — Actions, permissions, and prohibitions | 34 |
| `card_forms` — Card types and specialized forms | 4 |
| `choices_continuations` — Modes, targets, choices, and continuations | 13 |
| `combat` — Combat | 24 |
| `compiler_cardprogram` — Compiler and CardProgram pieces | 430 |
| `continuous_effects` — Static abilities and continuous effects | 33 |
| `costs_mana` — Costs and mana | 7 |
| `events_mutations` — Typed events and mutations | 99 |
| `keyword_mechanics` — Keyword actions and keyword abilities | 541 |
| `multiplayer_commander` — Multiplayer, Commander, and profile pieces | 1 |
| `object_identity` — Object identity and lifetime | 27 |
| `one_shot_effects` — One-shot semantic effects | 136 |
| `players_format` — Players, relationships, and format state | 1 |
| `proposals` — Casting and activation proposals | 13 |
| `quantities` — Quantity and value expressions | 1 |
| `references` — References | 1 |
| `replacement_prevention` — Replacement and prevention | 18 |
| `triggers` — Triggers | 2 |

## Universal systems

| System | Status | Pieces | Blocking pieces |
|---|---|---:|---:|
| `action_legality_casting_activation_costs_mana` | `inventoried` | 54 | 6 |
| `combat` | `compositional` | 24 | 0 |
| `derived_characteristics_static_layers` | `inventoried` | 33 | 7 |
| `generic_triggers_stack_placement` | `inventoried` | 2 | 2 |
| `multiplayer_player_leaving_commander` | `represented` | 2 | 0 |
| `objects_identity_zones_faces_copies` | `compositional` | 31 | 0 |
| `replacement_prevention` | `inventoried` | 18 | 4 |
| `state_turn_loops_stabilization` | `inventoried` | 0 | 0 |
| `targets_modes_searches_references_choices` | `inventoried` | 15 | 10 |
| `typed_transactions_events_mutations` | `inventoried` | 235 | 71 |

## Highest current blocker leverage

| Piece | Class | Residuals | Sole blockers | Expected cards | Runtime | Assurance |
|---|---|---:|---:|---:|---|---|
| `residual.continuous_layer.continuous-effect-layers-and-dependencies` | `continuous_effects` | 9,180 | 3,627 | 3,627 | `absent` | `untested` |
| `residual.activated_effect.unparsed-clause-grammar` | `one_shot_effects` | 2,340 | 254 | 254 | `absent` | `untested` |
| `residual.effect_clause.unparsed-clause-grammar` | `one_shot_effects` | 2,947 | 252 | 252 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-611-continuous-effects` | `keyword_mechanics` | 480 | 204 | 204 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-111-tokens` | `keyword_mechanics` | 338 | 123 | 123 | `absent` | `untested` |
| `residual.effect_clause.intrinsic-basic-land-type-mana-capability` | `one_shot_effects` | 106 | 70 | 70 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-result-clause` | `one_shot_effects` | 157 | 66 | 66 | `absent` | `untested` |
| `residual.replacement.damage-prevention` | `replacement_prevention` | 208 | 45 | 45 | `absent` | `untested` |
| `residual.activated_effect.create-token` | `one_shot_effects` | 474 | 36 | 36 | `absent` | `untested` |
| `residual.effect_clause.create-token` | `one_shot_effects` | 657 | 35 | 35 | `absent` | `untested` |
| `residual.keyword_dependency.morph` | `keyword_mechanics` | 141 | 35 | 35 | `absent` | `untested` |
| `residual.activated_effect.tap-state` | `one_shot_effects` | 322 | 34 | 34 | `absent` | `untested` |
| `residual.activated_effect.deal-damage` | `one_shot_effects` | 436 | 28 | 28 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-615-prevention-effects` | `keyword_mechanics` | 78 | 28 | 28 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-additional-cost-clause` | `one_shot_effects` | 123 | 26 | 26 | `absent` | `untested` |
| `residual.activated_effect.return` | `one_shot_effects` | 418 | 25 | 25 | `absent` | `untested` |
| `residual.effect_clause.destroy-target` | `one_shot_effects` | 569 | 20 | 20 | `absent` | `untested` |
| `residual.effect_clause.life-change` | `one_shot_effects` | 601 | 19 | 19 | `absent` | `untested` |
| `residual.keyword_dependency.unearth` | `keyword_mechanics` | 55 | 17 | 17 | `absent` | `untested` |
| `residual.keyword_dependency.bestow` | `keyword_mechanics` | 42 | 17 | 17 | `absent` | `untested` |
| `residual.keyword_dependency.cascade` | `keyword_mechanics` | 37 | 17 | 17 | `absent` | `untested` |
| `residual.effect_clause.return` | `one_shot_effects` | 637 | 16 | 16 | `absent` | `untested` |
| `residual.effect_clause.exile` | `one_shot_effects` | 622 | 16 | 16 | `absent` | `untested` |
| `residual.activated_effect.life-change` | `one_shot_effects` | 280 | 16 | 16 | `absent` | `untested` |
| `residual.mechanic_dependency.affinity-unsupported-wording` | `keyword_mechanics` | 36 | 16 | 16 | `absent` | `untested` |
| `residual.activated_effect.exile` | `one_shot_effects` | 386 | 14 | 14 | `absent` | `untested` |
| `residual.activated_effect.put-onto-battlefield` | `one_shot_effects` | 288 | 14 | 14 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-400-general` | `keyword_mechanics` | 26 | 14 | 14 | `absent` | `untested` |
| `residual.effect_clause.draw` | `one_shot_effects` | 487 | 12 | 12 | `absent` | `untested` |
| `residual.activated_effect.destroy-target` | `one_shot_effects` | 151 | 12 | 12 | `absent` | `untested` |

## Boundary

Inventory and classification are not implementation or trust. Universal systems remain conservatively below snapshot-complete until all required rules, pieces, rulings, and interactions close.
