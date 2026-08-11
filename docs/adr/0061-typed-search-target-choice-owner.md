---
title: "ADR 0061: typed search, target, and choice ownership"
status: "ADR"
authoritative_source: "selection contracts and typed operation owners"
verified: "2026-08-11"
audience: "rules, replay, privacy, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0061"
decision_status: "accepted"
date: "2026-08-11"
---

# ADR 0061: typed search, target, and choice ownership

## Context

`CommanderEngine` historically issued and completed target choices, hidden-zone
searches, APNAP selections, Storm copy targets, legend-rule choices, and Battle
choices through unrelated mapping continuations. The rules contracts differ:
targeting has revalidation and protection rules, hidden search has privacy and
fail-to-find rules, and public nontarget choices must not accidentally acquire
target semantics. Their shared replay identity was nevertheless implicit.

## Decision

`SelectionContinuation` is the immutable versioned envelope for the remaining
represented selection paths. It pins the contract, operation ID, actor, state
revision, stack and source identities, visibility, and an immutable
operation-owned payload. Targeting, hidden search, APNAP coordination, Storm,
and represented public choices use separate owners and operation IDs. Target
snapshot queries are read-only and isolated from `CommanderEngine`.

Current Game Record v3 continuation shapes are accepted only by explicit
operation-local compatibility adapters. `SemanticChoiceContinuation` v2 remains
the existing typed handler payload for semantic-choice registry operations; it
is not a second authority over target or search legality and is not rewritten
solely for naming uniformity. Activation cost selection remains within the
typed activation proposal and commit boundary.

The engine retains high-level completed-decision dispatch and domain-specific
candidate calculation. It no longer implements the extracted begin/complete
target, search, APNAP, Storm, legend, or Battle choice transactions.

## Alternatives

- Treat every selection as targeting. Rejected because search and nontarget
  choice obey materially different rules and privacy contracts.
- Keep mapping continuations and validate fields ad hoc. Rejected because stale
  actor, source, revision, or visibility changes would remain replay hazards.
- Redesign Game Record v3 around one new semantic-choice schema. Rejected
  because the existing typed semantic-choice registry is replay-pinned and a
  record redesign is not required for ownership extraction.

## Consequences

- New selection operations must declare an exact contract and closed operation
  payload.
- Actor, revision, source/stack identity, visibility, and legal candidate facts
  fail closed before mutation.
- Hidden search candidates remain actor-private, while public choices expose
  only public references and seats.
- Target completion and resolution revalidation use the same effective
  characteristic and protection queries.
- `CommanderEngine` shrinks and remains the orchestration facade.
- This decision does not claim every Magic choice, search variant, target
  restriction, or cost grammar is implemented.

## Removal condition

Game Record v3 compatibility adapters may be removed only after all supported
historical records no longer require their prior continuation shapes. The typed
contract distinction and immutable envelope remain.
