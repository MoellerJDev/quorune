---
title: "ADR 0058: typed trigger-processing ownership"
status: "ADR"
authoritative_source: "typed trigger participation, occurrence, and processing modules"
verified: "2026-08-11"
audience: "rules, replay, compiler, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0058"
decision_status: "accepted"
date: "2026-08-11"
---

# ADR 0058: typed trigger-processing ownership

## Context

ADR 0018 unified simultaneous triggered abilities into one APNAP batch, but
`CommanderEngine` still owned delayed-trigger scheduling and matching, batch
sequencing, Ward discovery, and target-selection coordination. Trigger
discovery also interpreted two live Oracle-text patterns: fixed generic Ward
and the additional-trigger wording used by Panharmonicon-style effects. The
split obscured mutation ownership and made runtime text a competing authority
to compiled CardPrograms.

## Decision

`TriggerProcessingOwner` is the authoritative coordinator for represented CR
603 transitions after a normalized event exists. It owns delayed-trigger
scheduling and matching, immutable occurrence materialization, pending-batch
mutation, APNAP ordering, target-selection delegation, and typed Ward
occurrence collection. `CommanderEngine` retains only narrow compatibility
adapters and high-level stabilization calls.

`TriggerOccurrence` is the immutable pre-placement envelope. Its historical
`PendingTriggerItem` name remains an alias so Game Record v3 checkpoints keep
their existing payload shape and replay meaning.

Executable trigger participation is compiled once into closed fragments:

- `TriggerMultiplierSpec` represents the supported artifact-or-creature-entry
  and another-creature-of-chosen-type predicates;
- `StaticTriggerParticipation` pins the physical source, logical incarnation,
  controller, chosen type where required, and normalized spec;
- `WardSpec` represents only the supported fixed-generic Ward cost.

Discovery evaluates those fragments against current effective characteristics
and control. Unsupported Ward costs and additional-trigger wording remain
explicit compiler residuals. Runtime trigger code may not parse Oracle text or
dispatch on printed card identity.

Specialized combat, prevention, and zone modules remain typed producers of
normalized occurrences. They do not become competing placement owners.

## Alternatives

- Keep delayed scheduling, APNAP placement, Ward discovery, and target
  coordination in `CommanderEngine`. Rejected because it preserves split
  mutation ownership and prevents the trigger-processing boundary from being
  independently validated.
- Continue interpreting Ward and additional-trigger Oracle text during live
  play. Rejected because runtime Oracle parsing would remain a second semantic
  authority beside the compiled CardProgram.
- Introduce card-specific trigger handlers for the currently covered witness
  cards. Rejected because printed identity is not a reusable rules boundary and
  would not provide capability closure for equivalent wording.

## Consequences

- Three authoritative writes leave `CommanderEngine` and are visible as
  canonical writes in the trigger-processing owner.
- Two prohibited runtime Oracle-text accesses are removed.
- Typed multiplier copies carry source provenance and deterministic occurrence
  identities through APNAP placement and exact replay.
- Ward uses the same legal targeting result for occurrence discovery; removed
  abilities, phasing, control changes, malformed costs, and cross-seat
  projection remain fail closed.
- Current private engine adapters remain temporarily available to historical
  fixtures and Game Record v3 integration without regaining implementation
  authority.
- This decision does not claim complete CR 603, Ward, intervening-if, reflexive
  trigger, state-trigger, modal trigger, or arbitrary additional-trigger
  coverage.

## Removal condition

Compatibility adapters may be removed only after every supported external and
historical caller uses the typed public facade and representative older Game
Record v3 fixtures still replay exactly. The typed occurrence, APNAP batch, and
compiled-fragment boundaries remain unless a successor preserves their strict
validation, privacy, rollback, and replay properties.
