---
title: "ADR 0057: actionable architecture ownership audit"
status: "ADR"
authoritative_source: "architecture policy, guard baseline, and generated architecture audit"
verified: "2026-08-11"
audience: "architecture, rules, replay, and tooling contributors"
maintenance: "hand-maintained"
adr_id: "0057"
decision_status: "accepted"
date: "2026-08-11"
---

# ADR 0057: actionable architecture ownership audit

## Context

The architecture audit reported direct `GameState` writes as one flat count and
mixed historical branch and CI facts with stable policy. It did not structurally
inventory production runtime access to raw Oracle text, did not expose bounded
subsystem context, and could not distinguish canonical mutation owners from
grandfathered `CommanderEngine` debt. Contributors therefore had to rediscover
ownership and migration order from broad searches, while new runtime text
interpretation could appear without a focused guard failure.

The current source tree contains 54 structurally identified production runtime
Oracle-text access identities. They are existing debt, not newly trusted
behavior. The immediate trigger-processing migration and later owner work must
remove them; this audit must prevent additions while allowing exact removals.

## Decision

Generate one architecture observability model from the existing architecture
policy, module classifications, subsystem ownership source, production AST,
guard baseline, reusable-piece matrix, and interaction matrix. The model:

- classifies every direct state-write identity as a canonical owner write,
  orchestration root replacement, compatibility adapter, grandfathered engine
  debt, unowned write, or reviewed false positive;
- classifies every raw Oracle-text access as compiler input, generated
  provenance, display metadata, reviewed historical compatibility, or
  prohibited runtime interpretation;
- emits bounded subsystem capsules and a deterministic missing-owner migration
  queue;
- separates stable policy, historical observations, evaluated source-tree
  identity, and live Git/worktree coordinates;
- exposes the same generated model through `simctl architecture` rather than a
  second hand-maintained registry.

The architecture guard baseline advances to schema 3 and pins the exact current
prohibited runtime-text identities and direct-write ownership counts. Any new
prohibited runtime interpretation, unowned write, or engine-local write fails.
Removals continue to pass. Existing identity non-growth and module ownership
checks remain in force.

## Alternatives

- Keep documentation-only ownership notes. Rejected because they drift and
  cannot fail a pull request.
- Ban all existing runtime text immediately. Rejected because that would make
  the guard unusable before the bounded trigger and successor migrations can
  remove the debt transactionally.
- Add a new ownership registry. Rejected because architecture policy, module
  classifications, subsystem ownership, reusable pieces, and capability data
  already own those facts.
- Query GitHub from the generated report. Rejected because feature branches,
  exact-head receipts, and worktree slots are transport state; the checked-in
  report must remain deterministic and live facts belong in the CLI view.

## Consequences

- The baseline records existing debt without classifying it as trusted or
  expanding any behavior allowance.
- A new runtime Oracle-text interpretation fails by exact structural identity.
- A new engine-local or unowned direct write fails even if the flat total is
  unchanged elsewhere.
- Contributors can retrieve bounded owner, write, runtime-text, debt, and
  changed-file context without reading the entire central engine.
- Runtime behavior, public protocol schemas, Game Record v3, privacy
  projections, and replay hashes are unchanged.
- The first migration remains trigger processing, followed by zones/object
  identity, turn/priority/decisions, and search/target/choice.

## Removal condition

Retire this exception when prohibited production runtime Oracle-text
interpretation is zero and every serialized grandfathered engine write has
migrated to a declared typed owner. Preserve the generated ownership model and
no-growth guards unless a successor derives at least the same exact identities,
bounded subsystem context, deterministic queue, and live provenance distinction
from the canonical architecture sources.
