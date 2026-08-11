---
title: "ADR 0056: typed ordinary Crew activation"
status: "ADR"
authoritative_source: "this decision record and the typed ordinary Crew owners"
verified: "2026-08-11"
audience: "rules, compiler, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0056"
decision_status: "accepted"
date: "2026-08-11"
---

# ADR 0056: typed ordinary Crew activation

## Context

Crew was recognized by the legacy activated-ability parser, but its aggregate
power cost and temporary type result remained coupled to the central engine.
That path could not capability-close source-pinned CardPrograms, did not expose
one immutable cost proposal shared by offers and commits, and replaced types
instead of representing the additive type result required by CR 205.1b.

The ordinary Oracle family is bounded: printed Crew N with a fixed nonnegative
integer threshold taps any number of other untapped creatures the activator
controls whose signed current power totals at least N. The cost may use
creatures with summoning sickness because it does not activate their own
tap-symbol abilities. Resolution makes the same Vehicle an artifact creature
until end of turn while retaining its other card types, subtypes, and
supertypes.

## Decision

Compile ordinary printed Crew once into a source-spanned CardProgram V2
activated-ability descriptor. The crew module owns immutable candidates and the
aggregate-power cost plan. Both action availability and activation commit use
that owner, which pins physical and logical identity, reads current effective
types and exact signed power, canonicalizes the selected set in battlefield
order, and revalidates before committing through the existing tap-state owner.

The stack context records the immutable crewed-by snapshots needed for replay
and future typed consumers. Resolution uses one reviewed
add_types_until_end_of_turn operation. Its strict handler accepts a closed
nonempty set of canonical card types and creates one layer-4 continuous effect
that adds Artifact and Creature to the same source incarnation. It grants no
arbitrary callback or GameState access.

The source-pinned runtime handler and capability-shape query are separate
focused modules. Runtime code does not parse Oracle prose or dispatch on a
printed name, collector number, set code, or Oracle ID.

## Alternatives

- Keep the legacy engine implementation. Rejected because offers, cost
  validation, compiler trust, and resolution would retain competing owners.
- Reuse add_type_until_end_of_turn twice. Rejected because two independent
  effects weaken the one-result invariant and can expose intermediate type
  states to later composition.
- Replace the source's type line with Artifact Creature. Rejected because CR
  205.1b retains existing types and subtypes for this wording.
- Add a general type-mutation dictionary operation. Rejected because it would
  admit unreviewed replacement, removal, subtype, supertype, copy, and
  text-changing behavior through the same authority.
- Special-case individual Vehicles. Rejected because card identity is not a
  rules boundary and cannot scale across the Oracle corpus.

## Consequences

- Ordinary fixed-power Crew uses one typed legality and cost owner from action
  advertisement through transactional commitment.
- Summoning-sick creatures, Crew 0, signed power, source exclusion, phasing,
  control changes, zone changes, and source identity are explicit evidence.
- Existing types, subtypes, supertypes, and intrinsic basic-land mana survive
  the additive layer-4 result.
- CommanderEngine shrinks, direct GameState writes remain flat, and the new
  operation is limited to the reviewed closed additive type result.
- Game Record v3 and public protocol schemas remain compatible. New records pin
  the source descriptor, selected cost identities, stack context, and
  continuous-effect journal for exact replay.
- Crew candidates and results are public battlefield information; only the
  current controller receives the activation capability, and no hidden zone is
  queried or projected.
- Crew prohibitions, alternative costs, variable thresholds, effects that crew
  directly, becomes-crewed trigger grammar, and granted, copied, removed, or
  text-changing Crew remain explicit fail-closed residuals.

## Removal condition

Replace these owners only with a more general typed activation-cost and
continuous-type result system that preserves source-spanned compilation,
current effective signed power, canonical cost selection, physical and logical
identity, summoning-sickness scope, additive CR 205.1b types, rollback,
privacy, exact replay, and fail-closed unsupported variants without runtime
Oracle parsing or card-identity dispatch.
