---
title: "ADR 0064: context-aware card-identity guard"
status: "ADR"
authoritative_source: "architecture policy and bounded Python identity-flow analysis"
verified: "2026-08-12"
audience: "rules, compiler, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0064"
decision_status: "accepted"
date: "2026-08-12"
---

# ADR 0064: context-aware card-identity guard

## Context

The previous architecture guard compared every production string literal with
a database-derived hash index of printed card names. It measured lexical
coincidence rather than authority flow: ordinary rules vocabulary such as
`life`, `stun`, `vigilance`, and `reason` needed structural allowances, while a
future card name or a name assembled from pieces could evade the index. The
result depended on a card database, a generated name index, a large allowance
baseline, and source fingerprints that turned harmless data refreshes into
architecture-governance work. It still could not establish whether identity
selected gameplay behavior.

## Decision

The architecture gate performs a bounded Python AST identity-flow analysis over
every production module. Configured card-name, face, collector-number, set-code,
and Oracle-ID fields are sources. Within one module or function scope, the
analysis follows direct attributes and mapping reads through simple assignments,
tuple unpacking, aliases, static constants and containers, string concatenation,
and common string normalization. Static comparisons, membership tests, match
patterns, and identity-keyed implementation-map lookups are fixed-dispatch
sinks.

Card identity remains valid data. Display metadata, generated provenance,
compiler self/face binding, dynamic typed rules predicates, and ordinary replay
identity are classified and inventoried. Fixed identity may not select generic
legality, mutation, implementation, capability, or outcome. A compiler module
does not receive a broad exemption: only structural `front`/`back` face binding
is accepted there. Every other fixed dispatch fails with no baseline or growth
allowance.

Historical Game Record v3 compatibility and explicit card overrides remain
allowed only when the exact generated module classification proves those
boundaries. Existing Oracle-ID shortcut behavior is moved under the reviewed
override package rather than hidden by a generic exception. Adding or widening
an override still requires its ordinary architecture review; no architecture
exception authorizes the identity-flow guard itself.

The generated architecture inventory records each classified flow, its source
and sink kind, exact module classification, stable structural flow ID, allowed
override location, and any prohibited location. Flow IDs hash structural AST
content and enclosing symbols rather than line numbers. The old card-name hash
index, printed-name allowance baseline, source-record exemption field, database
dependency, and work-selection debt derived from raw name counts are removed.

The analysis is deliberately bounded. It does not claim interprocedural taint,
reflection, dynamically constructed containers, arbitrary return-flow analysis,
or general information-flow/privacy coverage. Those limitations are serialized
in policy and generated evidence. New source or sink shapes require focused
synthetic tests and an explicit policy update instead of an implicit lexical
allowance.

## Alternatives

- Continue growing the lexical allowance baseline. Rejected because it rewards
  string splitting, confuses rules vocabulary with card identity, and makes card
  data refreshes architecture-authoritative.
- Ban all card-identity reads in production. Rejected because identity is valid
  data for display, compilation, replay, provenance, typed predicates, and
  explicitly reviewed compatibility or overrides.
- Introduce a repository-wide interprocedural taint framework. Rejected for this
  correction because the fixed-dispatch invariant is enforceable with a small,
  auditable analyzer and explicit documented limits.

## Consequences

- Ordinary domain strings and arbitrary future card-name literals no longer
  create debt unless identity reaches a fixed dispatch sink.
- Name splitting and normalization do not evade the represented source-to-sink
  paths.
- Architecture generation and validation no longer require a card database or
  printed-name artifacts.
- The scheduler consumes `prohibited_identity_dispatch_count`, whose baseline is
  permanently zero, instead of raw printed-name counts.
- Reviewed overrides and historical compatibility become visible classified
  inventory rather than generic path exemptions.
- Rollback means restoring this analyzer and policy with its zero-prohibited
  invariant. Reintroducing the lexical index or allowance baseline is not a
  supported rollback because it would restore the architectural defect.
