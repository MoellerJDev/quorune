---
title: "ADR 0065: typed self-regeneration replacement"
status: "ADR"
authoritative_source: "typed regeneration compiler, semantic handler, and destruction transaction"
verified: "2026-08-13"
audience: "rules, compiler, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0065"
decision_status: "accepted"
date: "2026-08-13"
---

# ADR 0065: typed self-regeneration replacement

## Context

The generated cross-program selector identified `Regenerate this creature.` as
the highest-leverage dependency-ready activated-effect family. The compiler
left the instruction residual, and the destruction transaction explicitly did
not represent regeneration. Correct execution requires persistent one-turn
state, effect and state-based destruction replacement, tapping, damage removal,
combat removal, cleanup expiration, logical-object reset, public projection,
and replay to agree.

The broader mechanic also contains static regeneration, targeted and
noncreature-self grammar, prohibition effects, and affected-player ordering
between multiple applicable destruction replacements. Those families do not
share this exact compiler or choice boundary.

## Decision

The compiler lowers only the complete effect sentence `Regenerate this
creature.` to `{"op":"regenerate","card":"$source.zone_object"}`. Ordinary
activated-cost compilation remains independent. A strict semantic handler
uses the reviewed universal `regenerate` operation, requires the current source
incarnation, and emits one immutable typed shield-creation intent through its
version-1 handler. The operation remains reusable by later spell, trigger, and
delayed-effect compiler families, while this decision lowers only the exact
activated-ability grammar selected by the frontier.

`CardInstance.regeneration_shields` stores a public noncopiable count on the
logical object. Zero is omitted from Game Record v3. The regeneration owner
creates shields; cleanup and zone-object reset clear them. The existing
destruction transaction snapshots the count and adds a regeneration
disposition after Indestructible prohibition. Commit consumes one shield, taps
the surviving permanent through the canonical tap-state owner, removes marked
and Deathtouch damage through the damage-result owner, and calls the canonical
combat-relationship owner. Both effect destruction and damage-based state
actions use the same path.

When an effect destruction would have both a shield counter and regeneration
available, preparation fails before mutation. CR 616 affected-player ordering
must be represented by a separate typed continuation before that interaction
can execute. Static regeneration, cannot-be-regenerated effects, targeted,
qualified, modal, repeated, and compound wording remain material residuals.

## Alternatives

- Reparse regeneration reminder text at resolution. Rejected because reminder
  prose is not authoritative runtime data and would bypass CardProgram trust.
- Implement regeneration as a counter. Rejected because it is a generated
  replacement effect, not a counter, and zone and cleanup lifetime differ.
- Pick a fixed priority over shield counters. Rejected because the affected
  player owns a meaningful ordering choice.

## Consequences

- The selected exact self-activation family gains one capability-closed owner
  without widening other regeneration grammar.
- The regeneration mutation owner is classified in the rules layer, and the
  semantic executor delegates to it through the existing permanent-object
  intent family without adding a second replacement or activation engine.
- Existing destruction producers automatically receive the represented
  regeneration outcome and retain one preflight/commit transaction.
- Public projection and replay include positive shield counts while historical
  zero-state checkpoints remain byte-compatible.
- The aggregate Regenerate mechanic remains untrusted until its separate
  static, prohibition, targeting, and competing-choice families are closed.

## Removal condition

Retain the focused capability while its exact grammar, identity pinning,
destruction ordering, cleanup, projection, rollback, and replay tests pass.
Widening requires another typed grammar or replacement-choice owner rather than
special cases in this boundary.
