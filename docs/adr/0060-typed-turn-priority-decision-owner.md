---
title: "ADR 0060: typed turn, priority, and decision ownership"
status: "ADR"
authoritative_source: "typed turn-step, priority-yield, and capability modules"
verified: "2026-08-11"
audience: "rules, replay, privacy, server, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0060"
decision_status: "accepted"
date: "2026-08-11"
---

# ADR 0060: typed turn, priority, and decision ownership

## Context

`CommanderEngine` historically selected turns, wrote phase and step state,
granted and passed priority, applied yield optimization, audited decision
opportunities, ran cleanup iterations, and issued capability-scoped decisions.
Those responsibilities formed one implicit state machine spread across large
engine methods. That made Full Control, automatic passing, multiplayer turn
order, cleanup exceptions, reconnect, rollback, and exact replay difficult to
review as one contract.

## Decision

Three cooperating typed owners form the authoritative boundary:

- `TurnStepOwner` selects normal and extra turns, commits turn-start state,
  establishes phase/step boundaries, advances the step table, repeats cleanup
  when CR 514.3 requires priority, and coordinates represented end-the-turn
  effects;
- `TurnPriorityDecisionOwner` grants and passes priority, owns yield epochs and
  invalidation, records meaningful-action opportunities, and runs the
  deterministic priority pump; and
- `CapabilityManager` issues, validates, consumes, reissues, and invalidates
  principal-scoped single-use decision capabilities.

Immutable `PriorityGrantPlan` and `PriorityPassPlan` close and serialize the
priority transition vocabulary. The engine retains narrow compatibility
facades and performs step-specific rules actions through a callback after the
turn owner has committed the canonical boundary. Stack, zone, control, draw,
combat, trigger, and continuous-effect mutation remain with their existing
typed owners.

The persisted Game Record v3 representation is unchanged. Yield counters keep
their historical keys, and the same event ordering and ref allocation are
preserved.

## Alternatives

- Keep the scheduler in `CommanderEngine` and extract only signature helpers.
  Rejected because authoritative turn and phase writes would remain engine
  debt.
- Move every beginning-, combat-, and ending-step rule into one scheduler
  module. Rejected because that would replace the engine with a new rules
  monolith and compete with draw, trigger, combat, and cleanup collaborators.
- Let browser Full Control or auto-pass settings advance the game directly.
  Rejected because clients are untrusted; they may express policy but cannot
  own legality or state transitions.

## Consequences

- Turn, phase, priority, yield, and decision-capability ownership is explicit.
- Manual Full Control and automatic passing traverse the same authoritative
  priority transition and action-opportunity audit.
- Rollback replaces `GameState` without leaving an owner bound to a stale
  snapshot because owners dereference the engine host at commit time.
- Step-specific rules remain independently owned while receiving a committed,
  canonical phase/step boundary.
- `CommanderEngine` shrinks while keeping private facade compatibility for
  existing tests, records, and service code.
- This decision does not claim complete turn-control effects, skipped phases or
  steps, every cleanup interaction, or complete rules coverage for all actions
  available during priority.

## Removal condition

Compatibility facades may be removed only after all supported callers use the
typed ports and exact Game Record v3 replay, private projections, reconnect,
multiplayer ordering, cleanup exceptions, and Full Control behavior remain
certified. The typed ownership boundary remains.
