---
title: "ADR 0041: effect entry counters and identity-pinned death return"
status: "ADR"
authoritative_source: "this decision record and typed Persist/Undying implementation"
verified: "2026-08-08"
audience: "rules, compiler, replay, privacy, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0041"
decision_status: "accepted"
date: "2026-08-08"
---

# ADR 0041: effect entry counters and identity-pinned death return

## Context

Persist and Undying trigger from a battlefield-to-graveyard transition and may
return the same physical card with a counter. The counter is part of the return
effect, not an intrinsic characteristic of the entering card. A correct
implementation must use last-known battlefield information for the trigger,
reject a stale graveyard incarnation, return the card under its owner, and let
zone-change and counter-placement replacement effects modify the event before
authoritative mutation.

The existing intrinsic entry-counter boundary cannot represent an
effect-generated counter or its placing player. A post-entry counter write
would bypass the shared replacement tree and could not suspend, roll back, or
replay atomically with the zone change.

## Decision

Add an immutable `EffectEntryCounter` value and permit an identity-pinned
`ZoneMoveIntent` to carry a closed sequence of those values when its destination
is the battlefield. Snapshot preparation lowers each value to a mandatory
self-replacement on the containing `zone.change` event. That replacement
creates the canonical nested `counter.place` event, so ordinary APNAP ordering,
replacement choices, continuation serialization, mutation ownership, and exact
replay remain shared with every other represented counter producer.

Add one closed `death_return_with_counter` semantic operation. Printed Persist
and Undying keyword instances compile to source-spanned CardProgram V2 nodes.
Trigger discovery records the keyword, counter condition, controller, owner,
source ref, and last-known battlefield facts. At resolution the strict handler
revalidates that exact card incarnation in its owner's graveyard and emits the
typed zone-move intent; it receives no direct GameState mutation authority.

The zone-replacement facade delegates input validation, subject construction,
active-source collection, and effect composition to focused helpers. The public
snapshot function remains a narrow coordinator below the architecture size
threshold.

## Alternatives

- Put the counter on the returned permanent after movement. Rejected because it
  bypasses CR 614.16 replacement ordering and breaks atomic suspension.
- Reuse intrinsic entry counters. Rejected because the counter's source and
  placing player belong to the resolving effect, not the card form.
- Dispatch on card names or parse Oracle text at runtime. Rejected because the
  compiler and typed CardProgram are the pinned semantic authority.
- Let the trigger retain only an object ID. Rejected because zone changes create
  a new logical incarnation and stale objects must not return.

## Consequences

- Persist and Undying share one reusable death-return family while retaining
  separate counter conditions and fine-grained capability declarations.
- Multiple printed instances trigger independently; only the first resolving
  trigger can return the identity-pinned graveyard object.
- Control changes use the trigger controller for replacement ordering and the
  owner as the returning permanent's controller.
- Tokens and departed or replaced graveyard incarnations do not return.
- Counter quantity replacement and zone destination replacement complete before
  the move mutates authoritative state; replay and private continuations remain
  canonical.
- Granted, copied, removed, or nonkeyword versions and wider conditional return
  wording remain explicit residuals. Aggregate Persist, Undying, replacement,
  and zone-change rules are not declared complete.
- Game Record v3 and public protocol schemas remain unchanged.

## Removal condition

Replace this boundary only with a typed zone-change result transaction that
preserves last-known trigger facts, physical-card incarnation checks,
effect-source counter provenance, replacement ordering, transactional
continuations, seat-scoped projections, and exact replay.
