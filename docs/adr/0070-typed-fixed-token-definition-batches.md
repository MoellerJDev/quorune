---
title: "ADR 0070: typed fixed token-definition batches"
status: "ADR"
authoritative_source: "fixed-token compiler, capability shape, and canonical token-creation transaction"
verified: "2026-08-16"
audience: "rules, compiler, token, activation, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0070"
decision_status: "accepted"
date: "2026-08-16"
---

# ADR 0070: typed fixed token-definition batches

## Context

The fixed-token compiler already owned one closed token definition at a time,
and the token transaction already owned replacement ordering, object identity,
entry counters, one creation timestamp, semantic entry events, and replay.
Several ordinary spells create two or three different fixed token definitions
simultaneously, but lowering them as separate effects would incorrectly create
multiple token events and apply creation replacements more than once.

Clue was also the remaining ordinary predefined artifact token whose fixed
definition and typed activation fit existing owners. Its printed activation
draws through the canonical draw transaction. Predefined token names can resolve
to database token records, so an explicit compiler-pinned object or token
activation catalog must take precedence over an empty printed catalog without
using token names as runtime behavior keys.

Dynamic quantities, copies, Roles, Incubate, Powerstones and other restricted
mana profiles, quoted custom abilities, attacking or attached tokens, ambiguous
separators, more than three definitions, and compound or conditional
instructions require different grammar or execution ownership and are not part
of this decision.

## Decision

The compiler accepts a simultaneous fixed-token batch only when exactly one
decomposition into two or three independently closed token definitions exists.
It emits `create_token_batch` with a strict ordered definition array and the
union of each definition's capability-backed mechanics. The capability shape
reconstructs and validates each single-token effect, requires the internal batch
marker, and rejects any extra field or unsupported definition.

The token owner validates every definition before mutation and submits the
entire ordered specification set to the existing replacement, entry-counter,
commit, logging, trigger, and replay pipeline. Replacement applicability sees
the aggregate created types and subtypes once. All resulting base and
replacement-created tokens share one creation timestamp and one token-creation
event.

Clue uses an explicit standard-token ability profile. The shared compiled
activation query prefers an explicit typed object or token catalog when present;
otherwise it retains the ordinary source-pinned CardProgram catalog. The Clue
activation pays generic mana and sacrifices through the normal activation-cost
owner, then lowers to the existing private draw operation. No runtime Oracle or
display prose and no printed token name determines execution.

## Alternatives

- Emit one `create_token` effect per definition. Rejected because simultaneous
  token creation is one replacement event, not a sequence of independent
  creation events.
- Add a CommanderEngine batch method. Rejected because the existing dedicated
  token-creation module already owns the transaction and requires no engine
  growth.
- Parse the Clue reminder text at activation time. Rejected because the typed
  predefined-token profile and shared draw owner are the execution authority.
- Accept every comma or conjunction as a batch separator. Rejected because
  color lists, keyword lists, quoted abilities, and compound instructions make
  that grammar ambiguous.

## Consequences

- One reusable simultaneous-batch owner supports the bounded two- and
  three-definition corpus family while preserving replacement semantics.
- Mascot Exhibition, Forbidden Friendship, Bestial Menace, Sokka's Sword
  Training, Cunning Maneuver, Forecasting Fortune Teller, and Knowledge Seeker
  are exact compiler witnesses. Adventure, return, and other unrelated residual
  clauses remain fail-closed.
- Focused tests cover exact and rejected grammar, strict capability shapes,
  real-card promotion, heterogeneous characteristics, one shared timestamp,
  competing additional-token replacements, four-player decision privacy,
  malformed rollback, typed Clue activation, private draw, mutation, and exact
  replay.
- The new universal operation adds no CommanderEngine method, direct state
  writer, card-identity dispatch, or current-game runtime-prose access.
- Layer-6 ability addition and removal continue to use the shared effective
  ability query. Dynamic characteristic counts and affected type-changing
  interactions remain outside this trust claim.

## Removal condition

Retain this focused capability while the unambiguous grammar, per-definition
capability closure, single replacement event, shared timestamp, atomic
validation, typed predefined-token activation, privacy, rollback, mutation, and
replay evidence pass. Any widening requires the appropriate typed quantity,
copy, Role, Incubate, restricted-mana, attachment, attack, reference, or
compound-effect owner rather than a looser token-text parser.
