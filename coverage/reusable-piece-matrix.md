---
title: "Reusable rules piece matrix"
status: "generated"
authoritative_source: "coverage/reusable-piece-matrix.json.gz"
verified: "7232d47fef889604d68f1bd200c09c475b8d37d7f549a701fff50f831f174fe0"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Reusable rules piece matrix

Current Oracle IR material ability and residual spans plus all registered capabilities, mechanics, handlers, components, and pinned rule references. This inventories current source relations without claiming universal runtime completion.

Counts official ruling presence by Oracle ID. Ruling prose is not yet behaviorally classified, so these counts are composition evidence rather than coverage claims.

## Snapshot

- Profile: `commander_review`
- Ontology: `reusable-pieces-v1`
- Pieces: 1,458
- Cards indexed: 31,623
- Material abilities classified: 59,649
- Unclassified material spans: 0
- Mapped pinned rules: 833 / 3,300
- Applicable piece pairs: 34,022
- Covered piece pairs: 620

## Ontology classes

| Class | Pieces |
|---|---:|
| `actions_permissions` — Actions, permissions, and prohibitions | 38 |
| `card_forms` — Card types and specialized forms | 4 |
| `choices_continuations` — Modes, targets, choices, and continuations | 13 |
| `combat` — Combat | 24 |
| `compiler_cardprogram` — Compiler and CardProgram pieces | 476 |
| `continuous_effects` — Static abilities and continuous effects | 33 |
| `costs_mana` — Costs and mana | 8 |
| `events_mutations` — Typed events and mutations | 105 |
| `keyword_mechanics` — Keyword actions and keyword abilities | 548 |
| `multiplayer_commander` — Multiplayer, Commander, and profile pieces | 1 |
| `object_identity` — Object identity and lifetime | 27 |
| `one_shot_effects` — One-shot semantic effects | 140 |
| `players_format` — Players, relationships, and format state | 1 |
| `proposals` — Casting and activation proposals | 17 |
| `quantities` — Quantity and value expressions | 1 |
| `references` — References | 1 |
| `replacement_prevention` — Replacement and prevention | 19 |
| `triggers` — Triggers | 2 |

## Universal systems

| System | Status | Pieces | Blocking pieces |
|---|---|---:|---:|
| `action_legality_casting_activation_costs_mana` | `inventoried` | 63 | 6 |
| `combat` | `compositional` | 24 | 0 |
| `derived_characteristics_static_layers` | `inventoried` | 33 | 7 |
| `generic_triggers_stack_placement` | `inventoried` | 2 | 2 |
| `multiplayer_player_leaving_commander` | `represented` | 2 | 0 |
| `objects_identity_zones_faces_copies` | `compositional` | 31 | 0 |
| `replacement_prevention` | `inventoried` | 19 | 4 |
| `state_turn_loops_stabilization` | `inventoried` | 0 | 0 |
| `targets_modes_searches_references_choices` | `inventoried` | 15 | 10 |
| `typed_transactions_events_mutations` | `inventoried` | 245 | 73 |

## Highest current blocker leverage

| Piece | Class | Residuals | Sole blockers | Expected cards | Runtime | Assurance |
|---|---|---:|---:|---:|---|---|
| `residual.continuous_layer.continuous-effect-layers-and-dependencies` | `continuous_effects` | 9,049 | 3,663 | 3,663 | `absent` | `untested` |
| `residual.effect_clause.unparsed-clause-grammar` | `one_shot_effects` | 2,959 | 253 | 253 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-611-continuous-effects` | `keyword_mechanics` | 515 | 234 | 234 | `absent` | `untested` |
| `residual.activated_effect.unparsed-clause-grammar` | `one_shot_effects` | 2,154 | 181 | 181 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-111-tokens` | `keyword_mechanics` | 338 | 127 | 127 | `absent` | `untested` |
| `residual.replacement.damage-prevention` | `replacement_prevention` | 209 | 45 | 45 | `absent` | `untested` |
| `residual.activated_effect.create-token` | `one_shot_effects` | 473 | 36 | 36 | `absent` | `untested` |
| `residual.keyword_dependency.morph` | `keyword_mechanics` | 141 | 36 | 36 | `absent` | `untested` |
| `residual.effect_clause.create-token` | `one_shot_effects` | 672 | 35 | 35 | `absent` | `untested` |
| `residual.activated_effect.tap-state` | `one_shot_effects` | 318 | 34 | 34 | `absent` | `untested` |
| `residual.activated_effect.deal-damage` | `one_shot_effects` | 436 | 28 | 28 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-615-prevention-effects` | `keyword_mechanics` | 78 | 28 | 28 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-additional-cost-clause` | `one_shot_effects` | 123 | 26 | 26 | `absent` | `untested` |
| `residual.activated_effect.return` | `one_shot_effects` | 417 | 25 | 25 | `absent` | `untested` |
| `residual.effect_clause.destroy-target` | `one_shot_effects` | 582 | 21 | 21 | `absent` | `untested` |
| `residual.effect_clause.life-change` | `one_shot_effects` | 621 | 19 | 19 | `absent` | `untested` |
| `residual.keyword_dependency.cascade` | `keyword_mechanics` | 37 | 18 | 18 | `absent` | `untested` |
| `residual.effect_clause.exile` | `one_shot_effects` | 638 | 17 | 17 | `absent` | `untested` |
| `residual.keyword_dependency.unearth` | `keyword_mechanics` | 55 | 17 | 17 | `absent` | `untested` |
| `residual.keyword_dependency.bestow` | `keyword_mechanics` | 42 | 17 | 17 | `absent` | `untested` |
| `residual.effect_clause.return` | `one_shot_effects` | 650 | 16 | 16 | `absent` | `untested` |
| `residual.activated_effect.life-change` | `one_shot_effects` | 278 | 16 | 16 | `absent` | `untested` |
| `residual.mechanic_dependency.affinity-unsupported-wording` | `keyword_mechanics` | 36 | 16 | 16 | `absent` | `untested` |
| `residual.activated_effect.exile` | `one_shot_effects` | 386 | 14 | 14 | `absent` | `untested` |
| `residual.activated_effect.put-onto-battlefield` | `one_shot_effects` | 288 | 14 | 14 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-400-general` | `keyword_mechanics` | 26 | 14 | 14 | `absent` | `untested` |
| `residual.keyword_dependency.changeling` | `keyword_mechanics` | 62 | 13 | 13 | `absent` | `untested` |
| `residual.effect_clause.draw` | `one_shot_effects` | 508 | 12 | 12 | `absent` | `untested` |
| `residual.activated_effect.destroy-target` | `one_shot_effects` | 150 | 12 | 12 | `absent` | `untested` |
| `residual.keyword_dependency.delve` | `keyword_mechanics` | 28 | 10 | 10 | `absent` | `untested` |

## Boundary

Inventory and classification are not implementation or trust. Universal systems remain conservatively below snapshot-complete until all required rules, pieces, rulings, and interactions close.
