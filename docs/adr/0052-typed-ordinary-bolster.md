---
title: "ADR 0052: typed ordinary Bolster resolution"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-10"
audience: "rules, compiler, counter, replay, and architecture maintainers"
maintenance: "hand-maintained"
adr_id: "0052"
decision_status: "accepted"
date: "2026-08-10"
---

# ADR 0052: typed ordinary Bolster resolution

## Context

Bolster N is a mandatory keyword action that asks its resolving player to
choose a creature they control with the least toughness among creatures they
control, then places N +1/+1 counters on that creature. Correct execution
therefore depends on the canonical effective-characteristic query, an
immutable public candidate snapshot, deterministic seat-scoped choice
continuation, and replacement-aware counter placement. Treating Bolster as an
ordinary target or choosing from printed toughness would produce incorrect
legality and stale decisions.

## Decision

Compile each exact fixed positive Bolster instruction into a source-spanned
CardProgram node with the closed `fixed_bolster` semantic operation. The
runtime handler obtains controlled phased-in battlefield creatures through the
shared object query, requires every candidate's effective toughness to be an
exact integer, retains only the least-toughness ties, and issues one
controller-scoped choice using physical and logical object identity.

The handler is read-only and emits the existing `PlaceCountersIntent` and
choice journal intent. Canonical counter placement owns replacement discovery,
ordering, suspension, mutation, rollback, and replay. If no legal creature
exists, the impossible mandatory choice is skipped and resolution continues
without mutation. Any stale identity, changed candidate set, unresolved
toughness, malformed amount, or unsupported wording fails closed before
counter mutation.

`object_query.exact_numeric_characteristic` is the single shared conversion
boundary for exact numeric power and toughness. CommanderEngine retains only a
narrow compatibility delegation and shrinks; the Bolster handler receives no
mutable GameState, runtime Oracle text, or card identity.

## Alternatives

- Reuse ordinary targeting. Rejected because Bolster does not target and its
  candidate set is constrained by a relative characteristic minimum.
- Compare printed toughness. Rejected because continuous effects and counters
  determine the current effective toughness used by the rule.
- Compute the choice inside CommanderEngine. Rejected because it would retain
  choice sequencing and characteristic ownership in the orchestration facade.
- Guess a numeric value for `*` or another unresolved characteristic. Rejected
  because unsupported layer or characteristic behavior must fail closed.

## Consequences

Fixed positive Bolster now composes across spell, triggered, and activated
effect contexts with exact effective-toughness ties, no-creature resolution,
four-player privacy, counter-quantity replacement, rollback, and exact replay.
The operation adds no direct GameState write and no card-name, collector,
set-code, or Oracle-ID behavior. Bolster X, nonpositive values, copied or
granted fragments outside the represented typed path, repeated or conditional
instructions, unresolved characteristic layers, and broader choice/counter
variants remain explicit blockers. This decision does not claim complete
Bolster, counters, continuous effects, choices, or CR 701 coverage.

## Removal condition

Retire `fixed_bolster` only if a successor preserves source-spanned
compilation, exact effective-toughness comparison, immutable candidate and
incarnation identity, seat-scoped continuation, canonical replacement-aware
counter placement, rollback, privacy, capability closure, and exact replay
without runtime Oracle interpretation.
