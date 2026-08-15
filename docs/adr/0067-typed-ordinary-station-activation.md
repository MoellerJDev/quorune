---
title: "ADR 0067: typed ordinary Station activation"
status: "ADR"
authoritative_source: "typed Station compiler, activation owner, and counter-placement transaction"
verified: "2026-08-14"
audience: "rules, compiler, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0067"
decision_status: "accepted"
date: "2026-08-14"
---

# ADR 0067: typed ordinary Station activation

## Context

The generated cross-program selector identified ordinary printed Station as the
highest-priority coherent counter-producer activation family. Correct execution
is not a fixed counter amount: activating taps one other untapped creature the
activator controls, and resolution uses that creature's current power or its
predeparture last known power. The resulting charge-counter event must still
use the canonical counter-placement replacement transaction.

Station symbols and their static threshold effects, toughness substitution,
modified activation costs, and granted or text-changed Station abilities have
different grammar or characteristic boundaries. They are not part of this
decision.

## Decision

The compiler lowers only one complete ordinary printed Station keyword to a
source-spanned, capability-closed activated-ability descriptor. Activation
uses the shared current effective activated-ability catalog, enforces sorcery
timing, and offers one other untapped creature controlled by the activator as a
typed cost object. The cost transaction validates the submitted logical
incarnations and taps that creature through the canonical tap-state owner.

The stack context pins the cost creature's physical and logical identity. The
zone-transition owner records its exact effective power as characteristic last
known information if it leaves before resolution. Resolution reads current
effective power only while the same logical creature remains; otherwise it
uses that pinned predeparture value. Negative power produces zero counters.
An unresolved characteristic or a type change that removes the creature type
fails closed until a cycle-safe broader characteristic boundary is represented.

The reviewed `station` semantic operation accepts only the source permanent,
the resolved nonnegative amount, and the source reference. Its strict read-only
handler emits the existing immutable `PlaceCountersIntent` for charge counters.
The canonical counter transaction retains source-incarnation validation,
replacement ordering, suspension, rollback, multiplayer coordination, replay,
and mutation ownership. A Station source that left the battlefield cannot put
counters on a returned incarnation.

## Alternatives

- Reparse Station reminder text during activation or resolution. Rejected
  because runtime prose is not an authoritative execution boundary.
- Snapshot power when paying the cost. Rejected because Station reads power on
  resolution and uses last known information only after departure.
- Mutate charge counters in the Station owner. Rejected because it would bypass
  the shared replacement-aware counter-placement transaction.
- Trust all type-changing interactions. Rejected until the characteristic
  evaluator can prove a cycle-safe boundary for this dynamic count.

## Consequences

- Ordinary Station gains one typed activation and one reviewed closed semantic
  operation without adding an engine method or direct state-write site.
- Summoning sickness does not prevent a creature from paying this non-tap-symbol
  cost, while ordinary tap state and control legality still apply.
- Copy, removal, and layer-6 ability changes continue to use the shared current
  activated-ability query; no Station-specific ability-presence check is added.
- The Station result composes with existing counter replacement, continuation,
  privacy, rollback, mutation, and exact-replay owners.
- Excluded Station grammar and unresolved type-changing characteristic cases
  remain explicit residual or fail-closed boundaries.

## Removal condition

Retain the focused capability while exact grammar, source and cost identity,
timing, current/LKI power, counter replacement, rollback, privacy, mutation,
and replay evidence pass. Widening requires the appropriate typed static,
characteristic, or activation grammar owner rather than a family-specific
shortcut.
