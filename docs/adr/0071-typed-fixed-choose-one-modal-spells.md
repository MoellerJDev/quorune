---
title: "ADR 0071: typed fixed Choose one modal spells"
status: "ADR"
authoritative_source: "fixed modal compiler, capability shape, and canonical casting/targeting runtime"
verified: "2026-08-16"
audience: "rules, compiler, casting, targeting, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0071"
decision_status: "accepted"
date: "2026-08-16"
---

# ADR 0071: typed fixed Choose one modal spells

## Context

The casting and targeting runtime already represents selected modes, exposes
mode-specific public target schemas, validates the selected target plan, stores
the mode on the stack item, revalidates that plan on resolution, and appends
only the selected mode's effects. The compiler did not own the ordinary printed
`Choose one —` grammar, so the header and every bullet remained separate
material residuals even when all effects inside the modes were already typed.

Treating those bullets as sequential spell nodes would be incorrect: a modal
spell resolves one announced branch, not all printed alternatives. A broad
modal parser would also overclaim distinct grammars such as choose-two,
repeatable modes, Spree, Escalate, Entwine, and modal nonspell abilities.

## Decision

The compiler accepts one complete instant or sorcery face only when it contains
an exact `Choose one —` header and exactly two or three bullet modes. A closed
named-mode label may precede a bullet body. Every body must compile completely
through an existing typed effect owner, and every mode may have at most the one
target schema already owned by that effect body.

The result is one `spell_ability` node with no top-level effects. Its target
schema contains one required stable mode ID per printed bullet, the mode's exact
effects, its target schema or an explicit empty group list, and its own mechanic
set. The node mechanic set is the modal marker plus the ordered union of branch
mechanics.

The modal capability shape reconstructs each branch independently. It rejects
changed mode counts, missing or renamed modes, empty or malformed effects,
unknown target fields, nested modes, duplicate mechanics, and any mechanic not
covered by the reconstructed child capabilities. Only after every branch closes
does it add `choice.modal.fixed_one` and the exact union of child capabilities.

The existing authoritative casting, target selection, stack, resolution,
rollback, projection, and replay paths remain the runtime owners. Oracle prose
and mode labels are not consulted during execution.

## Alternatives

- Compile each bullet as an ordinary spell node. Rejected because that would
  execute all alternatives and lose the announcement-time modal choice.
- Add a modal resolver to `CommanderEngine`. Rejected because the existing mode
  schema, target-plan, and `mode_effects` path already owns the behavior.
- Infer a branch's capabilities from the top-level mechanic union. Rejected
  because one branch could borrow another branch's mechanics and falsely close.
- Accept every modal header now. Rejected because different selection counts,
  repetition rules, additional costs, and nonspell timing require their own
  typed grammar owners.

## Consequences

- The current pinned Commander corpus has 38 complete ordinary two- or
  three-mode spell faces whose branches all close through existing owners; the
  destruction-selected frontier is harvested through this coherent generic
  boundary rather than one access at a time.
- Mode availability and target legality are derived from each selected branch.
  An invalid mode-target combination rolls back atomically, and a stale sole
  target makes the spell fizzle without executing an unselected sibling mode.
- Focused real-card tests cover target-free, targeted, mass, named, sequence,
  token, counter, draw, life, and characteristic-effect branches, strict
  negative and mutation shapes, four-player projection, rollback, target
  revalidation, selected-only resolution, and exact replay.
- The change adds no engine method, direct state writer, card-identity dispatch,
  or behavior-authoritative runtime Oracle-text access.
- Layer-6 ability addition/removal remains governed by the shared applicability
  query. Dynamic characteristic counts and affected type-changing interactions
  remain outside this trust claim.

## Removal condition

Retain this capability while the exact complete-face grammar, per-branch
mechanics, child capability reconstruction, announcement-time choice, target
validation, selected-only resolution, rollback, mutation, and replay evidence
pass. Widening requires a dedicated owner for the new modal selection or cost
grammar, never relaxation of this fixed Choose one shape.
