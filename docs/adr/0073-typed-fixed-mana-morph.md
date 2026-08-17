---
title: "ADR 0073: typed fixed-mana Morph"
status: "ADR"
authoritative_source: "typed Morph compiler, casting proposal, face-down state, and priority special-action owners"
verified: "2026-08-16"
audience: "rules, compiler, runtime, privacy, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0073"
decision_status: "accepted"
date: "2026-08-16"
---

# ADR 0073: typed fixed-mana Morph

## Context

Morph is not only a cost keyword. One printed ability authorizes a card to be
cast as a nameless, colorless, typeless 2/2 creature spell for `{3}`, carries
those copiable values onto the battlefield, keeps the physical identity hidden
from other players, and later authorizes its controller to reveal and pay a
different cost as a special action that does not use the stack.

Treating Morph as an ordinary alternate cost would incorrectly use the
face-up card's type, text, targeting, payment mechanics, and resolution
program. Treating turn face up as an activation would incorrectly create a
stack object and a response window. A face-down flag used only by projection
would leave face-up abilities and characteristics behavior-authoritative.

Megamorph, variable and nonmana costs, other face-down methods, copied objects,
and turn-face-up triggers are separate families. They are not part of this
decision.

## Decision

Compile only one complete ordinary `Morph {fixed ordinary mana}` line into a
source-spanned `FixedManaMorphSpec`. Its registered CardProgram component is
active in all zones and carries the fixed turn-up mana vector; runtime never
parses Oracle prose. Runtime discovery also requires the complete current
card to carry a compiler-pinned complete-card admission certificate, so an
independently exact Morph ability does not make an otherwise residual card
behavior-authoritative. The semantic-program compatibility CardProgram is not
used for this decision because it does not contain the complete Oracle IR
residual inventory.

Casting publishes a second immutable cast offer for the same physical card.
That offer supplies a typed `{3}` base alternative, the face-down `Creature`
spell type, and no printed cost schema or printed payment mechanic. Commander
tax, represented external cost reduction, external Improvise, canonical mana
payment, spell-cast events, and zone replacement continue through their shared
owners. The committed stack item has an identity-free label and a typed
face-down method marker.

The characteristic evaluator applies the marker in copy layer 1b after layer
1a copy values. The represented object has no name, mana cost, text, subtype,
color, or abilities and has creature type and 2/2 power/toughness. The same
logical object and marker survive only the stack-to-battlefield transition.
Projection exposes the physical identity to the controller's authorized view,
keeps it hidden from other seats, and reveals it to every seat when the object
turns face up or leaves the battlefield.

Priority exposes one `turn_face_up` action only for the controller of the same
face-down physical card. Eligibility reconstructs would-be-face-up
characteristics without the Morph layer-1b effect and consumes the shared
effective-keyword query. A represented layer-6 removal of Morph therefore
blocks the action. The action pays the fixed mana vector atomically, ends the
face-down effect through the object-state owner, dispatches a normalized
turned-face-up event, performs state-based actions and waiting triggers, and
returns priority without adding anything to the stack.

Every trusted static CardProgram component is generically inactive while its
source is face down, and printed trigger discovery suppresses a face-down
stack or battlefield source. This is a source-state rule, not a Morph-specific
Oracle or card-identity branch. Broader layer-6 addition/removal applicability
still requires the shared cross-component ability-presence boundary.

## Alternatives

- Add a Morph branch to the ordinary printed-cost parser. Rejected because it
  would retain face-up characteristics and printed cost mechanics.
- Represent turn face up as an activated ability. Rejected because CR 702.37e
  defines a special action with no stack or response window.
- Hide only the projection while leaving face-up characteristics active.
  Rejected because targeting, combat, static abilities, triggers, and costs
  would observe the wrong object.
- Trust all Morph, Megamorph, copy, and type-changing interactions together.
  Rejected because their costs, counter replacement, copiable values, trigger
  timing, and characteristic dependencies require separate typed owners.

## Consequences

- The fixed-mana slice promotes 139 Commander Morph abilities and 37 complete
  cards while the two variable costs, twelve nonmana costs, and cards with
  independently residual turn-up behavior remain fail closed at runtime.
- The same cast and priority catalogs own advertisement and acceptance; stale
  identity, control, affordability, method, CardProgram, and layer-6 ability
  state fail closed before mutation.
- Face-down identity, controller knowledge, public reveal, save/load, and exact
  command replay remain explicit rather than incidental UI behavior.
- Static source suppression is shared by all runtime components, but arbitrary
  static ability addition or removal remains outside trust until components
  consume one common ability-presence/applicability query.
- Dynamic characteristic counts are not used by this contract. Copy,
  type-changing, and dynamic-count interactions named in the capability
  exclusions are not trusted.

## Removal condition

Retain this boundary while face-down casting and turning face up remain linked
typed actions over one logical object. A wider face-down subsystem may
supersede it only if it preserves source-spanned descriptors, copy-layer
characteristics, complete-card trust, offer/commit parity, no-stack semantics,
controller knowledge, public reveal, zone reset, rollback, and exact replay.
