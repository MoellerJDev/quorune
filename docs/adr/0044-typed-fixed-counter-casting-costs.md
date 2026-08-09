---
title: "ADR 0044: typed fixed counter-placement casting costs"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-09"
audience: "rules, compiler, casting, replay, and architecture maintainers"
maintenance: "hand-maintained"
adr_id: "0044"
decision_status: "accepted"
date: "2026-08-09"
---

# ADR 0044: typed fixed counter-placement casting costs

## Context

Some instant and sorcery spells require their caster to put a fixed number of
counters on a creature they control as an additional cost. Treating the cost
sentence and result sentence as independent compiler nodes can accidentally
offer the represented result without its mandatory cost. Committing counters
through an ordinary resolution effect would also misclassify the placement for
replacement effects and could mutate mana or stack state before an affected
player orders competing replacements.

The family needs one source-spanned compiler production, a closed typed cost
descriptor, identical offer and commit predicates, and a replayable precommit
continuation for the complete cast.

## Decision

Compile exactly one mandatory fixed creature-counter additional-cost sentence
followed by exactly one independently represented instant or sorcery result
clause into one CardProgram V2 node. The node owns an immutable versioned cost
descriptor whose object predicate is a phased-in creature the caster currently
controls. Any other additional-cost grammar residualizes the entire spell;
later clauses are not lowered as independent cost-free actions.

Cast offer generation and commit consume the same descriptor. Commit
revalidates current effective characteristics and uses the canonical counter
placement transaction with `effect_generated=False`. If multiple quantity
replacements apply, the existing priority-action cost continuation rolls back
the provisional cast, issues only the affected caster a replacement-order
choice, and resumes the exact card, payment, counter event, and stack action.
The engine facade remains coordinator rather than counter or cost mutation
owner.

## Alternatives

Runtime Oracle parsing was rejected because it would create a second rules
authority beside CardProgram. Reusing resolution `place_counters` effects was
rejected because effect-only replacements must not apply to costs. Compiling a
supported result after an unsupported cost was rejected because it advertises
an illegal cost-free spell. Card-specific handlers were rejected because the
wording is a reusable casting-cost family.

## Consequences

Represented casts expose only currently payable creature choices, commit the
cost before stack placement, preserve exact rollback and replay, and interact
correctly with all-placement versus effect-only counter replacement. The
compiler can promote every card matching the bounded grammar and represented
result family without knowing card identity.

Optional, variable, alternate, compound, multiple, noncreature, removal,
movement, prohibition, and other additional-cost families remain explicit
residuals. This decision does not complete the CR 601 total-cost algorithm or
aggregate CR 122, 614, or 616 coverage.
