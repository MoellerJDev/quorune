---
title: "ADR 0051: typed ordinary Convoke payment"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-10"
audience: "rules, compiler, casting, replay, and architecture maintainers"
maintenance: "hand-maintained"
adr_id: "0051"
decision_status: "accepted"
date: "2026-08-10"
---

# ADR 0051: typed ordinary Convoke payment

## Context

Convoke changes how a spell's already-determined total cost may be paid. Each
untapped creature the caster controls may be tapped for one generic mana or one
mana of one of that creature's current colors. Correct execution therefore
depends on current layer-derived types and colors, whole-vector mana
affordability, stable object identity, the ordinary mana-source planner, and a
single transactional cast commitment. The legacy engine helper recognized the
keyword from live card metadata and selected the first locally valid colored
assignment, which could reject a globally payable multicolored plan.

## Decision

Compile each exact ordinary printed Convoke instance into a source-spanned
CardProgram and one versioned `ConvokeSpec`. Runtime casting discovers only a
current trusted descriptor for the selected face; live Oracle text and keyword
metadata cannot grant the payment permission.

Represent the announced requirements, selected physical and logical
creatures, derived colored or generic contributions, remaining mana vector,
and deterministic fingerprint in an immutable `ConvokePaymentPlan`. The pure
planner considers the complete remaining vector before accepting a colored
assignment. Offers and submitted commands use that same planner and current
effective-characteristic query. Commit revalidates identity, controller, type,
color, tap state, phasing, plan fingerprint, and proposal references before
spending mana or tapping anything.

Convoke is applied after represented total-cost modifiers. A creature selected
for Convoke is excluded from automatic mana-source activation for the same
spell. The existing mana owner spends the remainder, `tap_state.py` owns each
tap, and the casting transaction owns rollback, stack placement, event
dispatch, privacy, and replay. Multiple ordinary printed instances are
redundant. No new direct `GameState` mutation or card-specific runtime branch
is introduced.

## Alternatives

- Keep Convoke inside `CommanderEngine`. Rejected because it duplicated cost
  planning, characteristic reads, and cast validation.
- Greedily choose a colored contribution for each creature. Rejected because
  local choices can leave an unpayable remainder even when another assignment
  is payable.
- Parse reminder or Oracle text while offering the spell. Rejected because the
  compiler and runtime would become competing rules authorities.
- Ask the client to restate mana payments. Rejected because the server can
  derive and verify the canonical remaining mana vector.

## Consequences

Ordinary printed Convoke now composes with represented static generic
reductions, colored and chosen-X costs, current characteristic changes,
summoning-sick creatures, explicit mana-source exclusion, four-player
projection, rollback, and exact replay. Hybrid, Phyrexian, snow, and broader
cost-modification, restricted-mana, cost-floor, payment-replacement, granted,
removed, or rules-text-equivalent variants remain explicit blockers. This does
not claim complete cost payment, cost modification, mana, Convoke, or CR 601
coverage.

## Removal condition

Retire these boundaries only if a successor preserves face-pinned compilation,
whole-vector affordability, immutable physical and logical selections,
pre-mutation revalidation, canonical mana and tap owners, privacy, rollback,
capability closure, and exact replay without runtime Oracle interpretation.
