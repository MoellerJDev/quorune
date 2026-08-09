---
title: "ADR 0043: typed fixed multi-kind counter batches"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-09"
audience: "rules, compiler, replay, and architecture maintainers"
maintenance: "hand-maintained"
adr_id: "0043"
decision_status: "accepted"
date: "2026-08-09"
---

# ADR 0043: typed fixed multi-kind counter batches

## Context

Some Oracle instructions put two or more fixed counter kinds on the same
permanent simultaneously. Replaying those instructions as independent
`place_counters` effects would create false intermediate states, duplicate
replacement-choice windows, and lose the single-event relationship required by
counter replacement ordering. A printed-name branch or arbitrary mapping DSL
would not provide reusable compiler closure.

The family needs one immutable descriptor, one typed intent, and one canonical
counter transaction while preserving source spans, target revalidation,
affected-player choices, rollback, privacy, and exact replay.

## Decision

Add the closed universal `place_counter_batch` semantic operation. Its handler
accepts only the versioned fixed multi-kind descriptor emitted by the compiler,
normalizes distinct positive counter entries, resolves a source-self or direct
public target through the existing read-only query boundary, and emits one
typed batch intent. The canonical counter-placement coordinator remains the
only mutation owner and applies all entries as one replacement-aware event.

The compiler recognizes only the bounded single-sentence grammar represented
by this descriptor. Unsupported variable, conditional, distributed, optional,
or multi-object variants remain material residuals. Capability closure names
the batch producer separately from ordinary single-kind placement; keyword
counter characteristics retain their existing dependencies.

`place_counter_batch` is recorded as a reviewed universal operation in the
ratcheted architecture baseline. It has no callback, raw state access, runtime
Oracle parsing, card identity, or hidden-zone authority.

## Consequences

Equivalent instructions share one runtime owner and one deterministic event
shape. Quantity replacement can suspend and resume before mutation, exact
replay retains the selected ordering, and callers cannot observe partial batch
commit. CommanderEngine and direct authoritative writes remain flat.

The aggregate counter rules, variable counter quantities, counter movement,
and unsupported replacement interactions are not declared complete by this
decision. Future counter producers must reuse this operation only when their
full semantics match its closed descriptor.

## Alternatives

Lowering each counter kind as an independent effect was rejected because it
would expose impossible intermediate states and separate replacement windows.
Extending the generic mapping interpreter without a typed batch intent was
rejected because it would make operation validation and replay identity depend
on an open dictionary grammar. Card-specific handlers were rejected because
the Oracle wording is a reusable rules family rather than card identity.
