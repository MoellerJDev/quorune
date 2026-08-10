---
title: "Counter-placement transaction"
status: "current"
authoritative_source: "quorune/counter_placement.py, quorune/counter_state.py, quorune/counter_placement_sets.py, quorune/counter_placement_targets.py, quorune/token_creation.py, quorune/keyword_counters.py, quorune/attachment_references.py, quorune/entry_counter_model.py, quorune/entry_counters.py, quorune/saga_progression.py, quorune/death_return.py, quorune/unleash.py, quorune/mentor.py, quorune/relative_power_target.py, quorune/target_predicates.py, quorune/compiler/fixed_target_effect_sequences.py, semantic_runtime/counter_replacements.py, semantic_runtime/token_replacements.py, semantic_runtime/zone_replacements.py, semantic_runtime/self_entry_counters.py, semantic_runtime/block_restrictions.py, semantic_choices/death_return.py, ADR 0011, ADR 0034, ADR 0036, ADR 0037, ADR 0038, and ADR 0039"
verified: "2026-08-09"
audience: "rules, semantics, replay, and architecture contributors"
maintenance: "hand-maintained"
---

# Counter-placement transaction

`counter_placement.py` is the focused authoritative owner for represented
effect-generated counters placed on players, battlefield permanents, and the
already modeled card-zone counter children. It separates the operation into
preparation and commit:

1. Resolve each subject and build immutable player- or object-affected
   `counter.place` events.
2. Discover active trusted runtime descriptors against the pre-mutation state.
3. Traverse simultaneous events in APNAP order and let the affected player or
   permanent's controller choose among represented applicable replacements.
4. Suspend through the ordinary seat-scoped replacement continuation when a
   real choice exists.
5. Commit only after every selection is complete, every player still exists,
   and every permanent is still the same object in the expected zone.

This order enforces the represented portions of CR 122.6, 614.1, 614.16,
616.1, 616.1f, and 616.1g without giving pure runtime components mutable state.
The choice projection contains labels and stable option IDs only; the event
payload, object identifier, replacement batch, and prior journal remain in the
authoritative continuation. Exact replay reconstructs and validates the path,
chooser, and selected effect.

`replacement.counter.quantity.v2` is the current bounded component. It applies
fixed positive integral multiplication or fixed nonnegative addition to a
represented placement on a player or battlefield permanent. Its closed
descriptor distinguishes effect-only wording from all-placement wording and
may restrict the placing player, affected player/permanent relation, counter
name, and a small validated set of effective card-type or subtype predicates.
`replacement.counter.quantity.v1` remains registered only for replay and
reviewed-pack compatibility; new compiler output uses v2.

The generic compiler lowers exact ordinary "an effect would put," "you would
put," and passive "would be put" quantity-replacement sentences. It rejects
fractional, halving, dynamic, optional, team, opponent, "another," and
Class-level-gated variants as material residuals. Doubling Season's
effect-only wording therefore does not change a positive loyalty-symbol cost,
while represented all-placement wording such as Doc Samson's does.

Zone-destination replacements use the closed
`CreateAffectedObjectCounter` operation to derive a typed child from the
parent zone event. The operation binds the affected physical object and the
already transformed destination at application time, so one immutable source
effect can serve every event in a simultaneous batch. The containing zone
event is exhausted before its child is considered. Every replacement choice
is complete before the move; the child counter commits only after the card
reaches its validated destination. A counter on a card outside the battlefield
is represented for ordering but remains outside the permanent-only quantity
component.

The Oracle compiler lowers the closed “an opponent's card from anywhere would
enter a graveyard; exile it with one named counter instead” family to this same
destination handler and nested counter operation. Different owners, origins,
object kinds, optional wording, counter-free moves, and alternate destinations
remain residual rather than being inferred at runtime.

## Ownership and dependencies

`counter_placement.py` depends on immutable replacement values and narrow host
protocols. It delegates the one atomic write plan to `counter_state.py`, which
owns poison, energy, arbitrary normalized player counters, and permanent
counter maps.
`counter_placement_sets.py` and `counter_placement_targets.py` are read-only
coordinators: they snapshot a represented public battlefield set or the
still-legal members of a submitted bounded target set, canonicalize it by
APNAP controller and logical object identity, and delegate the complete batch
to `counter_placement.py`. Neither module owns authoritative state mutation.
`semantic_runtime/counter_replacements.py` validates source descriptors and
returns immutable effects; architecture policy prohibits it from importing the
engine, `GameState`, transport, persistence, or projection code. Positive
loyalty-symbol costs enter this same transaction through the typed activation
commit owner with `effect_generated=false`. A stable private cost-event ID and
strict priority-action continuation allow competing replacements to suspend
before any cost or stack mutation and resume with exact replay. Client commands
cannot supply those internal continuation fields.

The engine retains compatibility facades and supplies the host protocol. New
positive fixed counter operations must enter the transaction instead of adding
another direct engine write. Counter removal, effects that prohibit placement,
combined or modified loyalty-symbol costs, and other unrepresented rule actions
remain distinct and fail closed until their ordering semantics are modeled.

One closed target-threaded sequence may now place a fixed counter and then
grant Flying, First strike, Trample, or Vigilance for that target's current
battlefield incarnation. Counter placement still owns replacement suspension
and mutation;
the separate continuous-effect owner commits the later layer-6 result in
printed order. A failed later result rolls the entire resolution transaction
back. Optional, variable, compound, chosen, multi-target, and arbitrary granted
ability text remain residuals.

## Current producer inventory

The shared transaction currently owns the typed `place_counters` operation,
legacy-compatible positive `add_counter_selected`, positive generic `counter`,
`counter_all_subtype`, direct transaction calls, typed nested zone-replacement
counters, ordinary positive-integral Fabricate choices, the conditional +1/+1
counter from one permanent exploring once, and ordinary single-instruction
Proliferate over players and permanents. These paths prepare before mutation
and can safely suspend.

Intrinsic Planeswalker loyalty and Battle defense now use the same boundary.
The card-form compiler reads the canonical parsed type set and printed integral
characteristic once, emits a type-line-spanned CardProgram declaration, and
requires `counter.producer.intrinsic_entry`. Entry preparation lowers that
declaration to a mandatory self-replacement on the containing zone event; its
typed nested counter event follows any later destination replacement before
the ordinary affected-controller quantity-replacement ordering. A resolving
permanent can suspend through `resolving_entry` and resume without replaying
earlier spell effects. Simultaneous entries prepare in APNAP order without
mutation.

Planeswalker and Battle tokens reserve immutable prospective refs, physical
object IDs, logical identities, and a shared entry timestamp before mutation.
The token owner first exhausts represented additional-token replacements, then
prepares one simultaneous intrinsic-counter batch against those prospective
objects. A later quantity-replacement choice suspends through the same strict
selection journal. Commit allocates the exact reserved identities, creates the
tokens, and applies the prepared counters; the former replacement-free token
counter bypass has been removed.

Ordinary non-Read-Ahead Saga lore uses two deliberately distinct typed paths.
The card-form compiler emits `counter.producer.saga_lore` from the parsed Saga
subtype and treats the exact CR reminder line as provenance rather than a
runtime parser. The entry lore counter is a mandatory self-replacement inside
the zone-change tree, so represented effect-qualified quantity replacements
apply before the permanent enters and crossed trusted chapter events are
discovered afterward. At the active player's precombat main boundary,
`saga_progression.py` snapshots every controlled Saga with trusted typed
chapter declarations, commits all +1 lore changes through `counter_state.py`
before dispatching any chapter, and contributes the resulting triggers to the
same waiting-trigger batch as other beginning-of-phase triggers. That later
placement is a turn-based action, not an effect, so CR 614.16 excludes effects
such as Doubling Season. The separate `state_based.saga_final_chapter`
capability snapshots the exact Saga incarnation, waits while one of its typed
chapter abilities is pending, and then routes the ordinary final-chapter
sacrifice through the simultaneous state-based zone-change transaction.
Read Ahead, untrusted chapter programs, arbitrary lore-counter movement, and
copied, gained, removed, or layer-modified chapter abilities remain
fail-closed.

Effect-generated entry counters use the same nested replacement tree through
an immutable `EffectEntryCounter`. The instruction pins the physical card's
expected zone-change counter, prospective battlefield controller, placing
player, source, counter name, amount, and rule identity. Semantic preparation
completes every represented destination and counter-quantity replacement
choice before committing the move. A missing card, stale incarnation,
inactive placing player, non-battlefield destination, or malformed counter
fails or safely makes an explicitly optional return do nothing before state
mutation.

Printed Persist and Undying harvest that generic boundary. The compiler emits
one source-spanned triggered CardProgram per
printed keyword instance. Trigger discovery evaluates the relevant counter
from the departed creature's last-known public snapshot, preserves the
graveyard incarnation and trigger controller, and places simultaneous triggers
in the existing APNAP batch. Resolution returns only that same graveyard
incarnation under its owner, then applies the required -1/-1 or +1/+1 counter
through the effect-entry transaction. Control changes, duplicated keyword
instances, destination and quantity replacements, tokens, private projection,
and replay therefore share existing owners rather than keyword-specific state
writes. Granted or copied instances outside trusted typed ability fragments,
Oracle-equivalent prose, and unrepresented replacement families remain
explicit residuals.

Ordinary printed Unleash now adds a separate optional self-entry producer.
Oracle IR emits two independent typed programs from the same exact keyword
span: an all-zone affected-object entry replacement that offers one additional
+1/+1 counter,
and a battlefield block prohibition that reads the permanent's current public
counter snapshot. Each printed instance creates its own apply-or-decline
replacement, the prospective controller chooses before entry mutation, and an
accepted counter enters the same nested quantity-replacement tree described
above. The final counter state feeds the shared block-legality adapter used by
both projected options and accepted commands. Nonkeyword equivalents and
granted, copied, lost, or face-down Unleash outside typed ability propagation
remain explicit residuals; this slice does not broaden aggregate replacement
or blocking claims.

Ordinary printed Riot uses a separate linked entry-choice capability. Each
printed instance creates one optional affected-object replacement: applying it
creates a nested replacement-aware +1/+1 counter event, while declining it
creates an identity-pinned layer 6 Haste grant for that battlefield
incarnation. Both paths are selected by the prospective controller before the
zone mutation commits. The Haste result persists through cleanup, ends when
the object leaves the battlefield, and is consumed by the existing attack and
tap-or-untap-cost legality owners. Multiple Riot instances remain independent.
Nonkeyword equivalents, alternative results other than Haste, and granted,
copied, lost, or face-down Riot outside typed ability propagation remain
explicit residuals; aggregate entry replacement and continuous-effect claims
remain bounded.

Ordinary printed Mentor uses the same counter transaction without acquiring a
keyword-specific mutation path. The compiler emits one source-spanned typed
ability fragment per printed Mentor instance. A completed attack declaration
captures the source's effective power, creates independently identified
targeted triggers in the shared APNAP batch, and offers only current attacking
creatures with strictly lesser power. Resolution revalidates both creatures and their current effective
powers. If the Mentor source left before resolution, a typed departure snapshot
provides its immediate predeparture power while preserving the original logical
source identity; simultaneous departures capture every referenced source before
any move commits. A source that is currently, or immediately before departure,
a noncreature permanent has no power under CR 208.3; its printed power cannot
make the target legal. The result is one +1/+1 counter placed through the
canonical replacement-aware transaction. CR 702.134c's separate “mentors another
creature” event, granted or copied Mentor outside typed ability propagation,
prose equivalents, attackers put onto the battlefield outside declaration,
source phasing without a typed phase-out snapshot, unsupported characteristic
families, and trigger-doubling policies remain explicit residuals.

Oracle IR v54 lowers the closed reusable fixed-placement grammars through the
typed operation in spell, triggered, and activated contexts. It accepts one
positive exact quantity of one named counter on the source, the exact named
source, or one direct battlefield permanent target. Direct targets may use one
permanent card type or one pinned creature subtype, a fixed controller
relation, and source exclusion. The strict runtime handler lowers only to
`PlaceCountersIntent`; it neither parses Oracle text nor mutates state.

Oracle IR v64 adds one closed target-threaded sequence grammar for two or three
mandatory sentences that share direct creature target zero. Exactly one
sentence establishes the target; later clauses may refer to it only as “it.”
The represented sequence must contain one fixed counter placement and at least
one fixed power/toughness change or ordinary keyword grant until end of turn.
The compiler preserves printed operation order, emits one source-spanned
CardProgram node, and declares the counter, targeting, continuous-effect, and
individual keyword-mechanic dependencies actually used. Optional, modal,
conditional, variable, repeated, multiple-target, protection-choice, search,
scry, naming, and animation variants remain material residuals.

Ordinary CR 122.1b keyword counters now feed layer 6 through the typed
`keyword_counters.py` vocabulary. A positive represented counter grants its
named ability; removing the final counter removes that contribution. The
counter owner validates exact nonnegative quantities and has no Oracle-text or
card-name path. This characteristic projection does not by itself certify the
runtime behavior of every keyword: CardProgram closure still requires the
specific Flying, Haste, Trample, Hexproof, Indestructible, or other mechanic
capability. Parameterized keyword variants and same-layer dependency cases
outside the current continuous-effect model fail closed.

Oracle IR v65 lowers one mandatory instruction that places two or three
distinct fixed counter kinds on the source permanent or one direct permanent
target. The compiler preserves printed counter order and emits one
`PlaceCounterBatchIntent`; the runtime resolves the shared recipient once and
submits every placement as one simultaneous request sequence to the canonical
counter transaction. Replacement ordering therefore completes for the whole
instruction before any counter changes. Keyword counters additionally require
their typed layer 6 characteristic capability and the independent runtime
capability for the granted keyword. Optional, variable, repeated, duplicate,
distributed, multi-subject, player, entry, and affected-set variants remain
material residuals.

The attachment-relative fixed-placement family adds one typed semantic
reference for the object a source enchants, equips, or fortifies. The compiler
requires the exact parsed Aura, Equipment, or Fortification source subtype and
one closed permanent-type recipient; mismatched or dynamic qualities remain
residuals. Activation commit captures the reciprocal source/target identity
before costs, and trigger discovery captures it before enqueueing. Resolution
uses the live relation while the same source incarnation remains or the pinned
last-known relation after it leaves, then rejects a phased, wrong-type, or new
target incarnation before the existing counter intent is created. The
read-only identity resolver adds no state mutation or runtime Oracle parser.

The affected-set family lowers one mandatory fixed quantity onto every member
of one closed public battlefield set. Its predicates are serialized in an
immutable `AffectedPermanentSetSpec`; resolution snapshots the entire set
before the canonical simultaneous counter transaction begins. The bounded
target-set family separately lowers “each of up to N target” instructions for
direct permanent types, optional controller relations, and the represented
noncreature-artifact predicate. The selected refs remain distinct and bounded,
zero is legal for “up to,” and resolution follows CR 608.2b: still-legal
targets receive counters, while an originally nonempty selection with no legal
targets does not resolve. Both families use typed semantic intents and exact
replacement continuations rather than runtime Oracle interpretation.

The fixed positive Support N family reuses that target-set path. The compiler
derives source context from the exact parsed card-type set: a permanent source
adds the CR 701.41a “other” source exclusion, while an instant or sorcery
source does not. Unrelated or ambiguous source types remain residual. Support
then resolves as one +1/+1 counter on each surviving creature target through
the existing APNAP-canonical, quantity-replacement-aware transaction; it adds
no runtime Oracle parser, Support-specific mutation, or card identity branch.

The same compiler boundary now lowers one mandatory fixed player-counter
instruction in spell, triggered, and activated contexts. Its closed relations
are the controller, one direct active-player target, each active player, and
each active opponent. Energy and ticket symbols lower to their canonical
counter names; ordinary named poison, rad, energy, ticket, and experience
counters use the same typed `PlacePlayerCountersIntent`. Simultaneous subjects
are APNAP-canonical, direct targets are revalidated immediately before commit,
and every write remains owned by `counter_state.py`. Variable quantities,
linked subjects, multiple player-counter kinds, and player-counter quantity
replacement or prevention wording remain residual and fail closed.

The bounded Proliferate family compiles an unmodified `Proliferate.` clause in
spell, triggered, and activated contexts to CardProgram V2. The resolving
controller chooses any number of eligible public subjects. The continuation
pins physical and logical permanent identity plus every positive counter kind;
one additional counter of each kind then enters one simultaneous
replacement-aware batch. The transaction permits an empty selection and
rejects a changed subject or counter-kind snapshot before any counter changes.
Two-Headed Giant shared poison totals, repeated or variable Proliferate,
Proliferate replacement effects, and broader granted/copy propagation remain
explicitly unsupported.

The bounded Explore family compiles source/self and “target creature you
control” instructions to CardProgram V2. It publicly reveals the current
controller's top card, uses a replacement-aware zone move for a revealed land
or chosen nonland, places the counter only on the same current phased-in
logical incarnation, and emits one typed completion event. Its preparation
continuation pins the exact counter or zone intent, so a replacement choice
cannot repeat the prior reveal. Controller last-known information is captured
when the source leaves the battlefield. Simultaneous multi-permanent Explore,
repeated Explore, Explore replacement effects, and broader granted/copy
propagation remain explicit residuals.

One printed fixed positive ordinary mana cumulative-upkeep instance now uses a
two-stage semantic continuation. The first stage places its age counter through
the same replacement-aware transaction and can suspend for affected-object
ordering. Only after that commit does the second stage read the permanent's
actual age-counter count, calculate the payment, and issue the controller's
payment-or-sacrifice choice. This prevents quantity replacement from changing
the counter result without changing the cost. Resolution rechecks the pinned
source incarnation for the keyword's intervening battlefield condition. A
departed or returned new object makes the ability do nothing; a control change
leaves the original trigger controller responsible for the payment and permits
sacrifice only while that player still controls the permanent. Alternative,
snow, hybrid, Phyrexian, zero, variable, nonmana, copied, granted, and
multiple-instance forms remain precise residuals.

The compiler also owns one bounded mandatory casting-cost family: “As an
additional cost to cast this spell, put [fixed number] [counter kind]
counter(s) on a creature you control,” followed by exactly one represented
instant or sorcery result clause. The entire two-clause spell lowers to one
source-spanned CardProgram node with an immutable cost descriptor. Cast offers
query current effective creature characteristics and expose only the caster's
public, phased-in candidates. Commit revalidates that same predicate, marks the
placement as a cost rather than an effect, and routes it through the canonical
counter replacement transaction before stack placement. A replacement-order
choice suspends and resumes the complete cast atomically; mana, counters, and
stack state remain unchanged while the choice is pending. Unsupported cost
grammar blocks the whole spell so a following result clause cannot be compiled
as a cost-free action.

The following producers and wordings remain deliberately outside this slice:

- Read Ahead, nonordinary Saga progression, and stun-counter removal;
- negative loyalty counter-removal costs and damage-counter removal;
- optional, variable, alternate, compound, multiple, noncreature, and
  non-counter casting costs outside the bounded fixed creature-counter family;
- cumulative-upkeep forms outside the fixed positive ordinary mana family;
- Support X or zero and conditional, optional, repeated, copied, granted,
  modal, or compound Support instructions, plus variable, distributed, dynamic,
  subtype-qualified, combat-qualified, modal, conditional, compound, and
  multiple-counter target-set clauses, plus fixed player-counter variants
  outside the closed relations;
- conditional targets and non-creature subtype predicates;
- attachment-relative players, cards outside the battlefield, dynamic or
  compound attached-object predicates, and attachment creation or movement;
- Fabricate counter choices now suspend and resume through the typed semantic-completion continuation, while zero, variable, copied, and granted Fabricate variants remain explicit compiler residuals;
- optional, variable, state-derived, copied, face-down, or dynamically
  characteristic-modified Planeswalker and Battle token entry remains outside
  the represented prospective-token boundary;
- unsupported Battle subtype protector procedures and unrepresented
  copy-layer, face-down, or dynamic entry-characteristic interactions;
- counter removal and movement, state-based removals, and card-specific
  continuation paths such as Demonic Junker.

Several of those operations occur inside a larger semantic continuation after
earlier instructions have already mutated state. Routing them through a choice
that can suspend would replay prior side effects unless the enclosing
instruction first gains a typed resumable frame. They are recorded blockers,
not silently approximated migrations.

The component also excludes fractional or halving replacements, dynamic
quantities, counter movement, prevention, other enters-with-counter wordings,
and universal placing-player derivation. Broad CR 122/614/616 stays blocked
until those families and producers are integrated.

Primary assurance is in `test_counter_placement_replacements.py`,
`test_proliferate_rules.py`, `test_proliferate_compiler.py`, and
`test_fixed_counter_placement_effects.py`, with affected- and target-set
coverage in `test_fixed_counter_placement_sets.py` and
`test_fixed_counter_placement_target_sets.py`, plus intrinsic entry coverage
in `test_intrinsic_entry_counters.py`, Support coverage in
`test_support_counter_placement.py`, attachment-relative result coverage in
`test_attached_counter_placement.py`, shared event-order coverage in
`test_replacement_event_tree.py`, and focused mutation evidence in
`test_capability_implementation_mutations.py`. Mentor compiler, targeting,
last-known-information, replacement, rollback, multiplayer, and exact-replay
evidence is isolated in `test_mentor_rules.py`. Target-threaded counter and
characteristic sequences, strict residuals, replacement suspension, rollback,
four-player privacy, exact replay, keyword-counter projection, and focused
mutation evidence are isolated in `test_fixed_target_effect_sequences.py`.

Current aggregate corpus counts and remaining blockers are generated in
[`docs/COMPILER_COVERAGE_STATUS.md`](../COMPILER_COVERAGE_STATUS.md). They
measure represented behavior against the pinned corpus, not matchup results or
complete Oracle correctness.
