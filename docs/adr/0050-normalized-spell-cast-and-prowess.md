---
title: "ADR 0050: normalized spell-cast events and typed Prowess"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-10"
audience: "rules, compiler, trigger, replay, and architecture maintainers"
maintenance: "hand-maintained"
adr_id: "0050"
decision_status: "accepted"
date: "2026-08-10"
---

# ADR 0050: normalized spell-cast events and typed Prowess

## Context

Prowess triggers whenever its controller casts a noncreature spell. Correct
execution depends on the committed spell's controller and current types, the
source permanent's current layer-6 abilities, one trigger per Prowess instance,
APNAP batching with unrelated cast triggers, source identity, and exact replay.
A loose cast dictionary or runtime Oracle-text check would make the event and
the executable granted-ability boundary competing authorities.

## Decision

Construct one strict immutable `SpellCastEvent` after a cast commits. It pins
the physical spell, logical incarnation, controller, origin, stack reference,
and canonical current card types. Its versioned context is the only dispatch
shape used by the represented `spell.cast` and `artifact.cast` trigger paths.

Compile each exact ordinary Prowess occurrence into a source-spanned triggered
CardProgram and a typed layer-6 ability fragment. Trigger discovery requires
that exact fragment in the source's current effective characteristics. Removing
all abilities therefore prevents future Prowess triggers without erasing a
trigger that already exists independently on the stack. The ordinary trigger
handler accepts only a normalized spell-cast event controlled by the source's
current controller whose canonical type set lacks Creature.

The existing unified trigger-batch owner retains APNAP ordering, player trigger
ordering choices, projection, rollback, and replay. The existing continuous
effect owner applies the identity-pinned +1/+1 result until end of turn. No new
state mutation, runtime Oracle parser, card-name branch, or Oracle-ID branch is
introduced.

## Alternatives

- Inspect the cast card and Prowess source directly in `CommanderEngine`.
  Rejected because it would duplicate current-characteristic and trigger-batch
  ownership.
- Execute granted rules text. Rejected because executable abilities must be
  typed fragments participating in layer 6 and capability closure.
- Treat multiple Prowess instances as redundant. Rejected because CR 702.108b
  requires each instance to trigger separately.

## Consequences

Ordinary printed Prowess now composes with control changes, layer-6 ability
removal, simultaneous cast triggers, four-player APNAP ordering, end-of-turn
cleanup, privacy, and exact replay. Equivalent rules-text triggers, conditional
or restricted variants, copied abilities, unsupported ability grants, trigger
multiplication, and broader cast-event families remain explicit blockers. This
does not claim complete Prowess, trigger, continuous-effect, or CR 603 coverage.

## Removal condition

Retire these boundaries only if a successor preserves strict cast-event
identity, typed current layer-6 ability participation, per-instance triggering,
unified APNAP batching, identity-pinned duration, capability closure, and exact
replay without runtime Oracle interpretation.
