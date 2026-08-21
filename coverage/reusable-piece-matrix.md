---
title: "Reusable rules piece matrix"
status: "generated"
authoritative_source: "coverage/reusable-piece-matrix.json.gz"
verified: "750e2b2ee317ba544efaa18950831222f57b940859423f9fb1cbf6ec7beb218a"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Reusable rules piece matrix

Current Oracle IR material ability and residual spans plus all registered capabilities, mechanics, handlers, components, and pinned rule references. This inventories current source relations without claiming universal runtime completion.

Counts official ruling presence by Oracle ID. Ruling prose is not yet behaviorally classified, so these counts are composition evidence rather than coverage claims.

## Snapshot

- Profile: `commander_review`
- Ontology: `reusable-pieces-v1`
- Pieces: 1,742
- Cards indexed: 31,623
- Material abilities classified: 59,552
- Unclassified material spans: 0
- Mapped pinned rules: 898 / 3,309
- Applicable piece pairs: 42,603
- Covered piece pairs: 714

## Ontology classes

| Class | Pieces |
|---|---:|
| `actions_permissions` — Actions, permissions, and prohibitions | 54 |
| `card_forms` — Card types and specialized forms | 5 |
| `choices_continuations` — Modes, targets, choices, and continuations | 13 |
| `combat` — Combat | 24 |
| `compiler_cardprogram` — Compiler and CardProgram pieces | 715 |
| `continuous_effects` — Static abilities and continuous effects | 39 |
| `costs_mana` — Costs and mana | 8 |
| `events_mutations` — Typed events and mutations | 108 |
| `keyword_mechanics` — Keyword actions and keyword abilities | 544 |
| `multiplayer_commander` — Multiplayer, Commander, and profile pieces | 1 |
| `object_identity` — Object identity and lifetime | 29 |
| `one_shot_effects` — One-shot semantic effects | 156 |
| `players_format` — Players, relationships, and format state | 1 |
| `proposals` — Casting and activation proposals | 20 |
| `quantities` — Quantity and value expressions | 1 |
| `references` — References | 1 |
| `replacement_prevention` — Replacement and prevention | 21 |
| `triggers` — Triggers | 2 |

## Universal systems

| System | Status | Pieces | Blocking pieces |
|---|---|---:|---:|
| `action_legality_casting_activation_costs_mana` | `inventoried` | 82 | 6 |
| `combat` | `compositional` | 24 | 0 |
| `derived_characteristics_static_layers` | `inventoried` | 39 | 7 |
| `generic_triggers_stack_placement` | `inventoried` | 2 | 2 |
| `multiplayer_player_leaving_commander` | `represented` | 2 | 0 |
| `objects_identity_zones_faces_copies` | `compositional` | 34 | 0 |
| `replacement_prevention` | `inventoried` | 21 | 4 |
| `state_turn_loops_stabilization` | `inventoried` | 0 | 0 |
| `targets_modes_searches_references_choices` | `inventoried` | 15 | 10 |
| `typed_transactions_events_mutations` | `inventoried` | 264 | 78 |

## Highest current blocker leverage

| Piece | Class | Residuals | Sole blockers | Expected cards | Runtime | Assurance |
|---|---|---:|---:|---:|---|---|
| `residual.continuous_layer.continuous-effect-layers-and-dependencies` | `continuous_effects` | 8,807 | 3,806 | 3,806 | `absent` | `untested` |
| `residual.effect_clause.unparsed-clause-grammar` | `one_shot_effects` | 2,608 | 233 | 233 | `absent` | `untested` |
| `residual.activated_effect.unparsed-clause-grammar` | `one_shot_effects` | 2,024 | 139 | 139 | `absent` | `untested` |
| `residual.activated_effect.create-token` | `one_shot_effects` | 329 | 22 | 22 | `absent` | `untested` |
| `residual.replacement.damage-prevention` | `replacement_prevention` | 168 | 21 | 21 | `absent` | `untested` |
| `residual.effect_clause.exile` | `one_shot_effects` | 621 | 18 | 18 | `absent` | `untested` |
| `residual.effect_clause.create-token` | `one_shot_effects` | 580 | 17 | 17 | `absent` | `untested` |
| `residual.effect_clause.return` | `one_shot_effects` | 636 | 16 | 16 | `absent` | `untested` |
| `residual.effect_clause.life-change` | `one_shot_effects` | 555 | 16 | 16 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-additional-cost-clause` | `one_shot_effects` | 106 | 16 | 16 | `absent` | `untested` |
| `residual.mechanic_dependency.affinity-unsupported-wording` | `keyword_mechanics` | 36 | 16 | 16 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-400-general` | `keyword_mechanics` | 26 | 16 | 16 | `absent` | `untested` |
| `residual.activated_effect.exile` | `one_shot_effects` | 376 | 14 | 14 | `absent` | `untested` |
| `residual.activated_effect.put-onto-battlefield` | `one_shot_effects` | 288 | 14 | 14 | `absent` | `untested` |
| `residual.keyword_dependency.evoke` | `keyword_mechanics` | 30 | 12 | 12 | `absent` | `untested` |
| `residual.keyword_dependency.delve` | `keyword_mechanics` | 28 | 12 | 12 | `absent` | `untested` |
| `residual.keyword_dependency.improvise` | `keyword_mechanics` | 23 | 12 | 12 | `absent` | `untested` |
| `residual.effect_clause.sacrifice` | `one_shot_effects` | 110 | 11 | 11 | `absent` | `untested` |
| `residual.keyword_dependency.banding` | `keyword_mechanics` | 13 | 10 | 10 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-725-the-monarch` | `keyword_mechanics` | 38 | 9 | 9 | `absent` | `untested` |
| `residual.keyword_dependency.rebound` | `keyword_mechanics` | 34 | 9 | 9 | `absent` | `untested` |
| `residual.activated_effect.life-change` | `one_shot_effects` | 225 | 8 | 8 | `absent` | `untested` |
| `residual.effect_clause.add-mana` | `one_shot_effects` | 57 | 8 | 8 | `absent` | `untested` |
| `residual.keyword_dependency.start-your-engines` | `keyword_mechanics` | 40 | 8 | 8 | `absent` | `untested` |
| `residual.keyword_dependency.living-weapon` | `keyword_mechanics` | 19 | 8 | 8 | `absent` | `untested` |
| `residual.keyword_dependency.retrace` | `keyword_mechanics` | 17 | 8 | 8 | `absent` | `untested` |
| `residual.keyword_dependency.umbra-armor` | `keyword_mechanics` | 15 | 8 | 8 | `absent` | `untested` |
| `residual.keyword_dependency.enlist` | `keyword_mechanics` | 12 | 8 | 8 | `absent` | `untested` |
| `residual.keyword_dependency.equip` | `keyword_mechanics` | 25 | 7 | 7 | `absent` | `untested` |
| `residual.keyword_dependency.myriad` | `keyword_mechanics` | 23 | 7 | 7 | `absent` | `untested` |

## Boundary

Inventory and classification are not implementation or trust. Universal systems remain conservatively below snapshot-complete until all required rules, pieces, rulings, and interactions close.
