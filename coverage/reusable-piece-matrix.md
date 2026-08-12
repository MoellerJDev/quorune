---
title: "Reusable rules piece matrix"
status: "generated"
authoritative_source: "coverage/reusable-piece-matrix.json.gz"
verified: "fbf892104a9ffbc568f7446d7990327af7329e94dd49d8756d1ebaaeae328198"
audience: "compiler and rules contributors"
maintenance: "generated"
---

# Reusable rules piece matrix

Current Oracle IR material ability and residual spans plus all registered capabilities, mechanics, handlers, components, and pinned rule references. This inventories current source relations without claiming universal runtime completion.

Counts official ruling presence by Oracle ID. Ruling prose is not yet behaviorally classified, so these counts are composition evidence rather than coverage claims.

## Snapshot

- Profile: `commander_review`
- Ontology: `reusable-pieces-v1`
- Pieces: 1,321
- Cards indexed: 31,623
- Material abilities classified: 59,601
- Unclassified material spans: 0
- Mapped pinned rules: 797 / 3,300
- Applicable piece pairs: 27,645
- Covered piece pairs: 448

## Ontology classes

| Class | Pieces |
|---|---:|
| `actions_permissions` — Actions, permissions, and prohibitions | 29 |
| `card_forms` — Card types and specialized forms | 4 |
| `choices_continuations` — Modes, targets, choices, and continuations | 9 |
| `combat` — Combat | 22 |
| `compiler_cardprogram` — Compiler and CardProgram pieces | 402 |
| `continuous_effects` — Static abilities and continuous effects | 22 |
| `costs_mana` — Costs and mana | 7 |
| `events_mutations` — Typed events and mutations | 99 |
| `keyword_mechanics` — Keyword actions and keyword abilities | 544 |
| `multiplayer_commander` — Multiplayer, Commander, and profile pieces | 1 |
| `object_identity` — Object identity and lifetime | 26 |
| `one_shot_effects` — One-shot semantic effects | 125 |
| `players_format` — Players, relationships, and format state | 1 |
| `proposals` — Casting and activation proposals | 10 |
| `quantities` — Quantity and value expressions | 1 |
| `references` — References | 1 |
| `replacement_prevention` — Replacement and prevention | 16 |
| `triggers` — Triggers | 2 |

## Universal systems

| System | Status | Pieces | Blocking pieces |
|---|---|---:|---:|
| `action_legality_casting_activation_costs_mana` | `inventoried` | 46 | 6 |
| `combat` | `compositional` | 22 | 0 |
| `derived_characteristics_static_layers` | `inventoried` | 22 | 5 |
| `generic_triggers_stack_placement` | `inventoried` | 2 | 2 |
| `multiplayer_player_leaving_commander` | `represented` | 2 | 0 |
| `objects_identity_zones_faces_copies` | `compositional` | 30 | 0 |
| `replacement_prevention` | `inventoried` | 16 | 3 |
| `state_turn_loops_stabilization` | `inventoried` | 0 | 0 |
| `targets_modes_searches_references_choices` | `inventoried` | 11 | 6 |
| `typed_transactions_events_mutations` | `inventoried` | 224 | 67 |

## Highest current blocker leverage

| Piece | Class | Residuals | Sole blockers | Expected cards | Runtime | Assurance |
|---|---|---:|---:|---:|---|---|
| `residual.continuous_layer.continuous-effect-layers-and-dependencies` | `continuous_effects` | 9,492 | 3,628 | 3,628 | `absent` | `untested` |
| `residual.activated_effect.unparsed-clause-grammar` | `one_shot_effects` | 2,525 | 718 | 718 | `absent` | `untested` |
| `residual.effect_clause.unparsed-clause-grammar` | `one_shot_effects` | 2,627 | 427 | 427 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-611-continuous-effects` | `keyword_mechanics` | 480 | 197 | 197 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-614-replacement-effects` | `keyword_mechanics` | 539 | 196 | 196 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-509-declare-blockers-step` | `keyword_mechanics` | 428 | 157 | 157 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-additional-cost-clause` | `one_shot_effects` | 123 | 122 | 122 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-111-tokens` | `keyword_mechanics` | 338 | 117 | 117 | `absent` | `untested` |
| `residual.effect_clause.deal-damage` | `one_shot_effects` | 956 | 112 | 112 | `absent` | `untested` |
| `residual.effect_clause.exile` | `one_shot_effects` | 988 | 102 | 102 | `absent` | `untested` |
| `residual.effect_clause.destroy-target` | `one_shot_effects` | 572 | 98 | 98 | `absent` | `untested` |
| `residual.effect_clause.return` | `one_shot_effects` | 686 | 96 | 96 | `absent` | `untested` |
| `residual.activated_effect.deal-damage` | `one_shot_effects` | 479 | 86 | 86 | `absent` | `untested` |
| `residual.activated_effect.tap-state` | `one_shot_effects` | 322 | 76 | 76 | `absent` | `untested` |
| `residual.effect_clause.tap-state` | `one_shot_effects` | 373 | 68 | 68 | `absent` | `untested` |
| `residual.effect_clause.typed-spell-result-clause` | `one_shot_effects` | 66 | 65 | 65 | `absent` | `untested` |
| `residual.activated_effect.return` | `one_shot_effects` | 418 | 64 | 64 | `absent` | `untested` |
| `residual.effect_clause.look-reveal` | `one_shot_effects` | 552 | 60 | 60 | `absent` | `untested` |
| `residual.activated_effect.create-token` | `one_shot_effects` | 474 | 55 | 55 | `absent` | `untested` |
| `residual.effect_clause.draw` | `one_shot_effects` | 577 | 48 | 48 | `absent` | `untested` |
| `residual.effect_clause.create-token` | `one_shot_effects` | 695 | 44 | 44 | `absent` | `untested` |
| `residual.activated_effect.destroy-target` | `one_shot_effects` | 151 | 42 | 42 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-508-declare-attackers-step` | `keyword_mechanics` | 135 | 39 | 39 | `absent` | `untested` |
| `residual.keyword_dependency.morph` | `keyword_mechanics` | 141 | 32 | 32 | `absent` | `untested` |
| `residual.activated_effect.draw` | `one_shot_effects` | 412 | 30 | 30 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-119-life` | `keyword_mechanics` | 76 | 30 | 30 | `absent` | `untested` |
| `residual.activated_effect.exile` | `one_shot_effects` | 386 | 28 | 28 | `absent` | `untested` |
| `residual.mechanic_dependency.cr-615-prevention-effects` | `keyword_mechanics` | 78 | 28 | 28 | `absent` | `untested` |
| `residual.effect_clause.counter` | `one_shot_effects` | 243 | 26 | 26 | `absent` | `untested` |
| `residual.activated_effect.put-counter` | `one_shot_effects` | 323 | 23 | 23 | `absent` | `untested` |

## Boundary

Inventory and classification are not implementation or trust. Universal systems remain conservatively below snapshot-complete until all required rules, pieces, rulings, and interactions close.
