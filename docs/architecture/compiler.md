---
title: "Oracle compiler architecture"
status: "current"
authoritative_source: "quorune/oracle_ir.py, quorune/compiler, and quorune/card_programs"
verified: "2026-08-14"
audience: "compiler and rules contributors"
maintenance: "hand-maintained"
---

# Oracle compiler architecture

The compiler transforms a pinned local card and rulings snapshot into typed
Oracle IR, recognized semantic nodes, dependency declarations, material
residuals, and a canonical `CardProgram`. For the same inputs and compiler
version, the result must be deterministic.

```mermaid
flowchart LR
    Input["Pinned card and rulings"] --> Normalize["Normalize faces and text"]
    Normalize --> Parse["Parse typed spans"]
    Parse --> Lower["Lower exact constructs"]
    Parse --> Residuals["Classify residuals"]
    Lower --> Gate["Bind trust and dependencies"]
    Residuals --> Gate
    Gate --> Program["Canonical CardProgram"]
```

## Stage ownership

`oracle_ir.py` owns parsing and IR compatibility.
`compiler/program_generation.py` owns lowering exact nodes into registry
programs. `card_programs/adapters.py` combines abilities, face identity,
source hashes, residuals, and capability closure into the canonical artifact.
The local card database is a compiler input; the engine does not query it while
performing a transition.

`compiler/fixed_target_effect_sequences.py` owns the closed cross-sentence
target-threading grammar. It is the only compiler authority for represented
fixed counter plus until-end-of-turn characteristic sequences: one clause
establishes target zero through one closed `DirectPermanentTargetSpec`, later
clauses use the exact pronoun “it,” and printed operation order is retained.
The runtime consumes only the resulting typed node and never reparses those
Oracle sentences.

`compiler/fixed_source_effect_sequences.py` owns the separate source-threaded
two-clause grammar. It accepts one fixed positive counter placement on a
permanent source followed by one represented fixed characteristic result until
end of turn. Both instructions lower to `$source.zone_object`; runtime
resolution validates the same physical and logical battlefield incarnation
before counter replacement and again when a suspended continuation resumes.
This production contains no card names or mechanic-specific runtime behavior.

`compiler/fixed_counter_controller_effect_sequences.py` owns a third closed
two-clause grammar. It accepts exactly one fixed counter placement on the
current source zone object or one direct permanent target plus exactly one
fixed controller draw, life-change, or Scry instruction, in either printed
order. Each clause reuses its existing typed owner; the sequence adds only the
immutable ordering and continuation boundary. Optional, modal, conditional,
variable, linked, repeated, and larger instruction families remain residual.

`compiler/target_effect_corpus_assurance.py` independently reconstructs the
resolution body for every promoted standalone or sequenced fixed-target node,
then requires the source grammar, emitted effects, target relation, closed
capability shape, and declared capability closure to agree. The normal pinned
compiler census derives grammatical shapes and representative identities from
the complete corpus; it does not maintain a card list. Its synthetic contract
also covers every accepted keyword, spell/trigger/activation context,
two-/three-clause and target-/counter-first sequence, controller relation, and
closed characteristic predicate and source-exclusion dimension. Adjacent
optional, modal, variable, compound-result, repeated, and multi-target forms
must remain residual. The generated assurance lives in the Oracle coverage
reports and contains hashes and public identities rather than Oracle prose.

`compiler/counter_placement_templates.py` separately owns the closed
fixed counter-placement grammar. Direct targets lower once to
`DirectPermanentTargetSpec`, whose deterministic runtime schema supports the
represented type conjunctions and disjunctions, pinned creature-subtype
disjunctions, reviewed Vehicle subtype, Flying predicate, controller relation,
and source exclusion. Arbitrary adjectives are never inferred as creature
subtypes. The same owner preserves two or three printed fixed placements on
one shared source or direct permanent target as one typed batch node; runtime
code receives the typed node and never reparses Oracle text.

The same compiler owner lowers optional bounded permanent target sets from
both “up to N target” and “each of up to N target” wording. It emits one
zero-to-N target schema and one typed simultaneous placement instruction;
spell, triggered, and activated contexts share that production. Variable
limits, subtype or combat-state predicates, and compound instructions remain
source-spanned residuals.

`compiler/fixed_counter_trigger_nodes.py` composes that already typed effect
body with closed normalized-event bindings for represented beginnings of
steps; a land entering under the source controller's control; a noncreature or
instant-or-sorcery spell cast by the source controller; controller life gains,
card draws, and exact second draws; and public artifact, creature,
enchantment, or permanent entries plus creature deaths. The public zone-change
grammar lowers only closed controller, opponent, source-exclusion, and token
predicates. It consumes the normalized owner's current entry facts or
predeparture last-known facts and does not perform a characteristic query of
its own. The binding emits only an immutable event predicate and ordinary
triggered node; APNAP placement, target revalidation, replacement suspension,
and counter mutation stay with their existing owners. Cast-or-copy, opponent
or arbitrary casts, broader land-entry relations, subtype- or
characteristic-qualified zone changes, one-or-more aggregation, combined
events, intervening-if, optional, variable, linked, movement, removal, and
unrepresented compound bodies remain material. Spell-cast type predicates
explicitly exclude type-changing stack interactions until their
characteristic boundary is trusted.

`compiler/counter_keyword_activation_nodes.py` composes that counter owner
with one source-pinned activation family for fixed ordinary-mana Level Up,
Outlast, Reinforce, and Scavenge. Level Up and Outlast resolve the exact current
source zone object; Reinforce and Scavenge use one revalidated creature target
and the shared replacement-aware source-zone cost transaction. Scavenge lowers
only a positive integral power printed on a single-face card. Star power,
characteristic-defining or otherwise dynamic counts, and copy, face, text, or
type-changing interactions remain residual until a cycle-safe zone-
characteristic boundary owns them.

## Invariants

- Every lowered node retains its exact source provenance.
- Unknown or ambiguous grammar becomes a source-spanned residual, never
  guessed behavior.
- Instruction order, targets, modes, choices, and continuations remain
  explicit in the typed result.
- Parsing success is separate from runtime and rules closure.
- A reviewed ability can supersede generated output only at the same stable
  semantic key; conflicts fail closed.
- Compiler output cannot claim trust beyond all declared capabilities and
  runtime dependencies.
- Card names and Oracle IDs are evidence and lookup keys, not generic runtime
  behavior switches.

Activated-mana lowering has separate closed owners for fixed output and
current color-set output. The color-set grammar represents choosing one color
among qualifying legendary permanents or legendary creatures and
planeswalkers, choosing among owned legendary creature cards in a graveyard,
and adding one mana of each color among controlled permanents. Each form
lowers an immutable relative `ObjectQuerySpec`. Monocolored-only, linked-exile,
opponent-relative, additional-condition, restricted, and side-effecting
variants remain source-spanned residuals.

Printed `Affinity for artifacts` lowers as one source-spanned `cast.cost`
descriptor per printed instance. The selected-face runtime reads only those
typed descriptors and current effective artifact characteristics; other
Affinity parameters and equivalent rules text remain residual instead of
becoming runtime Oracle interpretation.

Printed `Sunburst` lowers as one source-spanned `zone.change` descriptor per
instance. The descriptor contains the counter kind derived from the printed
selected-face card types, never a runtime type query. Cast commit separately
records the distinct WUBRG colors actually spent; only a resolving cast card
with a nonempty payment fact can apply the descriptor. Parameterized or
qualified wording, Modular—Sunburst linked values, nonkeyword equivalents,
and ability propagation outside the typed fragment remain material residuals.

Two exact controller-wide static permissions lower to selected-face
`action.permission` descriptors: playing lands from the controller's own
graveyard and activating abilities of controlled creatures as though they had
haste. Runtime action and activation queries consume only those trusted typed
descriptors. Additional-land, any-graveyard, opponent-relative, conditional,
temporary, targeted, and ordinary haste wording remains source-spanned
residual material.

Printed Exhaust prefixes lower to a typed `ActivationLimit` on each distinct
ability. The exact reminder sentence is stripped once by the ability parser;
neither legality nor commit reparses it. Fixed-output and color-set mana
descriptors carry that limit, and each nonmana result still needs its own
ordinary effect and cost closure. Wording that permits another Exhaust use
remains a material residual.

The exact activated-effect sentence `Regenerate this creature.` lowers to one
`regenerate` instruction over `$source.zone_object`. Cost compilation remains
independent, so unsupported counter-removal, typed-sacrifice, snow, hybrid,
exile, or restricted activation costs stay residual even when the effect
sentence matches. Targeted, static, noncreature-self, repeated, qualified, and
cannot-be-regenerated grammar remains residual rather than widening this
self-activation family.

Fixed mass-damage lowering uses the same complete `ObjectQuerySpec` descriptor
consumed by the runtime affected-set snapshot. The compiler emits ordered
player/permanent groups and an optional exact target-opponent controller; it
does not encode card names or reparse Oracle text during resolution. Only the
closed positive predicates represented by the object-query vocabulary are
accepted. Negative keyword or subtype predicates, divided or variable damage,
multiple damage clauses, and linked result riders remain source-spanned
residuals until their own typed families exist.

Source-self wording uses one immutable `SourceReferenceSpec` across represented
counter, damage, prevention, trigger, entry, activation-cost, and declaration
grammar. It accepts the full Oracle name and bounded complete leading forms
before a comma, the title delimiters “the” or “of,” or a bounded ordinary
two-word name. It never guesses an arbitrary prefix, suffix, or nickname.
Lowered instructions use `$source`; runtime handlers do not receive names or
reinterpret Oracle text. See
[ADR 0040](../adr/0040-closed-source-self-references.md).

## Extending the compiler

Add the smallest reusable grammar production and typed construct. Include
source-pinned positive, negative, ambiguity, residual, canonical-JSON, and
runtime-lowering tests. Reuse an existing runtime primitive when its contract
matches exactly; otherwise leave the construct residual until the primitive
has its own owner and assurance. Regenerate the compiler and rules reports
through their owning commands rather than editing them by hand.

Schema changes and new stage ownership require an ADR. Current coverage and
blockers live in the generated
[compiler status](../COMPILER_COVERAGE_STATUS.md); stable IR fields and
provenance live in the [Oracle IR reference](../reference/oracle-ir.md).
See [ADR 0005](../adr/0005-card-program-v2.md),
[ADR 0006](../adr/0006-typed-semantic-handler-boundary.md), and
[ADR 0022](../adr/0022-reusable-rules-piece-inventory.md).
