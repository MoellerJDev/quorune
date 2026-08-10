---
title: "ADR 0046: typed fixed sacrifice casting costs"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-09"
audience: "rules, compiler, casting, replay, and architecture maintainers"
maintenance: "hand-maintained"
adr_id: "0046"
decision_status: "superseded"
date: "2026-08-09"
---

# ADR 0046: typed fixed sacrifice casting costs

> Superseded by [ADR 0049](0049-typed-fixed-zone-change-casting-costs.md),
> which retains this descriptor as a Game Record v3 compatibility shape while
> moving its execution into the shared fixed single-object zone-change owner.

## Context

A recurring instant-and-sorcery family requires its caster to sacrifice one
permanent as an additional cost. The supported wording may accept any
permanent, one canonical permanent card type, or either of two such types. A
runtime Oracle parser or card-named handler would create a second authority and
could advertise a spell without its mandatory cost. A direct battlefield write
would also bypass current characteristics, owner graveyards, destination
replacement, departure triggers, rollback, privacy, and replay.

## Decision

Compile exactly one mandatory fixed sacrifice sentence followed by one
independently represented spell-result clause into one source-spanned
CardProgram V2 node. The node owns a strict immutable versioned descriptor for
one phased-in permanent controlled by the caster. Its closed type union contains
zero, one, or two of artifact, battle, creature, enchantment, land, and
planeswalker. Unsupported qualifiers or cost structures residualize the whole
spell.

Offer generation and cast proposal validation consume the same effective-object
query. Commit revalidates that exact object, then uses the canonical
replacement-aware battlefield-departure owner within the unified cost-payment
transaction and before stack placement finishes. Competing destination
replacements suspend and roll back the whole proposed cast, expose a decision
only to the affected caster, and resume the pinned zone-change event and cast.
Historical unversioned sacrifice descriptors remain on the Game Record v3
compatibility path.

CR 701.21a is the keyword-action owner: the current controller chooses the
permanent, the unmodified destination is its owner's graveyard, and sacrifice
does not invoke destruction. Indestructible therefore does not prevent the
cost. Destination replacement remains applicable to the zone change.

## Alternatives

Runtime Oracle parsing was rejected because CardProgram is the semantic
authority. Treating the sentence as an ordinary sacrifice effect was rejected
because casting costs have different ordering, rollback, and continuation
requirements. Card-specific programs were rejected as the scaling model;
Diabolic Intent keeps only its still-uncompiled tutor result while its cost now
uses the same typed descriptor.

## Consequences

Village Rites-, Costly Plunder-, and equivalent represented spell families can
be promoted generically without card identity. Advertised and accepted choices
remain identical across current type and control changes. Sacrificing an
Indestructible permanent is legal, an opponent's permanent is not, and a
controlled permanent still moves toward its owner's graveyard. Exact replay
pins both ordinary payment and suspended destination-replacement order.

Optional, variable, repeated, multiple, alternate, qualified, subtype, color,
and composite costs remain residual. Sacrifice effects, activated costs,
rule-generated sacrifices, simultaneous multi-player sacrifice batches, and
keyword families such as Casualty or Forage are separate capabilities. This
decision does not complete CR 601, aggregate Sacrifice producers, replacement
effects, regeneration, or trigger grammar.
