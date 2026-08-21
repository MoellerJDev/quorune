---
title: "ADR 0078: input-fingerprinted generated-owner reuse"
status: "ADR"
authoritative_source: "generated-artifact manifest and cloud owner receipts"
verified: "2026-08-21"
audience: "CI, compiler, and generated-artifact contributors"
maintenance: "hand-maintained"
adr_id: "0078"
decision_status: "accepted"
date: "2026-08-21"
---

# ADR 0078: input-fingerprinted generated-owner reuse

## Context

ADR 0042 established one dependency graph and exact-source finalization, but
the implementation still treated a commit SHA and almost the entire tracked
tree as the reusable unit. A pull-request head and its content-identical merge
commit therefore repeated the compiler census and every downstream report.
Unrelated owners also ran because the workflow copied a fixed stage list rather
than deriving affected owners from declared inputs. The resulting three-to-four
hour PR cadence made broad card harvests slower than their semantic work.

Commit identity is necessary for a downloadable final bundle, but it is too
coarse for deterministic intermediate products. Reuse is sound only when the
owner implementation, direct source closure, dependency outputs, and governed
database provenance are identical.

## Decision

Schema 3 of `platform/generated-artifacts.json` declares reusable input groups,
owner-specific direct inputs, static implementation entry points, database
identity, execution class, and reuse policy. Static local Python imports extend
each implementation entry point into its transitive implementation closure.
Generated outputs and the complete manifest file are excluded from direct
source globs; the selected owner row is hashed separately.

`scripts/generated_owner_cache.py` computes one content identity per owner from
Git-clean source blobs, the canonical owner row, each dependency's Git-clean
output fingerprint, and the pinned database identity when applicable. It never
includes the commit SHA. Reusable receipts are strict, immutable, and bind all
outputs by raw SHA-256 and Git-clean blob identity. A missing cache runs the
owner once, a valid hit installs it, and malformed or contradictory data fails
closed. An unchanged owner selected out by the generated affected-owner plan
may inherit the exact checked output already committed at the base.

The pinned card database is cached by its governed snapshot and builder inputs.
Before use, its provenance identity also verifies SQLite integrity, schema, and
table cardinalities. Database-backed owner receipts bind that identity rather
than a runner-local path or file timestamp.

The same affected-owner planner is used by the local pre-corpus quick-gate
phase and the parallel cloud workflow. A compiler-identity sentinel runs before
any census and requires an Oracle compiler, Oracle IR schema, or CardProgram
schema identity change whenever the static semantic compiler implementation
closure changes. The census has one owner and one immutable input key, so an
exact key can produce at most one successful reusable artifact.
An operator may request diagnostic recomputation only with a recorded nonempty
force reason; the recomputed receipt must equal the immutable cached receipt.

The cloud workflow runs on source-changing PR events and `main` pushes. It is
deliberately not subscribed to `ready_for_review`. PR-produced owner artifacts
are reusable by a content-identical merge commit, while every staged owner
envelope and the complete downloadable bundle remain bound to the exact checked
out commit and source-tree fingerprint. The bundle job verifies the assembled
DAG and writes a finalization receipt without rerunning any owner.
Cross-run lookup accepts only completed executions of this workflow whose head
repository is Quorune itself. A successfully checked owner receipt survives a
later downstream workflow failure or cancellation; an owner that published no
receipt retries. Fork-run artifacts are never reuse sources for `main`.

This decision supersedes ADR 0042 only for generated-owner scheduling and
intermediate reuse. ADR 0042 remains authoritative for single ownership,
dependency ordering, tracked-output review, and exact final verification.

## Alternatives

- Cache by commit SHA. Rejected because merge commits cannot reuse PR work.
- Cache only the corpus files. Rejected because downstream reports can consume
  different dependency outputs under the same source label.
- Trust a database path or timestamp. Rejected because neither establishes
  pinned corpus equivalence across runners.
- Rerun the ordinary finalizer after cloud assembly. Rejected because it turns
  verified owner artifacts back into duplicated execution.
- Subscribe to draft-to-review transitions. Rejected because they change no
  tracked source and ADR 0066 already establishes content-bound CI reuse.

## Consequences

The first schema-3 run is a conservative cold start because schema-2 history
has no declared input closure. Later PR and post-merge runs reuse unchanged
owners across commits and run only the affected closure on misses. Broad public
CI remains the regression authority, but its expensive generated work happens
after cheap compiler, manifest, and focused impact sentinels.

Input declarations are now correctness boundaries. Adding a dynamic source
read, implementation helper, dependency, or database input requires updating
the owner row in the same change. Cache corruption cannot be repaired by
silently accepting the output; the immutable key must be invalidated by a real
input or cache-schema change.
