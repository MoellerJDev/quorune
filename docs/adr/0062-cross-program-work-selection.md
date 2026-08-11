---
title: "ADR 0062: cross-program work selection"
status: "ADR"
authoritative_source: "rules scheduler policy and generated work-selection evidence"
verified: "2026-08-11"
audience: "rules, compiler, assurance, architecture, and CI contributors"
maintenance: "hand-maintained"
adr_id: "0062"
decision_status: "accepted"
date: "2026-08-11"
---

# ADR 0062: cross-program work selection

## Context

The dependency-ordered rules queue, card-unlock frontier, reusable-piece
interaction matrix, architecture audit, compact-CI dependency report, and
platform replay/privacy status each answered a different scheduling question.
The selected rules batch was therefore easy to mistake for the foreground task
even when a deterministic CI defect, unowned rules boundary, runtime Oracle-text
interpretation, replay/privacy defect, or high-risk interaction gap was more
urgent. Conversely, a large projected card gain could appear authoritative
without exposing its prerequisites or assurance cost.

Shroud, Echo, and ordinary Crew were intentionally implemented ahead of the
already dependency-ready counter-producer queue. Shroud established shared
target advertisement and revalidation. Echo crossed upkeep, trigger, control,
payment, compact-data, and replay boundaries. Crew established a sentinel for
activation parity, effective power, tap commitment, layer-4 results, projection,
rollback, and replay. Those selections did not make the rules queue wrong; they
used scheduling evidence that the queue did not yet combine.

## Decision

The existing generated rules dependency queue remains the single rules queue
and gains a nested cross-program work-selection view. The selector consumes the
canonical compact-CI, platform readiness, architecture, card frontier, and
reusable-piece reports after their registered generators complete. It does not
create a second rules registry or copy their underlying inventories.

Every serious candidate declares its work class, universal subsystem, reusable
pieces, rules dependencies, compiler/runtime/assurance readiness, blocker-card
frontier, expected ability/card/residual gains, interaction debt, architecture
debt removal, write migration, engine extraction, runtime-text removal, effort,
and reranking reason. Unknown projections remain `null` with a basis rather than
being estimated as observed.

Priority is class-first and deterministic:

1. deterministic CI correctness;
2. replay and privacy defects;
3. missing architecture owners;
4. runtime Oracle-text removal;
5. interaction-assurance exit gates;
6. measured architecture debt;
7. dependency-ready rules foundations;
8. compiler harvests;
9. isolated card families.

Card gain orders candidates only within an equal class. Post-stabilization
coverage candidates normally require at least fifty projected complete cards;
very-large coarse frontier rows remain visible in their source report but are
not presented as one executable batch. Runtime Oracle-text debt is likewise
split by generated architecture capsule. Any remainder without a capsule is an
attribution task, not permission to treat several runtime owners as one
implementation batch. The reviewed Shroud, Echo, and Crew reranking rationales
are stable policy history without branch, pull-request, commit, or workflow
identifiers.

`simctl rules next` preserves the selected rules batch for compatibility and
also returns the selected cross-program candidate plus the bounded ranked
candidate list.

## Alternatives

- Use only the card-unlock frontier. Rejected because card gain cannot rank CI,
  replay, privacy, ownership, runtime-text, or interaction defects.
- Replace the rules queue with a new global scheduler. Rejected because the
  rules queue remains the authoritative dependency and conformance schedule.
- Hand-maintain the current task in documentation. Rejected because transient
  selection would drift from generated evidence and would not fail closed.
- Assign one opaque numerical score. Rejected because incomparable units would
  hide why correctness outranked card gain and encourage false precision.

## Consequences

- Contributors can inspect one generated queue to see both the dependency-ready
  rules batch and the actual foreground work.
- Architecture and assurance defects can outrank larger card gains without
  erasing the measured frontier opportunity.
- Generator ordering changes so the rules scheduler consumes final architecture,
  frontier, compact-CI, platform, and reusable-piece outputs.
- Adding a new work class or changing priority requires a reviewed policy change
  and regenerated evidence.
- The selector reports readiness and expected gains; it does not certify that a
  candidate is implemented or authorize weakening any merge gate.
