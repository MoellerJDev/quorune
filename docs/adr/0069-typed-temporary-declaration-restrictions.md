---
title: "ADR 0069: typed temporary declaration restrictions"
status: "ADR"
authoritative_source: "activated temporary declaration-restriction compiler and layer-6 continuous-effect owner"
verified: "2026-08-16"
audience: "rules, compiler, combat, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0069"
decision_status: "superseded"
date: "2026-08-16"
---

# ADR 0069: typed temporary declaration restrictions

> Superseded by
> [ADR 0072](0072-resolution-created-declaration-rules.md), which preserves the
> compiler family and duration journal while correcting the resolved result
> from a layer-6 added ability to an independent declaration rule.

## Context

The declaration solver already consumes source-spanned typed restriction
fragments through one effective layer-6 ability query. Activated abilities that
temporarily prohibit a target creature from attacking, blocking, both, or being
blocked remained compiler residuals even though the declaration vocabulary,
resolution-created continuous-effect journal, target revalidation, duration,
and replay owners already existed.

These four whole clauses form one closed result family. Source-relative
blocking restrictions, blocking exceptions, optional targets, compound riders,
conditions, next-turn durations, spells, and triggers require different
grammar, reference, or execution ownership and are not part of this decision.
Dynamic characteristic-count predicates whose evaluation could re-enter a
type-changing layer dependency cycle also remain outside trust.

## Decision

The activated-ability compiler lowers only the four exact target-creature
clauses to `grant_declaration_restriction_until_end_of_turn`. The strict
operation accepts one revalidated battlefield target, one of four enumerated
restriction kinds, and typed resolving-source identity.

The rules owner translates the kind into the existing
`DeclarationRestrictionTemplate` vocabulary and commits it as an
identity-locked layer-6 `add_ability_fragment` continuous effect until cleanup.
It does not add a declaration-family presence flag or specialized combat
lookup. Ability addition, later `remove_all_abilities`, and declaration solving
all observe the same effective ability-fragment boundary. A departed, phased,
returned, malformed, or unsupported target fails before the new effect is
committed.

The operation is a reviewed universal semantic result with a closed payload.
It cannot carry Oracle prose, card identity, arbitrary callbacks, dynamic
predicates, or direct state mutation. The existing continuous-effect journal
owns object identity, duration, rollback, and Game Record replay.

## Alternatives

- Check a temporary combat marker in attack and block code. Rejected because it
  would create a family-specific applicability path outside the shared
  effective layer-6 ability query.
- Reparse the resolving ability's Oracle text. Rejected because compiler-pinned
  typed semantics are the sole current-game authority.
- Compile every phrase containing `can't attack`, `can't block`, or `can't be
  blocked`. Rejected because source references, exceptions, optionality,
  conditions, riders, and other durations have materially different semantics.
- Generalize dynamic declaration predicates in this change. Rejected because
  trustworthy characteristic counts require a cycle-safe characteristic
  boundary or an explicit exclusion of affected type-changing interactions.

## Consequences

- Forty Commander-legal activated abilities across the four exact forms enter
  one typed producer and remove forty material residuals; twenty-three cards
  become capability-closed.
- Actual activation, target resolution, attack and block legality, cleanup
  expiry, layer-6 ability removal, malformed rollback, multiplayer identity,
  and exact replay are covered by focused behavioral tests.
- Runtime Oracle-text access, card-identity dispatch, direct state writes, and
  CommanderEngine size remain flat.
- Unsupported declaration grammar remains explicit residual debt, and dynamic
  characteristic-count interactions remain explicitly outside this trust
  claim.

## Removal condition

Retain this focused capability while the exact grammar, strict operation,
target identity, shared effective ability-fragment applicability, declaration
legality, cleanup, rollback, multiplayer behavior, and replay evidence pass.
Any widening requires the appropriate typed declaration grammar, reference,
duration, or cycle-safe characteristic owner rather than a parallel combat
applicability check.
