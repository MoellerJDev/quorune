---
title: "ADR 0059: typed zone-transition ownership"
status: "ADR"
authoritative_source: "typed zone-transition and logical-incarnation modules"
verified: "2026-08-11"
audience: "rules, replay, privacy, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0059"
decision_status: "accepted"
date: "2026-08-11"
---

# ADR 0059: typed zone-transition ownership

## Context

The engine already had typed destination replacement, Aura entry, attachment,
entry-counter, and normalized zone-trigger collaborators, but
`CommanderEngine.move_card` still performed the authoritative zone-list
mutation, CR 400.7 logical-incarnation reset, timestamp allocation, LKI
capture, hidden-zone logging, and simultaneous-move sequencing. That 339-line
method made physical-object continuity, replay behavior, privacy, and event
announcement one oversized engine responsibility.

## Decision

`ZoneTransitionOwner` is the single authoritative commit owner for represented
zone changes. It validates a typed transition cause, prepares the existing
replacement and entry collaborators before mutation, captures departure facts,
then owns:

- removal from and insertion into authoritative zone lists;
- CR 400.7 logical-incarnation reset while preserving physical identity;
- the stack-to-battlefield incarnation exception;
- shared timestamp allocation for simultaneous transitions;
- battlefield acquisition and hidden-zone visibility state;
- public/private transition journals; and
- normalized single and simultaneous zone-change announcements.

`ZoneMovePlan` and `ZoneDepartureSnapshot` separate preflight facts from commit
and announcement. `CommanderEngine` retains narrow compatibility facades for
existing callers and Game Record v3 fixtures, but those facades delegate all
represented mutation to the owner.

Destination replacement, entry-result commitment, Aura legality, attachment
legality, trigger discovery/placement, and state-based actions remain separate
typed owners. The zone owner coordinates their public ports and does not parse
Oracle text or dispatch on printed card identity.

## Alternatives

- Keep `move_card` in `CommanderEngine` and extract only helper functions.
  Rejected because the engine would remain the mutation owner and ownership
  metrics would disguise rather than remove the architectural debt.
- Move destination replacement, Aura legality, attachment cleanup, and trigger
  placement into one zone module. Rejected because it would create a new
  monolith and competing rules authorities.
- Introduce a new persisted zone-event schema. Rejected because the existing
  Game Record v3 state and journal already preserve the required physical and
  logical identity facts.

## Consequences

- Represented single and simultaneous moves use one typed commit boundary.
- Hidden-origin moves keep identity out of public journals while owner and
  analyst projections retain the private record.
- A transaction failure restores all zone membership, identity, timestamp,
  visibility, event, trigger, and attachment state through the existing engine
  transaction boundary.
- Simultaneous moves capture every departure before mutation and share one
  destination timestamp before APNAP trigger placement.
- `CommanderEngine` shrinks substantially while retaining source-compatible
  private facades for existing integration and replay fixtures.
- This decision does not claim complete CR 400 coverage, arbitrary replacement
  effects, face-down rules, meld, phased-out zone semantics, or every unusual
  command-zone interaction.

## Removal condition

Compatibility facades may be removed only after every supported internal and
historical caller uses the typed transition port and representative Game
Record v3 fixtures still replay to identical authoritative hashes. The typed
owner boundary remains unless a successor preserves strict validation,
transactional rollback, private projection, simultaneous LKI, and exact replay.
