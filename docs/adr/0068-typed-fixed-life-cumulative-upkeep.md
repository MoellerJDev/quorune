---
title: "ADR 0068: typed fixed-life cumulative upkeep"
status: "ADR"
authoritative_source: "fixed-life cumulative-upkeep compiler and typed payment owner"
verified: "2026-08-15"
audience: "rules, compiler, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0068"
decision_status: "accepted"
date: "2026-08-15"
---

# ADR 0068: typed fixed-life cumulative upkeep

## Context

Fixed-mana cumulative upkeep already used a source-spanned upkeep trigger, the
canonical age-counter placement transaction, and an optional-payment choice.
The distinct printed form `Cumulative upkeep—Pay N life.` could not reuse its
mana-cost payload, but it has the same ordered counter-then-payment rule and
source-incarnation requirements. Treating the life clause as mana, reparsing
Oracle prose during resolution, or applying a direct life-total write would
break the existing typed ownership boundaries.

Variable life payments, mixed costs, nonpayment consequences other than the
ordinary sacrifice, and granted or text-changed cumulative-upkeep abilities are
different grammar or applicability families. They are not part of this
decision.

## Decision

The compiler lowers only the exact positive fixed-life form to one
source-spanned triggered-ability descriptor. The closed capability shape
requires the source controller's upkeep, one fixed-life payment effect, no
target schema, and the cumulative-upkeep mechanic dependency.

The reviewed `cumulative_upkeep_life` semantic operation first emits the
existing immutable counter-placement intent. After replacement-aware age
counter placement commits, its versioned choice handler computes the life cost
from the resulting age-counter count and offers only the legal pay-or-sacrifice
choice. Payment emits `PayLifeIntent`, which validates and commits through the
canonical life-cost owner. Declining emits the existing identity-pinned
zone-move intent. A departed source, returned incarnation, malformed counter
state, unaffordable or stale payment, or unsupported descriptor fails before
mutation.

Life paid as a cost is not damage and is not a life-loss event. Damage
prevention, damage replacement applicability, and damage replacement ordering
therefore remain explicit fail-closed interaction boundaries rather than being
silently admitted as positive composition.

## Alternatives

- Encode fixed life as a synthetic mana requirement. Rejected because mana and
  life payment have different legality, projection, and mutation owners.
- Mutate the player's life total in the choice handler. Rejected because it
  would bypass the canonical life-cost validation and replay boundary.
- Add a cumulative-upkeep-specific current-ability query. Rejected because
  layer-6 ability addition and removal must eventually share one applicability
  query across static and triggered components.
- Generalize all cumulative-upkeep costs now. Rejected because sacrifice,
  discard, variable, hybrid, and compound costs require their own typed cost
  grammars and interaction evidence.

## Consequences

- Fixed positive life cumulative upkeep compiles and resolves without runtime
  Oracle-text access, card identity, direct state writes, or engine growth.
- Counter-quantity replacement changes the payable life amount before the
  choice is projected, and the same private choice and result replay exactly.
- The new operation remains a closed replay-visible schema entry with one
  registered handler and one capability dependency.
- Unsupported costs and unmodeled damage/prevention relationships remain
  explicit residual or fail-closed boundaries.
- The capability-shape owner remains below architecture review thresholds, and
  existing oversized modules and functions do not grow.

## Removal condition

Retain this focused capability while exact grammar, source identity,
counter-before-payment ordering, replacement suspension, life-cost legality,
decline sacrifice, multiplayer privacy, mutation, and replay evidence pass.
Widening requires the appropriate typed cost or shared ability-applicability
owner rather than a cumulative-upkeep-specific shortcut.
