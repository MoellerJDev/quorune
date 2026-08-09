---
title: "ADR 0045: typed fixed Scry resolution"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-09"
audience: "rules, compiler, replay, privacy, and architecture maintainers"
maintenance: "hand-maintained"
adr_id: "0045"
decision_status: "accepted"
date: "2026-08-09"
---

# ADR 0045: typed fixed Scry resolution

## Context

The legacy Scry choice selected only a subset of looked-at cards to put on the
bottom. It could not express either required ordering independently, cited
obsolete rule numbers, and reused a generic bottom-move intent as the mutation
authority. A complete Scry implementation must keep the looked-at cards private,
reject stale or malformed responses before mutation, and preserve historical
Game Record v3 commands.

## Decision

Compile one positive fixed-controller Scry instruction to the fine-grained
`library.scry.fixed_controller` capability. A dedicated choice handler issues an
ordered two-part partition, and an immutable `ScryArrangement` carries the exact
top and bottom groups to one authoritative library mutation owner. Scry 0 and an
empty library auto-continue without producing a Scry event.

Keep handler identity and a legacy bottom-subset response adapter for historical
command replay. The typed response is the current client contract. Runtime code
uses only the source-pinned CardProgram node and never reparses Oracle text.

## Alternatives

Extending the generic reorder handler was rejected because ordinary reordering
and Scry have different event, privacy, partition, and Scry-0 semantics. Keeping
the subset-only schema was rejected because it cannot implement CR 701.22a.
Card-specific handlers were rejected because fixed Scry is a reusable keyword
action family.

## Consequences

The represented family now owns private inspection, complete partitioning,
independent ordering, stale-state rollback, multiplayer seat projection, and
exact replay. Simultaneous multi-player Scry under CR 701.22c, dynamic counts,
modified Scry instructions, Scry triggers, Surveil, fateseal, and broader library
ordering remain explicit residuals; aggregate Scry is not claimed complete.

