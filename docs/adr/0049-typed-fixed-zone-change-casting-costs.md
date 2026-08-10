---
title: "ADR 0049: typed fixed single-object zone-change casting costs"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-10"
audience: "rules, compiler, casting, replay, and architecture maintainers"
maintenance: "hand-maintained"
adr_id: "0049"
decision_status: "accepted"
date: "2026-08-10"
---

# ADR 0049: typed fixed single-object zone-change casting costs

## Context

Many spells require one card or permanent to change zones as an additional
cost. Fixed discard, sacrifice, graveyard exile, battlefield exile, and
return-to-owner-hand sentences share casting order and rollback requirements,
but differ in who owns or controls the selected object, what information is
private, which destination applies, and which normalized zone facts follow.
Leaving those contracts in unrelated dictionaries would let offer and commit
legality diverge and would grow another string-switched payment path.

## Decision

Represent one mandatory single-object zone-change payment with an immutable,
versioned descriptor. A closed operation vocabulary derives the exact origin,
unmodified destination, and response field; callers cannot supply those facts
independently. The descriptor embeds one `ObjectQuerySpec` and permits only the
owner/controller relationship and characteristic dimensions reviewed for that
operation.

The compiler lowers fixed one-card discards; one creature or instant/sorcery
card exiled from the caster's graveyard; one artifact, creature, or permanent
the caster controls exiled from the battlefield; and one controlled land,
creature, or permanent returned to its owner's hand. The same descriptor also
widens single-permanent sacrifice predicates to pinned creature subtypes,
Legendary creatures, fixed colors, and nonland permanents. Ordinary zero-, one-,
or two-card-type sacrifice descriptors retain their serialized shape for Game
Record v3 compatibility but lower immediately to the same runtime value.

Offer and submitted-command validation share one immutable candidate query.
Commit revalidates that query, prepares the operation-owned zone change, and
uses the existing destination-replacement continuation before any cost or spell
mutation survives. A completed payment dispatches normalized discard,
graveyard-departure, or battlefield-departure facts before the cast event. The
zone owner routes a controlled object to its actual owner's hand or graveyard.
No runtime path parses Oracle text.

## Alternatives

- Keep separate discard, sacrifice, exile, and return dictionaries. Rejected
  because origin, destination, response shape, and revalidation would drift.
- Parse Oracle text during action generation or payment. Rejected because the
  source-spanned CardProgram must remain the sole semantic authority.
- Model these payments as ordinary resolving effects. Rejected because casting
  costs require atomic rollback, replacement suspension, privacy, and ordering
  before stack placement completes.
- Generalize immediately to arbitrary counts and alternatives. Rejected because
  simultaneous multi-object payments and player-selected cost order need a
  distinct typed batch and continuation design.

## Consequences

- Private hand and graveyard candidates are visible only in the caster's
  capability; opponents receive neither the refs nor the replacement
  continuation.
- Destination replacements, rollback, trigger batching, and exact replay are
  identical across represented operations, while each capability retains its
  exact CR and privacy evidence.
- The legacy unversioned discard/sacrifice candidate scan is isolated in the
  casting-cost module, and `CommanderEngine` no longer owns it.
- Fixed destination contracts do not encode result dependencies on the paid
  object's power, mana value, color, or later identity. Those spell-result
  clauses still need their own typed lowering.
- Random, variable/X, multiple, simultaneous, optional, alternative, reveal,
  tap, historical, dynamic, and keyword-named costs remain fail-closed
  residuals. This does not complete CR 601, 701.9, 701.13, or aggregate zone
  changes.

## Removal condition

Retire this descriptor only if a successor preserves its closed operation
vocabulary, immutable object predicate, shared offer/commit legality,
replacement-aware precommit boundary, normalized event ordering, owner routing,
private continuation, compatibility lowering, and exact replay identity.
