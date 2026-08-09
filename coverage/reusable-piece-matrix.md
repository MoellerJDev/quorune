---
title: "Reusable rules piece matrix"
status: "generated"
authoritative_source: "coverage/reusable-piece-matrix.json.gz"
verified: "b1c6d25b408f3badcc7934cf263800de104cda730f58dc2f124b4593c2c7dc80"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Reusable rules piece matrix

Current Oracle IR material ability and residual spans plus all registered capabilities, mechanics, handlers, components, and pinned rule references. This inventories current source relations without claiming universal runtime completion.

Counts official ruling presence by Oracle ID. Ruling prose is not yet behaviorally classified, so these counts are composition evidence rather than coverage claims.

## Snapshot

- Profile: `commander_review`
- Ontology: `reusable-pieces-v1`
- Pieces: 1,159
- Cards indexed: 31,623
- Material abilities classified: 59,817
- Unclassified material spans: 0
- Mapped pinned rules: 720 / 3,300
- Applicable piece pairs: 23,845
- Covered piece pairs: 126

## Ontology classes

| Class | Pieces |
|---|---:|
| `actions_permissions` — Actions, permissions, and prohibitions | 7 |
| `card_forms` — Card types and specialized forms | 4 |
| `choices_continuations` — Modes, targets, choices, and continuations | 6 |
| `combat` — Combat | 22 |
| `compiler_cardprogram` — Compiler and CardProgram pieces | 310 |
| `continuous_effects` — Static abilities and continuous effects | 16 |
| `costs_mana` — Costs and mana | 7 |
| `events_mutations` — Typed events and mutations | 83 |
| `keyword_mechanics` — Keyword actions and keyword abilities | 548 |
| `multiplayer_commander` — Multiplayer, Commander, and profile pieces | 1 |
| `object_identity` — Object identity and lifetime | 26 |
| `one_shot_effects` — One-shot semantic effects | 104 |
| `players_format` — Players, relationships, and format state | 1 |
| `proposals` — Casting and activation proposals | 5 |
| `quantities` — Quantity and value expressions | 1 |
| `references` — References | 1 |
| `replacement_prevention` — Replacement and prevention | 15 |
| `triggers` — Triggers | 2 |

## Universal systems

| System | Status | Pieces | Blocking pieces |
|---|---|---:|---:|
| `action_legality_casting_activation_costs_mana` | `inventoried` | 19 | 5 |
| `combat` | `compositional` | 22 | 0 |
| `derived_characteristics_static_layers` | `inventoried` | 16 | 5 |
| `generic_triggers_stack_placement` | `inventoried` | 2 | 2 |
| `multiplayer_player_leaving_commander` | `represented` | 2 | 0 |
| `objects_identity_zones_faces_copies` | `compositional` | 30 | 0 |
| `replacement_prevention` | `inventoried` | 15 | 3 |
| `state_turn_loops_stabilization` | `inventoried` | 0 | 0 |
| `targets_modes_searches_references_choices` | `inventoried` | 8 | 6 |
| `typed_transactions_events_mutations` | `inventoried` | 187 | 58 |

## Highest current blocker leverage

| Piece | Class | Residuals | Sole blockers | Expected cards | Runtime | Assurance |
|---|---|---:|---:|---:|---|---|
| `residual.continuous_layer.continuous-effect-layers-and-dependencies` | `continuous_effects` | 9,561 | 3,525 | 3,525 | `absent` | `untested` |
| `residual.activated_effect.unparsed-clause-grammar` | `one_shot_effects` | 2,689 | 765 | 765 | `absent` | `untested` |
| `residual.effect_clause.unparsed-clause-grammar` | `one_shot_effects` | 2,790 | 480 | 480 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-611-continuous-effects` | `keyword_mechanics` | 567 | 192 | 192 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-614-replacement-effects` | `keyword_mechanics` | 539 | 167 | 167 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-509-declare-blockers-step` | `keyword_mechanics` | 428 | 146 | 146 | `absent` | `untested` |
| `residual.effect_clause.deal-damage` | `one_shot_effects` | 1,007 | 115 | 115 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-111-tokens` | `keyword_mechanics` | 338 | 112 | 112 | `absent` | `untested` |
| `residual.effect_clause.return` | `one_shot_effects` | 740 | 111 | 111 | `absent` | `untested` |
| `residual.effect_clause.destroy-target` | `one_shot_effects` | 588 | 96 | 96 | `absent` | `untested` |
| `residual.effect_clause.exile` | `one_shot_effects` | 1,038 | 91 | 91 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-115-targets` | `keyword_mechanics` | 298 | 86 | 86 | `absent` | `untested` |
| `residual.activated_effect.deal-damage` | `one_shot_effects` | 479 | 83 | 83 | `absent` | `untested` |
| `residual.activated_effect.return` | `one_shot_effects` | 450 | 83 | 83 | `absent` | `untested` |
| `residual.activated_effect.tap-state` | `one_shot_effects` | 322 | 75 | 75 | `absent` | `untested` |
| `residual.effect_clause.tap-state` | `one_shot_effects` | 387 | 69 | 69 | `absent` | `untested` |
| `residual.effect_clause.look-reveal` | `one_shot_effects` | 574 | 60 | 60 | `absent` | `untested` |
| `residual.activated_effect.create-token` | `one_shot_effects` | 475 | 54 | 54 | `absent` | `untested` |
| `residual.effect_clause.create-token` | `one_shot_effects` | 723 | 43 | 43 | `absent` | `untested` |
| `residual.effect_clause.draw` | `one_shot_effects` | 599 | 43 | 43 | `absent` | `untested` |
| `residual.activated_effect.put-counter` | `one_shot_effects` | 356 | 42 | 42 | `absent` | `untested` |
| `residual.effect_clause.sacrifice` | `one_shot_effects` | 387 | 41 | 41 | `absent` | `untested` |
| `residual.activated_effect.destroy-target` | `one_shot_effects` | 151 | 41 | 41 | `absent` | `untested` |
| `residual.mechanic_dependency.scry` | `keyword_mechanics` | 107 | 40 | 40 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-508-declare-attackers-step` | `keyword_mechanics` | 135 | 39 | 39 | `absent` | `untested` |
| `residual.effect_clause.put-counter` | `one_shot_effects` | 335 | 38 | 38 | `absent` | `untested` |
| `residual.keyword_dependency.morph` | `keyword_mechanics` | 141 | 31 | 31 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-119-life` | `keyword_mechanics` | 76 | 30 | 30 | `absent` | `untested` |
| `residual.activated_effect.draw` | `one_shot_effects` | 412 | 29 | 29 | `absent` | `untested` |
| `residual.activated_effect.exile` | `one_shot_effects` | 386 | 28 | 28 | `absent` | `untested` |

## Boundary

Inventory and classification are not implementation or trust. Universal systems remain conservatively below snapshot-complete until all required rules, pieces, rulings, and interactions close.
