---
title: "ADR 0055: typed direct counter-removal effects"
status: "ADR"
authoritative_source: "this decision record and the typed counter-removal owner"
verified: "2026-08-10"
audience: "rules, compiler, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0055"
decision_status: "accepted"
date: "2026-08-10"
---

# ADR 0055: typed direct counter-removal effects

## Context

Counter-removal costs and rule actions already used an exact typed transaction,
but ordinary spell, triggered, and activated effects had no shared compiler or
runtime boundary. Extending the legacy semantic switch would preserve a second
counter-state writer, encourage runtime Oracle interpretation, and make target
revalidation, rollback, and replay depend on effect context.

The represented Oracle corpus has two distinct direct effect families: remove a
fixed positive number of one named counter kind from one public battlefield
permanent, and remove every counter of every kind from one such permanent.
These are not interchangeable with exact counter-removal costs. An effect does
as much as possible, while a cost must remain exactly payable.

## Decision

Compile the closed direct-target grammar once into source-spanned CardProgram V2
nodes. Spell, trigger, and activated contexts share the same target predicate
and lower to one of two reviewed operations:

- `remove_counters` carries a fixed positive amount and one normalized counter
  name;
- `remove_all_counters` carries no counter-name or amount field and snapshots
  every positive canonical counter kind on the target.

Strict read-only handlers lower those descriptors to immutable typed intents.
The counter-removal owner pins the target's physical identity, current logical
identity, battlefield zone, and canonical before-state, then validates again
before committing through the canonical counter-state owner. Partial fixed
removal, exact cost and rule removal, and all-kind removal therefore remain
separate typed plans. Removing the final defense counter still delegates the
resulting Siege battle trigger to the existing trigger owner.

The direct permanent target grammar is shared with fixed counter placement. Its
capability shape lives in a focused rules module so the general CardProgram
shape registry does not become another oversized rules owner.

## Alternatives

- Reuse exact cost removal for effects. Rejected because effects remove as much
  as possible and costs require the full amount.
- Represent all-counter removal as a magic counter name or a very large amount.
  Rejected because both lose the canonical set of removed kinds and weaken
  replay validation.
- Parse Oracle text or dispatch on card identity at runtime. Rejected because
  compilation and runtime would become competing rules authorities.
- Add one general counter-mutation dictionary operation. Rejected because it
  would permit unreviewed player counters, movement, variable quantities, and
  arbitrary target forms through the same authority.

## Consequences

- CardProgram compiler version `oracle-ir-v76` can capability-close the two
  represented effect families across spell, triggered, and activated contexts.
- Authoritative counter maps reject booleans, strings, negative amounts, and
  other malformed values before mutation.
- Descriptor, result, and target shapes fail closed; callbacks and raw
  GameState access are not exposed to handlers.
- The operations concern public battlefield permanents, so no hidden-zone
  projection or additional private continuation is introduced.
- Game Record v3 and public protocol schemas remain unchanged. New games pin
  the source-spanned descriptor and canonical public counter journal, preserving
  exact replay and rollback.
- Player counters, source or nontarget clauses, named-kind all removal, up-to,
  optional, variable, distributed, repeated, linked, modal, compound, moving,
  and non-battlefield variants remain explicit residuals.

## Removal condition

Replace these operations only with a more general typed counter-result system
that preserves the distinction between partial effects and exact costs, the
all-kind snapshot, closed source-spanned grammar, target identity and
revalidation, counter-state strictness, Siege consequences, rollback, privacy,
exact replay, and fail-closed unsupported variants without runtime Oracle or
card-identity dispatch.
