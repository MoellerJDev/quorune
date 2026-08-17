---
title: "ADR 0076: typed self-zone-move activations"
status: "ADR"
authoritative_source: "typed activated-ability compiler, complete-card admission, semantic runtime, and canonical zone-transition owner"
verified: "2026-08-17"
audience: "rules, compiler, runtime, privacy, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0076"
decision_status: "accepted"
date: "2026-08-17"
---

# ADR 0076: typed self-zone-move activations

## Context

Several cards contain an activated ability whose resolving object is the source
itself. Three repeated forms account for one coherent broad compiler family:
returning the card from its owner's graveyard to hand, returning it from the
graveyard to the battlefield tapped, and returning a battlefield Aura to its
owner's hand. They share source-incarnation identity, ordinary activation and
stack timing, owner-zone routing, destination replacement, normalized zone
events, privacy projection, and replay.

The parser's default battlefield activation zone is wrong for both graveyard
forms. A runtime text comparison would correct the zone too late and make
Oracle prose behavior-authoritative. Treating tapped reanimation like the two
hand returns would also admit independently exact abilities on partial cards
whose unsupported permanent behavior could become authoritative immediately.

## Decision

Compile only these exact complete effect clauses:

- `Return this card from your graveyard to your hand.`
- `Return this card from your graveyard to the battlefield tapped.`
- `Return this Aura to its owner's hand.`

One source-spanned `SelfZoneMoveSpec` records the corrected active zone,
destination, tapped state, source form, and complete-card policy. The existing
activated-cost compiler must represent the complete cost. The ordinary
activation proposal and commit owners advertise, revalidate, pay, and place
the ability on the stack without reading Oracle text.

Resolution lowers the closed effect to one `SelfZoneMoveIntent` pinned to the
source's physical and logical incarnation. The coordinator verifies the same
card remains in the represented origin; the Aura form additionally verifies
the source's current effective subtype. It delegates all movement, owner-zone
routing, tapped entry, attachment cleanup, replacement selection, normalized
events, projection, and journaling to the canonical zone-transition owner.

Graveyard-to-battlefield resolution requires the shared source-pinned complete-
card admission certificate because it materializes current permanent behavior.
The two hand-return forms may execute on partial cards because they remove the
source from a public active or graveyard zone and do not expose its unsupported
hand behavior. This policy is descriptor-driven and is not tied to a family-
specific handler check.

## Alternatives

- Reinterpret the effect text during activation or resolution. Rejected because
  current Oracle prose must not be behavior authority.
- Build three independent runtime implementations. Rejected because source
  identity, activation, zone transition, replacement, privacy, and replay are
  the same ownership boundary.
- Admit tapped reanimation on every independently exact ability. Rejected
  because a partial returned permanent can immediately affect the game.
- Include untapped, targeted, mass, optional, conditional, or multiple-object
  movement. Rejected because those forms require different result grammar and
  interaction evidence.

## Consequences

- The database-backed compiler census produces 71 exact activated abilities and promotes
  33 complete Commander cards.
- Graveyard activation uses owner scope and the correct active zone. A
  countered or stale activation leaves the current card incarnation unchanged.
- Tapped entry, Aura attachment cleanup, owner hand routing, replacements,
  trigger discovery, projection, rollback, and replay remain shared owners.
- Untapped reanimation and open source, destination, quantity, condition,
  target, copy, grant, or text-change forms remain source-spanned residuals.
- No family-specific layer-6 ability-presence query or dynamic characteristic
  count is introduced.

## Removal condition

Retain this boundary while the three exact source-self forms share one closed
descriptor and canonical zone-transition transaction. A broader typed zone-
movement family may supersede it only if it preserves corrected active zones,
source incarnation, conditional complete-card admission, replacement ordering,
owner routing, attachment cleanup, privacy, rollback, mutation evidence, and
exact replay.
