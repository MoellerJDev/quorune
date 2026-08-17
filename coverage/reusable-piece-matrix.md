---
title: "Reusable rules piece matrix"
status: "generated"
authoritative_source: "coverage/reusable-piece-matrix.json.gz"
verified: "5a5c3c5497180283864e5c053d0078978fe68bc81618276b0c94a6219db8ee39"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Reusable rules piece matrix

Current Oracle IR material ability and residual spans plus all registered capabilities, mechanics, handlers, components, and pinned rule references. This inventories current source relations without claiming universal runtime completion.

Counts official ruling presence by Oracle ID. Ruling prose is not yet behaviorally classified, so these counts are composition evidence rather than coverage claims.

## Snapshot

- Profile: `commander_review`
- Ontology: `reusable-pieces-v1`
- Pieces: 1,646
- Cards indexed: 31,623
- Material abilities classified: 59,567
- Unclassified material spans: 0
- Mapped pinned rules: 865 / 3,300
- Applicable piece pairs: 39,290
- Covered piece pairs: 663

## Ontology classes

| Class | Pieces |
|---|---:|
| `actions_permissions` — Actions, permissions, and prohibitions | 45 |
| `card_forms` — Card types and specialized forms | 4 |
| `choices_continuations` — Modes, targets, choices, and continuations | 13 |
| `combat` — Combat | 24 |
| `compiler_cardprogram` — Compiler and CardProgram pieces | 633 |
| `continuous_effects` — Static abilities and continuous effects | 36 |
| `costs_mana` — Costs and mana | 8 |
| `events_mutations` — Typed events and mutations | 108 |
| `keyword_mechanics` — Keyword actions and keyword abilities | 552 |
| `multiplayer_commander` — Multiplayer, Commander, and profile pieces | 1 |
| `object_identity` — Object identity and lifetime | 28 |
| `one_shot_effects` — One-shot semantic effects | 148 |
| `players_format` — Players, relationships, and format state | 1 |
| `proposals` — Casting and activation proposals | 20 |
| `quantities` — Quantity and value expressions | 1 |
| `references` — References | 1 |
| `replacement_prevention` — Replacement and prevention | 21 |
| `triggers` — Triggers | 2 |

## Universal systems

| System | Status | Pieces | Blocking pieces |
|---|---|---:|---:|
| `action_legality_casting_activation_costs_mana` | `inventoried` | 73 | 6 |
| `combat` | `compositional` | 24 | 0 |
| `derived_characteristics_static_layers` | `inventoried` | 36 | 7 |
| `generic_triggers_stack_placement` | `inventoried` | 2 | 2 |
| `multiplayer_player_leaving_commander` | `represented` | 2 | 0 |
| `objects_identity_zones_faces_copies` | `compositional` | 32 | 0 |
| `replacement_prevention` | `inventoried` | 21 | 4 |
| `state_turn_loops_stabilization` | `inventoried` | 0 | 0 |
| `targets_modes_searches_references_choices` | `inventoried` | 15 | 10 |
| `typed_transactions_events_mutations` | `inventoried` | 256 | 75 |

## Highest current blocker leverage

| Piece | Class | Residuals | Sole blockers | Expected cards | Runtime | Assurance |
|---|---|---:|---:|---:|---|---|
| `residual.continuous_layer.continuous-effect-layers-and-dependencies` | `continuous_effects` | 8,884 | 3,728 | 3,728 | `absent` | `untested` |
| `residual.effect_clause.unparsed-clause-grammar` | `one_shot_effects` | 2,902 | 298 | 298 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-611-continuous-effects` | `keyword_mechanics` | 515 | 244 | 244 | `absent` | `untested` |
| `residual.activated_effect.unparsed-clause-grammar` | `one_shot_effects` | 2,114 | 167 | 167 | `absent` | `untested` |
| `residual.replacement.damage-prevention` | `replacement_prevention` | 206 | 45 | 45 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-615-prevention-effects` | `keyword_mechanics` | 78 | 28 | 28 | `absent` | `untested` |
| `residual.keyword_dependency.cascade` | `keyword_mechanics` | 37 | 19 | 19 | `absent` | `untested` |
| `residual.keyword_dependency.bestow` | `keyword_mechanics` | 42 | 17 | 17 | `absent` | `untested` |
| `residual.effect_clause.return` | `one_shot_effects` | 640 | 16 | 16 | `absent` | `untested` |
| `residual.effect_clause.life-change` | `one_shot_effects` | 557 | 16 | 16 | `absent` | `untested` |
| `residual.effect_clause.draw` | `one_shot_effects` | 495 | 16 | 16 | `absent` | `untested` |
| `residual.activated_effect.create-token` | `one_shot_effects` | 330 | 16 | 16 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-additional-cost-clause` | `one_shot_effects` | 106 | 16 | 16 | `absent` | `untested` |
| `residual.mechanic_dependency.affinity-unsupported-wording` | `keyword_mechanics` | 36 | 16 | 16 | `absent` | `untested` |
| `residual.effect_clause.exile` | `one_shot_effects` | 629 | 14 | 14 | `absent` | `untested` |
| `residual.activated_effect.exile` | `one_shot_effects` | 376 | 14 | 14 | `absent` | `untested` |
| `residual.activated_effect.put-onto-battlefield` | `one_shot_effects` | 288 | 14 | 14 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-400-general` | `keyword_mechanics` | 26 | 14 | 14 | `absent` | `untested` |
| `residual.keyword_dependency.changeling` | `keyword_mechanics` | 62 | 13 | 13 | `absent` | `untested` |
| `residual.keyword_dependency.storm` | `keyword_mechanics` | 33 | 12 | 12 | `absent` | `untested` |
| `residual.effect_clause.sacrifice` | `one_shot_effects` | 114 | 11 | 11 | `absent` | `untested` |
| `residual.keyword_dependency.evoke` | `keyword_mechanics` | 30 | 11 | 11 | `absent` | `untested` |
| `residual.keyword_dependency.improvise` | `keyword_mechanics` | 23 | 11 | 11 | `absent` | `untested` |
| `residual.effect_clause.create-token` | `one_shot_effects` | 582 | 10 | 10 | `absent` | `untested` |
| `residual.keyword_dependency.delve` | `keyword_mechanics` | 28 | 10 | 10 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-725-the-monarch` | `keyword_mechanics` | 38 | 9 | 9 | `absent` | `untested` |
| `residual.keyword_dependency.banding` | `keyword_mechanics` | 13 | 9 | 9 | `absent` | `untested` |
| `residual.activated_effect.life-change` | `one_shot_effects` | 224 | 8 | 8 | `absent` | `untested` |
| `residual.effect_clause.add-mana` | `one_shot_effects` | 57 | 8 | 8 | `absent` | `untested` |
| `residual.keyword_dependency.rebound` | `keyword_mechanics` | 34 | 8 | 8 | `absent` | `untested` |

## Boundary

Inventory and classification are not implementation or trust. Universal systems remain conservatively below snapshot-complete until all required rules, pieces, rulings, and interactions close.
