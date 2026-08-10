---
title: "ADR 0053: typed own-graveyard return to hand"
status: "ADR"
authoritative_source: "this decision record and the typed graveyard-return implementation"
verified: "2026-08-10"
audience: "rules, compiler, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0053"
decision_status: "accepted"
date: "2026-08-10"
---

# ADR 0053: typed own-graveyard return to hand

## Context

[ADR 0028](0028-typed-return-to-owner-hand.md) established an
identity-pinned, replacement-aware transaction for returning a battlefield
permanent to its owner's hand. Ordinary recursion such as “Return target card
from your graveyard to your hand” remained a material residual even though its
target zone is public and its result uses the same canonical zone-change owner.

Treating every sentence containing “return” as one operation would erase
material differences in origin zone, target ownership, card predicates,
destination, quantity, and result binding. Keeping a second ad hoc graveyard
move path would instead duplicate identity, replacement, replay, and rollback
semantics.

## Decision

The represented family has one immutable `OwnGraveyardCardTargetSpec`. It
describes exactly one public card in the resolving controller's graveyard and
supports only the closed card-type predicates declared by its typed target
kind. Spell, trigger, and activated parsing lower the same whole-clause grammar
to `return_graveyard_card_to_owner_hand` with a precise source span.

The operation lowers through a dedicated read-only semantic handler and typed
intent. `return_to_hand.py` verifies that the selected object is a physical card
owned by the actor. The shared single-object zone-transition transaction now
pins a typed battlefield or graveyard origin in addition to physical identity,
logical identity, owner, and controller. Battlefield return and permanent exile
continue to require a phased-in battlefield origin; graveyard return requires
the original own-graveyard incarnation. Commit revalidates the entire plan and
delegates the move to the existing replacement-aware zone owner.

## Alternatives

- Reuse the battlefield `bounce` operation with a different target schema.
  Rejected because the operation would no longer declare or enforce its origin
  and object-kind contract.
- Add a generic move-from-zone operation. Rejected because it would create an
  open dictionary language whose accepted runtime behavior exceeds compiler
  evidence.
- Implement individual recursion cards. Rejected because card identity is not
  a rules boundary and the wording is shared across spell, trigger, and
  activated contexts.

## Consequences

- Offer generation, command validation, and resolution share one owner-relative
  graveyard target schema.
- A target that leaves the graveyard and later returns is a new object and the
  prepared transition fails before mutation.
- Tokens, copies that are not cards, and cards in another player's graveyard
  cannot enter this path.
- Destination replacement, logical-incarnation creation, public journaling,
  hidden-hand projection, rollback, and replay remain owned by existing
  canonical boundaries.
- Opponent-graveyard, reanimation, mass, optional, modal, linked-result,
  arbitrary-predicate, library-destination, and compound wording remain precise
  residuals.
- Game Record v3 and the public protocol are unchanged; the new source-pinned
  CardProgram operation participates in the existing semantic-handler
  fingerprint for newly compiled games.

## Removal condition

Replace this boundary only with a typed zone-transition effect model that
preserves exact source grammar, target ownership, object kind, physical and
logical identity, destination replacement, transactional rollback, replay, and
principal-scoped hidden information without reintroducing runtime Oracle
parsing or card-specific dispatch.
