---
title: "ADR 0042: canonical generated-artifact finalization"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-08"
audience: "contributors, maintainers, and coding agents"
maintenance: "hand-maintained"
adr_id: "0042"
decision_status: "accepted"
date: "2026-08-08"
---

# ADR 0042: canonical generated-artifact finalization

## Context

Quorune tracks generated rules, compiler, architecture, readiness, and coverage
artifacts because they are reviewable public evidence and inputs to other
reports. Their writers previously appeared as duplicated command lists in CI,
local guidance, and agent instructions. Some outputs consumed other generated
outputs, but that dependency order was not machine-readable. A contributor
could therefore refresh one report, invalidate a downstream report, and learn
about the omission only after exact-head CI had already run broad jobs.

Two implementation details amplified the churn. Platform readiness embedded a
fingerprint of almost every tracked non-generated file even when its actual
readiness inputs were unchanged, and test discovery counted synthetic unittest
loader failures without rejecting the broken environment. The architecture
audit also copied volatile `verified` digests from generated documents into its
own output.

The failure sequence was observed repeatedly rather than inferred: stale
platform status was followed by stale architecture outputs and then stale
reusable-piece fingerprints on consecutive exact heads. The current generated
[CI escape report](../../coverage/ci-escape-report.md) retains the concrete
workflow evidence. The common cause was copied generator lists with no
executable dependency graph or fixed-point finalization step.

A later compiler-family change exposed one remaining undeclared edge: the
card-unlock frontier compared its freshly compiled CardProgram states with four
tracked Oracle/CardProgram census files that had no manifest owner. A compiler
version could therefore advance without refreshing those inputs, and any real
status-count change failed only at the final frontier check.

## Decision

`platform/generated-artifacts.json` is the canonical registry for deterministic
Python reports enforced by generated/architecture CI. It declares one owner for
every registered output, generator dependencies, check and write commands, and
whether writing is automatic, requires the pinned card database, or is an
explicit manual baseline action. Protocol types, pinned rules snapshots, and
other separately governed generated assets retain their existing owners.

`scripts/finalize_generated.py` is the ordinary write and freshness interface.
It runs automatic writers in topological order, repeats them to a bounded fixed
point, runs every manifest check, validates documentation, and performs diff
hygiene. Database-backed generators use `--db` or `MTG_CARD_DB`; a generator may
provide a safe derived-only writer when its corpus inputs do not require the
database. Manual performance baselines are checked but are never rewritten
unless explicitly requested.

The manifest also owns the full and Commander-legal Oracle and CardProgram
censuses as one database-backed generator. That generator precedes the
card-unlock frontier and platform/architecture consumers. The CardProgram
reports persist compiler, capability-evidence, capability-registry, and pinned
card-data fingerprints so check mode rejects stale source even when aggregate
status counts happen not to change.

The pinned corpus is rebuilt only on the first topological pass. Stabilization
passes rerun only changed generators and their downstream automatic or safe
derived-only consumers, because rerunning unrelated writers or an unchanged
multi-minute corpus producer would add latency without changing any declared
downstream ordering.

Project guidance requires write mode after the source, tests, and documentation
are coherent and before the final commit. Contributors inspect and stage those
outputs with the causal source change. The pre-push hook is deliberately a
second line of defense rather than the first time finalization should run.

Pull-request CI invokes the same finalizer in check-only mode. The local impact
plan selects that one command instead of maintaining another generator list.
An opt-in repository-owned pre-push hook runs write mode with the worktree-local
CPython 3.12 environment and aborts when it creates uncommitted outputs. It does
not amend commits or push generated changes automatically.
When `MTG_CARD_DB` is unset, the hook accepts the worktree's ordinary exact
receipt first. The ordinary finalizer already performs every database-backed
freshness check, so an unrelated change does not rebuild the corpus merely
because `data/scryfall-current.sqlite3` exists. If that receipt is stale, the
hook uses the worktree database when present and prints explicit database
guidance otherwise. An explicitly selected `MTG_CARD_DB` remains part of the
receipt identity and requires database-bound finalization.

Platform readiness fingerprints only its authoritative source and derived
package, stable test-shard inventory, rules, and CardProgram inputs. Exact
source-tree equivalence remains owned by the ephemeral certification receipt
and main-smoke verification. Any remaining unittest discovery used by a
generator fails closed on loader errors. Architecture documentation metrics
validate generated-document metadata but normalize volatile owner-generated
verification digests instead of embedding them.

## Alternatives

Keeping a prose ordering checklist was rejected because it had already allowed
repeatable deterministic omissions. Letting CI write or commit outputs was
rejected because it would move the reviewed head, complicate fork permissions,
and create workflow-loop and provenance risks. A pre-commit hook was rejected
because incremental commits are allowed and generators must observe the
coherent final worktree, not a partially staged snapshot. Removing freshness
checks was rejected because the reports enforce real architecture, trust,
coverage, and documentation boundaries.

## Consequences

Contributors use one command for generated finalization and no longer need to
memorize individual ordering. CI and local tooling share the same ownership
manifest, and tests reject duplicate outputs, dependency cycles, or drift back
to copied workflow lists. Ordinary source edits no longer churn platform
readiness solely because the repository tree changed.

Database-backed compiler and corpus changes still require a valid pinned card
database. Manual performance baseline changes remain deliberate review events.
The pre-push hook is local Git configuration and can be bypassed, so public
exact-head CI remains the final authority.

The finalizer's post-check phase also runs the reviewed architecture policy
validator. Generated freshness and architecture authorization are separate
properties: a branch can have byte-for-byte current reports while adding a new
unreviewed semantic operation. Keeping the policy validator behind the same
required pre-commit command and pre-push backstop prevents that distinction
from becoming another CI-only discovery.
