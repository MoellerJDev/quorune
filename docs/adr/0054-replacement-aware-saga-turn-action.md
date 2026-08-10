---
title: "ADR 0054: replacement-aware Saga turn action"
status: "ADR"
authoritative_source: "this decision record and the typed Saga turn-counter coordinator"
verified: "2026-08-10"
audience: "rules, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0054"
decision_status: "accepted"
date: "2026-08-10"
---

# ADR 0054: replacement-aware Saga turn action

## Context

Ordinary Saga entry already creates its lore counter inside the canonical
replacement event tree. The later CR 714.3c turn-based action instead wrote a
typed `counter_state` plan directly. That correctly avoided Doubling Season,
whose Oracle text is restricted to counters put by an effect, but it also
excluded replacements whose wording applies whenever their controller would
put counters. It could not suspend before mutation when multiple such effects
were applicable.

Treating all counter placements as effects would produce the opposite rules
error. Adding a Saga-specific replacement switch would duplicate the CR 616
ordering, subject identity, privacy, rollback, and replay owners.

## Decision

The precombat Saga action creates one simultaneous canonical
`counter.place` batch with `effect_generated=false`. Each event pins the
physical and logical Saga identity, current controller, battlefield zone,
placing player, lore counter name, and requested amount. Existing typed
quantity replacements therefore evaluate their declared scope: unqualified
replacements may apply, while `effect_only` replacements do not.

If multiple replacements are applicable, `turn_counter_coordination.py`
issues the ordinary seat-scoped replacement decision before any counter or
chapter trigger is created. Its strict continuation pins the phase frame,
event IDs, affected objects, replacement snapshot, selection journal, and any
triggers already waiting for priority. Held triggers use the canonical
immutable `PendingTriggerItem` model rather than a continuation-local stack
shape. Resume revalidates that frame and each held trigger, retries the same
immutable batch, commits every resulting lore placement together, then
discovers crossed chapter events and completes the existing step-entry trigger
batch exactly once.

## Alternatives

- Keep the direct counter-state plan because the action is not an effect.
  Rejected because “not an effect” narrows applicability; it does not make the
  counter event immune to every replacement effect.
- Mark the turn action effect-generated so existing descriptors see it.
  Rejected because that makes Doubling Season and other effect-qualified text
  apply illegally.
- Add bespoke checks for individual replacement cards. Rejected because card
  identity is not a rules boundary and would create a competing runtime owner.

## Consequences

- Saga entry and turn progression remain distinct rules events but share the
  same counter-placement transaction and typed replacement descriptors.
- Competing unqualified replacements suspend transactionally and project only
  to the affected controller.
- No lore counter, chapter trigger, or priority grant occurs before ordering
  is complete.
- Save/load and command replay preserve the suspended turn action without
  replaying the precombat-main boundary.
- The ordinary no-replacement journal remains compatible with prior Game
  Record v3 behavior.
- Read Ahead, arbitrary lore movement, untrusted chapter programs, and counter
  replacement families outside the represented typed vocabulary remain
  fail-closed.

## Removal condition

Replace this coordinator only with a more general typed turn-based-action
transaction that preserves event origin, simultaneous counter placement,
strict continuation validation, seat privacy, rollback, chapter timing, and
exact replay without runtime Oracle parsing or card-specific dispatch.
