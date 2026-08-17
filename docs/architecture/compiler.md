---
title: "Oracle compiler architecture"
status: "current"
authoritative_source: "quorune/oracle_ir.py, quorune/compiler, and quorune/card_programs"
verified: "2026-08-17"
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

`compiler/life_templates.py` owns fixed life changes shared by spell and
activated contexts. In addition to controller gain/loss, it lowers one direct
player gain or loss, one opponent-only loss or equal drain, and one equal
each-opponent drain. Direct targets use the ordinary public player-target and
resolution-revalidation boundary; table-wide drains use one canonical life
batch. Dynamic amounts, target-player drains that could affect the controller,
each-player loss, life-total setting, exchanges, and unequal drains remain
source-spanned residuals.

`compiler/mill_templates.py` owns one mandatory positive fixed-count Mill
instruction for the controller, one target player, or one target opponent.
The same grammar is consumed by spell, triggered, and activated contexts and
feeds one immutable current-library-top plan into the canonical simultaneous
zone-transition owner. A short library mills as many cards as possible;
destination replacements, actual public results, target revalidation, APNAP
zone triggers, rollback, privacy, and replay remain shared. Optional and cost
Mill, dynamic or half-library quantities, player groups, linked
cards-milled-this-way consumers, and graveyard-order-sensitive interactions
while CR 404.3 is blocked remain source-spanned residuals or explicit trust
exclusions.

`compiler/fixed_effect_clause_sequences.py` owns the general closed
two-sentence composition boundary. It accepts exactly two top-level,
period-separated, mandatory clauses when each clause independently lowers to
one effect through an existing reviewed atomic owner and the pair contains at
most one direct target schema. The composed node preserves printed order and
the exact union of both component capabilities across spell, triggered, and
activated contexts. Optional, modal, conditional, linked-result, pronoun,
variable, repeated, multi-target, quoted-boundary, parenthetical-boundary, and
larger sequences remain source-spanned residuals.

`compiler/cumulative_upkeep_nodes.py` owns the closed printed
cumulative-upkeep grammar. It lowers one fixed positive ordinary-mana cost or
one em-dash-delimited fixed positive life cost to a source-spanned upkeep
trigger. Both forms place the age counter before calculating the optional
payment and require the shared replacement-aware counter owner; unsupported
costs and additional cumulative-upkeep instances remain material residuals.

`compiler/spell_additional_cost_templates.py` owns one closed binary
additional-cost expression. Each side must independently lower to a positive
fixed ordinary-mana payment, a positive fixed-life payment, or one existing
single-object discard, sacrifice, exile, or return payment. The casting owner
publishes one distinct cost-option identity per currently payable branch,
requires the pilot to select that identity when more than one branch is
available, folds a selected mana leaf into the total cost before reductions
and payment mechanics, and commits only the selected nonmana leaf. A spell is
excluded from its own discard candidates because this engine retains the card
in its origin zone until cost commit. Optional, three-or-more-branch,
variable, random, repeatable, composite, reveal, tap, linked-result, and named
mechanic costs remain source-spanned residuals. Direct mandatory positive
fixed-life costs use the same life-payment leaf and canonical life owner.

`compiler/keyword_nodes.py` owns one closed ordinary fixed-mana Morph
production. It lowers the turn-up cost to a typed all-zone runtime component;
the casting proposal owner separately supplies the face-down `{3}` creature-
spell alternative, suppresses printed costs and abilities, and retains
external cost modifiers that apply to the represented face-down spell. The
same descriptor later authorizes a controller-only no-stack turn-face-up
action through the current effective-keyword boundary. Megamorph, variable,
hybrid, Phyrexian, snow, nonmana, copied, granted, text-changed, multiface,
merged, and residual turn-up families remain source-spanned residuals or
fail-closed runtime exclusions.

`compiler/cascade_nodes.py` owns ordinary printed Cascade as one independently
source-spanned stack-zone trigger per instance. The casting transaction
materializes those descriptors into the ordinary APNAP trigger batch and
captures the selected spell face's mana value, including announced X. The
runtime coordinator publicly exiles to the first lower-mana-value nonland,
then delegates the optional cast to the generic one-shot exile-cast choice
owner. That owner revalidates the selected face, no-mana alternative,
additional costs, targets, and spell program before casting; the canonical
zone owner simultaneously returns every uncast card to the library bottom in
a deterministic random order. CR 702.85b action windows, replacement-choice
suspension during the sequential exile loop, and granted, copied,
text-changed, conditional, or face-down Cascade remain fail-closed.

`compiler/unearth_nodes.py` owns one closed ordinary fixed-mana Unearth
production. It lowers the graveyard-only sorcery-speed activation to a typed
fixed mana descriptor and one `unearth` semantic operation. The descriptor
requires a compiler-pinned complete-card admission certificate because
resolution materializes the card's other behavior on the battlefield. The
runtime coordinator delegates return, Haste, leave replacement, and delayed
trigger behavior to their existing typed owners. Variable and nonmana costs,
copied or granted instances, multiface cards, and cards with other material
residuals remain source-spanned residuals or fail-closed runtime exclusions.

`compiler/kicker_nodes.py` owns one single fixed ordinary-mana Kicker cost and
one closed kicked counter-plus-keyword entry replacement. The cost component
adds a server-authored optional total-cost branch only for a complete admitted
CardProgram. Its paid stack fact flows into immutable zone-replacement and
normalized entry snapshots. The entry component creates a nested replacement-
aware +1/+1 counter event and optionally grants Flying, First Strike, Haste, or
Trample through existing consumers. Multiple, and/or, variable, nonmana,
copied, granted, kicked-trigger, spell-rider, dynamic, and open entry families
remain source-spanned residuals.

`compiler/activated_mana_nodes.py` also owns three exact source-self zone-move
effects: graveyard to owner hand, graveyard to battlefield tapped, and a
battlefield Aura to owner hand. The typed descriptor replaces the parser's
default battlefield active zone with the represented origin and records the
destination, tapped state, source form, and complete-card policy. Only the
battlefield result requires the shared complete-card admission certificate;
the hand-return forms may remain independently executable on partial cards.
Untapped, targeted, mass, optional, conditional, multiple-object, copied,
granted, and text-changed movement stays source-spanned and residual.

The same activated-effect owner admits closed fixed characteristic results
through the existing resolution-created continuous-effect capability. It
lowers fixed numeric self power/toughness changes, fixed numeric
controller-creature affected sets, and the closed self keyword vocabulary to
the canonical duration journal and effective-characteristic query. Dynamic or
state-derived quantities, unsupported keywords, missing or alternate
durations, copy and face-down semantics, and player or game-rule effects remain
residual. This producer adds no family-specific ability-presence check and
performs no dynamic characteristic count.

`compiler/continuous_templates.py` owns the fixed-query keyword-grant grammar.
It accepts only live battlefield sets representable by `ObjectQuerySpec`: a
source-controller relation over closed type, pinned creature-subtype, color,
supertype, or token predicates, or an unqualified global type/subtype set. The
selected keyword set is Haste, Trample, Vigilance, First Strike, Double Strike,
and Flying; the prior controlled-artifact Hexproof sentence remains a narrow
compatibility form. Every emitted node declares both the layer-6 grant
capability and each keyword's existing combat or targeting consumer
capability. Opponent-relative, attacking or blocking, modified,
counter-qualified, multicolored, dynamic, conditional, temporary, chosen, and
other-keyword forms remain source-spanned residuals. Matching Class lines also
remain residual until level applicability has a typed owner. The grammar
performs no dynamic characteristic counts and does not claim ability-removal
composition.

`compiler/devoid_characteristics.py` owns the ordinary printed Devoid
production. One
exact keyword instance lowers to an all-zone
`ability.static.colorless-characteristic-definition.v1` fragment. Copy values
carry that fragment at layer 1; the characteristic evaluator then removes all
colors as a characteristic-defining effect in layer 5 before later non-CDA
color effects. Commander color identity remains a separate database-derived
format characteristic. Nonordinary wording, untyped granted Devoid,
text-changing producers, and face-down producers remain residual or outside
trust; the production performs no dynamic characteristic count.

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
represented type conjunctions and canonical disjunctions of up to four
permanent card types, pinned creature-subtype disjunctions, reviewed Vehicle
subtype, Flying predicate, controller relation, source exclusion, closed
negative subtype and color forms, and one shared typed public-state predicate
for tapped state, named-counter presence, or current-turn battlefield entry.
Arbitrary adjectives are never inferred as creature subtypes. Targeted
destruction delegates its whole-clause subject to this same owner, so spells,
triggers, and activations share the exact typed target grammar without a
destruction-specific predicate vocabulary. Mixed type/subtype disjunctions and
unrepresented qualifiers remain residual. The counter owner preserves two or
three printed fixed placements on one shared source or direct permanent target
as one typed batch node; runtime code receives the typed node and never
reparses Oracle text.

The same compiler owner lowers optional bounded permanent target sets from
both “up to N target” and “each of up to N target” wording. It emits one
zero-to-N target schema and one typed simultaneous placement instruction;
spell, triggered, and activated contexts share that production. The closed
tapped-creature form uses the same public-state predicate and resolution
revalidation as a single direct target. Variable limits, subtype or other
combat-state predicates, and compound instructions remain
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
and the shared replacement-aware source-zone cost transaction. Reinforce uses
ordinary priority timing; Level Up, Outlast, and Scavenge use sorcery timing.
Action offers and submitted commands consume that same compiler-pinned timing
field rather than applying mechanic-specific checks at either call site.
Scavenge lowers only a positive integral power printed on a single-face card.
Star power,
characteristic-defining or otherwise dynamic counts, and copy, face, text, or
type-changing interactions remain residual until a cycle-safe zone-
characteristic boundary owns them.

`compiler/token_templates.py` owns fixed-definition token creation across
spell, triggered, and activated effects. The closed production emits one
positive fixed quantity, an optional tapped entry state, and either a
represented Treasure, Food, or Map definition or a fixed creature definition
with at most two colors and capability-backed keywords. The corresponding
node capability shape validates every emitted field and adds the keyword or
predefined-token ability dependencies before promotion. Resolution uses the
existing `create_token` semantic operation and the replacement-aware
`token_creation.py` transaction. Dynamic quantities, copies, named or
legendary tokens, Roles, attached or attacking tokens, custom quoted
abilities, unrepresented predefined tokens, and compound or conditional
instructions remain source-spanned residuals.

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
two-word name. The same owner recognizes a closed compile-time vocabulary of
`this` permanent descriptors, including Aura, Equipment, Saga, Spacecraft, and
Vehicle. Those descriptors identify the physical source; they are not current
characteristic predicates, so type-changing effects do not retarget or cancel
an already represented result. The model never guesses an arbitrary prefix,
suffix, nickname, or subtype. Lowered instructions use `$source`; runtime
handlers do not receive names or reinterpret Oracle text. See
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
