---
title: "Target legality and protection"
status: "current"
authoritative_source: "quorune/targets.py, quorune/target_predicates.py, quorune/target_protection.py, quorune/target_protection_engine_adapter.py, and CommanderEngine._target_row_matches"
verified: "2026-08-16"
audience: "rules, compiler, replay, and architecture contributors"
maintenance: "hand-maintained"
---

# Target legality and protection

Quorune uses one server-side target predicate for offer generation, submitted
command validation, and resolution-time revalidation. A client receives only
the legal public references in its current action schema and cannot substitute
an authoritative object identifier or bypass the same predicate at commit.

`targets.py` owns the closed schema vocabulary and public-zone boundary.
`target_predicates.py` owns reusable characteristic and relationship tests.
`CommanderEngine._target_row_matches` remains the orchestration facade over
current projected rows and the complete predicate. The narrow
`target_protection_engine_adapter.py` compatibility query materializes the
immutable `TargetProtectionSnapshot`; the pure
`target_protection_verdict` owner evaluates it.

Direct permanent schemas may also carry one typed public-state predicate.
`PermanentStatePredicateSpec` is shared with affected-set queries and evaluates
current tapped state, one named counter minimum, or positive current-turn
battlefield-entry history. Target offers, submitted commands, and CR 608.2b
revalidation all consume that same immutable descriptor. Effective type,
subtype, and color qualifiers remain in the characteristic snapshot, so the
represented type disjunctions, negative creature subtypes, nonblack, and
colorless creature forms respond to continuous characteristic changes without
parsing Oracle text at runtime. The same snapshot supplies one fixed exact,
minimum, or maximum mana-value qualifier. That qualifier observes represented
copy-derived characteristics and the public mana value of a face-down object;
it does not open power, toughness, variable, total, or combined public-state
numeric grammar. The compiler's `DirectPermanentTargetSpec` owner supplies
this one schema vocabulary to counter placement, destruction, exile, and tap
or untap effects; no effect family adds a private legality predicate.

## Typed protection boundary

The protection snapshot accepts already-derived current facts:

- acting spell or ability controller;
- protected player or permanent controller;
- current represented effective keyword set;
- source colors;
- represented player/controller color protections; and
- the existing typed Protection verdict.

It never reads or mutates `GameState`, parses Oracle text, chooses a target, or
discovers characteristics. It returns a closed allowed-or-blocked reason.
Malformed controller, keyword, color, boolean, and typed-verdict values fail
before legality is evaluated.

Ordinary permanent Hexproof is controller-relative: an opponent's spell or
ability cannot target the permanent, while its current controller may.
Ordinary permanent Shroud is controller-independent: no spell or ability may
target the permanent, including one controlled by that permanent's controller.
The same current-controller and effective-keyword calculation is repeated at
CR 608.2b resolution revalidation. Shroud, Hexproof, represented Protection,
player protection, and the existing temporary color-qualified
player/controller restriction remain cumulative in the same typed decision
boundary. Non-target selection and attachment legality deliberately bypass
targeting prohibitions and use their own rules owners.

## Compiler, capabilities, and reusable pieces

A source-spanned bare `Hexproof` or `Shroud` keyword lowers through CardProgram
V2 with the fine-grained `target.protection.hexproof_permanent` or
`target.protection.shroud_permanent` capability. Both capabilities depend on
`target.revalidate_resolution` and map to their corresponding capability and
mechanic reusable pieces plus `capability.target.revalidate_resolution` and
`mechanic.cr-115-targets`.

The compiler recognizes ordinary permanent Hexproof and Shroud
case-insensitively and composes them with sibling keyword nodes. It also lowers
the bounded temporary grant "target creature gains shroud until end of turn"
through the same typed characteristic and target-revalidation path. Player
Hexproof, player Shroud, Hexproof from a quality, targeting-exception effects,
multiple or each-quality variants, and rules-text equivalents remain precise
material residuals. Runtime code does not reinterpret those variants.

## Replay, privacy, rollback, and performance

Target schemas persist selected public references and logical identities; they
do not persist a separate Hexproof or Shroud journal. Replay rebuilds the same
current target predicate at offer, command, and resolution boundaries. An
injected illegal reference is rejected before mutation, so the authoritative
state hash is unchanged.

Only the acting principal receives its decision. Hexproof and Shroud use public
current battlefield characteristics and do not expose hidden-zone candidates
or another seat's decision. The pure verdict is constant in the number of game
objects; candidate enumeration remains owned by the surrounding target query.

Primary evidence is in `test_hexproof_targeting.py`,
`test_shroud_targeting.py`, `test_fixed_mana_value_target_predicates.py`,
`test_oracle_ir.py`, and
`test_capability_implementation_mutations.py`. Broader player Hexproof, player
Shroud, Hexproof-from-quality, effects that ignore either ability, hidden-zone
targets, and unsupported ability-changing, copying, face-down, or merged-object
keyword producers remain outside these trusted slices.
