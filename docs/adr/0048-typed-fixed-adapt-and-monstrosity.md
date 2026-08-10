---
title: "ADR 0048: typed fixed Adapt and Monstrosity actions"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-10"
audience: "rules, compiler, replay, and architecture maintainers"
maintenance: "hand-maintained"
adr_id: "0048"
decision_status: "accepted"
date: "2026-08-10"
---

# ADR 0048: typed fixed Adapt and Monstrosity actions

## Context

Adapt and Monstrosity are resolution-time conditional keyword actions. Their
activated abilities remain legal to activate when the condition will currently
be false. On resolution, both inspect the same current source incarnation and
place +1/+1 counters through replacement effects. Monstrosity then applies a
public, noncopiable designation even if replacement leaves no counters.

Runtime Oracle interpretation, a direct counter write, or a generic annotation
would each create a competing rules owner. Monstrous state additionally needs
stable zone-object identity, control-change and phasing behavior, public
projection, exact replay, and a stored fixed value for future CR 701.37c
consumers.

## Decision

Add the closed `fixed_self_counter_keyword_action` semantic operation for one
source-spanned positive fixed Adapt or Monstrosity instruction. A strict
read-only handler validates the current physical and logical source identity,
checks the relevant condition only during resolution, and emits existing typed
counter-placement intents. Monstrosity follows the counter intent with an
identity-pinned `BecomeMonstrousIntent`.

The rules-layer permanent-designation owner stores the fixed Monstrosity value
on the current `CardInstance`, journals and projects the public transition, and
dispatches a normalized becomes-monstrous event. The designation survives
control changes and phasing, is not copied, and is cleared by the canonical
zone-change owner. The object-local CR 400.7 reset has been extracted from
`CommanderEngine` into a typed rules owner so designation, counters, combat
state, attachments, and retained annotations share one reset boundary.
Historical Game Record v3 card payloads omit the new field
while it is absent, preserving their serialized form and replay hashes.

The operation accepts no arbitrary callback, runtime Oracle parser, card name,
Oracle ID, hidden-zone query, or direct client mutation. Counter placement and
quantity replacement remain owned by the existing canonical counter
transaction. Continuation resume revalidates the source and rejects a
disappeared expected intent before any later result can commit.

## Consequences

Fixed positive Adapt and Monstrosity CardPrograms share one compiler and
runtime family. Activation advertisement and command acceptance retain ordinary
activated-ability legality; a false resolution condition deterministically does
nothing. Competing counter replacements can suspend, persist, resume, roll
back, and replay before the Monstrosity designation commits.

Variable and zero values, compound instructions, granted or copied abilities,
monstrous-matters triggers and static abilities, and executable references to
the stored Monstrosity value remain explicit residuals. The aggregate mechanics
and CR 701.37a, 701.37c, and 701.46a therefore remain partial even though the
bounded capabilities are trusted.

## Alternatives

Parsing reminder or Oracle text at resolution was rejected because CardProgram
must remain the sole executable authority. Writing counters or annotations
directly was rejected because it bypasses replacement, identity, projection,
rollback, and replay. Treating the condition as an activation restriction was
rejected because it would change the rules. Card-specific handlers were
rejected because both keyword actions are reusable typed families.
