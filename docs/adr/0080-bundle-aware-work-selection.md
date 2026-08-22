---
title: "ADR 0080: bundle-aware work selection"
status: "ADR"
authoritative_source: "rules scheduler policy, Git corpus receipts, and generated work-selection evidence"
verified: "2026-08-22"
audience: "rules, compiler, assurance, architecture, and CI contributors"
maintenance: "hand-maintained"
adr_id: "0080"
decision_status: "accepted"
date: "2026-08-22"
---

# ADR 0080: bundle-aware work selection

## Context

The cross-program selector correctly ranked correctness before card gain, but
its coverage candidates were still atomic frontier families. Small siblings
that shared one typed owner and grammar therefore remained individually
ineligible, while coarse residual volume could suggest work that was not one
reusable implementation boundary. Actual harvest outcomes were also copied
into upstream policy by hand, so calibration could disagree with immutable
whole-corpus base-to-head evidence.

## Decision

Retain the rules scheduler and its existing work-selection policy. Static
policy may declare coherent bundles, but each bundle must name all member
frontier families, canonical capability or component owners, source contexts,
normalized literal parameters, shared dependencies and grammar, explicit
exclusions, implementation hours, generation hours, and expected downstream
closure. The generated selector measures the bundle directly from complete
frontier card and ability blocker sets.

Coverage thresholds are disjunctive: a coherent executable candidate is
eligible when it reaches the complete-card, exact-ability, or material-residual
floor. A zero-card structural carrier remains ineligible regardless of raw
volume. Within an equal correctness class, ranking uses complete cards per
cycle hour, shared-context fan-out, one- and two-additional-blocker closure,
normalized value per cycle hour, and then deterministic tie breakers.

Static policy records only immutable harvest provenance: bundle identity,
candidate members, expected complete-card gain, and full base/head Git commits.
The rules-scheduler owner generates `coverage/harvest-outcome-history.json` by
reading the Commander CardProgram and card-unlock-frontier blobs at those
commits. Each receipt includes Git blob IDs, content hashes, compiler and
CardProgram identities, pinned card-data identity, and aggregate counts.
Actual complete-card, exact-ability, and material-residual outcomes are derived
from those receipts and never accepted as policy input.

This refines the coverage-ranking and calibration portions of ADR 0062. Its
class-first correctness ordering and single generated rules-queue authority
remain unchanged.

## Alternatives

- Select the highest atomic residual count. Rejected because unrelated grammar
  can share a coarse residual label without sharing a typed owner.
- Copy actual outcomes into policy. Rejected because policy edits can drift
  from the corpus that produced the result and contaminate upstream inputs.
- Treat the frontier's globally highest arbitrary combinations as bundles.
  Rejected because mathematical co-closure does not establish shared grammar,
  ownership, exclusions, or implementation coherence.
- Use one opaque score. Rejected because it would hide the class ordering,
  throughput, fan-out, blocker closure, and normalized-value tradeoffs.

## Consequences

- Subthreshold sibling families can qualify together through one reviewed
  shared-owner boundary without combining unrelated mechanics.
- Material-residual and exact-ability thresholds operate as documented OR
  conditions while structural zero-card aggregates remain blocked.
- Historical calibration is reproducible from immutable Git corpus receipts.
- Adding a bundle requires explicit coherence and exclusion review; generated
  metrics cannot manufacture semantic ownership.
- The generated queue remains advisory work selection. It does not certify an
  implementation or relax replay, privacy, interaction, architecture, or CI
  gates.

## Removal condition

Retain this decision while the repository uses generated frontier families and
Git-backed corpus evidence for foreground selection. A successor may replace
it only if it preserves one scheduler authority, immutable outcome provenance,
explicit coherent ownership, class-first correctness ordering, and auditable
throughput and blocker-closure fields.
