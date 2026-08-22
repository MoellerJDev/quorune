---
title: "ADR 0081: bounded-cohort work selection"
status: "ADR"
authoritative_source: "rules scheduler policy and generated candidate-bundle measurements"
verified: "2026-08-22"
audience: "rules, compiler, assurance, architecture, and CI contributors"
maintenance: "hand-maintained"
adr_id: "0081"
decision_status: "accepted"
date: "2026-08-22"
---

# ADR 0081: bounded-cohort work selection

## Context

ADR 0080 added shared-owner candidate bundles and disjunctive card, ability,
and residual thresholds. Its first generated token bundle exposed an important
distinction: family-level blocker co-closure is an upper bound, not proof that
all members share one executable grammar. The affected token families mixed
fixed definitions with copies, dynamic quantities, named tokens, custom
abilities, unsupported keyword mechanics, linked results, delayed behavior,
modal carriers, and predefined-token gaps. Applying the declared exclusions
removed the apparent whole-card closure rather than certifying it.

The same risk applies to coarse atomic residual families. A large residual
count can combine unrelated syntax even when every row has the same family
label.

## Decision

Candidate bundles remain visible generated evidence, but a synthesized bundle
is `upper_bound_only` until an affected-cohort probe defines one closed grammar
and measures its executable lower bound. Static owner hypotheses, source
contexts, cycle hours, and exclusions cannot convert an upper bound into an
eligible harvest.

Atomic frontier candidates may use the exact-ability or material-residual OR
threshold only when the corresponding nodes are already lowerable but remain
untrusted. Missing-lowering residual volume requires a bounded cohort or an
explicit prerequisite review. Complete-card gain remains usable only after the
same structural and effort gates.

The selector may return no eligible foreground after it has synthesized and
classified candidate bundles. That is a valid fail-closed result, not a reason
to select the largest coarse family. The next development cycle must classify
another family or add a generated bounded-cohort measurement; it must not copy
an estimated lower bound into policy.

A bundle may declare `bounded_executable` only when the generated frontier
proves that every occurrence in every member family is already lowerable and
untrusted, the recomputed cross-family card rows account for the same exact
ability count, and at least that many material residuals are removable. Any
drift in those generated counts demotes the bundle back to
`requires_bounded_cohort`. A setup-only family may use the honest `setup`
source context; it does not invent spell, trigger, or activation fan-out merely
to rank more highly.

This supersedes ADR 0080 only where it treated family-level bundle co-closure as
an executable measurement. ADR 0080's immutable harvest receipts, bundle
metadata, class-first correctness ordering, and auditable throughput fields
remain in force.

## Alternatives

- Subtract exclusions informally from the upper bound. Rejected because the
  affected cards, abilities, and residuals would not be reproducible.
- Select an upper bound and refine during implementation. Rejected because it
  repeats the slow, low-yield harvest pattern the selector is intended to stop.
- Treat residual count alone as the third OR threshold. Rejected for
  missing-lowering families because a shared label does not establish shared
  grammar or runtime ownership.
- Hide unmeasured bundles. Rejected because visible upper bounds and explicit
  deferral reasons are useful classification pressure.

## Consequences

- Generated bundle upper bounds cannot become foreground without an executable
  cohort measurement.
- Reviewed bounded bundle declarations remain eligible only while the current
  generated frontier independently verifies their executable census.
- Already-lowered untrusted ability and residual families can still qualify
  through the documented OR thresholds.
- A zero-eligible result is explicit and auditable.
- Bounded probes must report the closed grammar, contexts, dependencies,
  exclusions, lower/upper gains, and cycle estimate before implementation.

## Removal condition

Retain this decision while frontier families can contain multiple independent
grammars. A successor may remove the upper-bound gate only if the frontier
itself emits independently verified executable cohort identities with closed
owners, filters, exclusions, and lower-bound measurements.
