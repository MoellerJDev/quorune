---
title: "ADR 0075: typed fixed-mana Kicker entry"
status: "ADR"
authoritative_source: "typed Kicker compiler, casting-cost, stack-fact, entry-replacement, counter, and keyword owners"
verified: "2026-08-17"
audience: "rules, compiler, runtime, replay, privacy, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0075"
decision_status: "accepted"
date: "2026-08-17"
---

# ADR 0075: typed fixed-mana Kicker entry

## Context

Kicker is an optional additional cost paid while casting a spell. Whether it
was paid is a characteristic of that spell on the stack and may change its
resolution, entry replacement, or later trigger results. A cost-only compiler
would be incorrect if it advertised payment while the linked result remained
unrepresented. Reinterpreting `was kicked` prose during resolution or entry
would make current Oracle text behavior-authoritative.

The generated frontier contains 208 Commander cards blocked by Kicker. Their
result grammar is not one family: it includes multiple and/or Kicker costs,
variable costs, spell-result alternatives, cast and entry triggers, dynamic
quantities, and replacement effects. One coherent initial slice consists of a
single fixed ordinary-mana Kicker cost plus a mandatory enters-with result that
adds a fixed positive number of +1/+1 counters and optionally grants Flying,
First Strike, Haste, or Trample.

## Decision

Compile one source-spanned `Kicker {fixed ordinary mana}` line into a
`FixedManaKickerSpec`. Its all-zone runtime component supplies one optional
additional total-cost branch through the existing casting proposal. The branch
uses the same cost modification, mana-source, payment, offer, commit, rollback,
and replay owners as the base spell.

Runtime advertises the Kicker branch only when the compiler-pinned complete-
card admission certificate is exact. This allows the Kicker ability itself to
be counted as independently exact while withholding payment on cards whose
linked kicked result remains material residual behavior. Commit revalidates the
descriptor fingerprint before payment or stack mutation.

When the Kicker branch is selected, the casting owner records one typed paid-
Kicker fact on the current spell object. Zone replacement captures that fact in
its immutable subject snapshot. The stack-to-battlefield departure snapshot
also copies it into the normalized entry occurrence before CR 400.7 clears the
spell annotation. No later runtime path reads printed or reminder prose.

Compile the closed `If this creature was kicked, it enters with ...` line into
one `FixedKickedEntrySpec`. Its mandatory self-replacement creates a nested
counter-placement event and, when present, one affected-object keyword grant.
Counter quantity replacement resolves before commitment. The existing entry-
result owner commits counters and a zone-object layer-6 keyword effect only
after the complete replacement tree finishes.

## Alternatives

- Mark every Kicker line exact and always advertise payment. Rejected because
  paying an unsupported linked result would change authoritative behavior.
- Store the paid result only on the stack item. Rejected because entry
  replacement and normalized zone-trigger snapshots need the same immutable
  fact while the physical card changes zones.
- Add counters or keywords after entry. Rejected because enters-with wording is
  a replacement effect and counter-doubling effects must see its nested event.
- Compile all kicked triggers and spell riders in this branch. Rejected because
  their target, event, ordering, dynamic quantity, and linked-result grammars
  are separate harvest families.

## Consequences

- The bounded compiler probe produces 187 exact fixed Kicker cost abilities,
  27 exact kicked-entry replacements, and 20 complete Commander cards.
- Normal casting remains available without kicked counters or keywords. Partial
  cards expose no Kicker cost branch.
- Counter replacement, Haste attack/tap legality, Flying block legality, First
  Strike participation, Trample assignment, projection, and replay remain
  existing shared owners.
- Multiple, and/or, variable, hybrid, Phyrexian, snow, nonmana, copied, granted,
  modified, and text-changed Kicker costs remain residual. Kicked triggers,
  spell riders, ability fragments, keyword counters, dynamic quantities, and
  other entry results remain residual for subsequent coherent harvests.
- No Kicker-specific layer-6 ability-presence query or dynamic characteristic
  count is introduced; affected ability-changing and type-changing interactions
  remain outside trust.

## Removal condition

Retain this boundary while fixed Kicker payment, stack fact, entry replacement,
and linked result require one source-pinned transaction. A broader optional-
cost system may supersede it only if it preserves complete-card admission,
total-cost composition, immutable paid facts, nested replacement ordering,
incarnation reset, rollback, privacy, and exact replay.
