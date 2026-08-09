---
title: "ADR 0047: typed zone-object keyword results"
status: "ADR"
authoritative_source: "this decision record"
verified: "2026-08-09"
audience: "rules, compiler, replay, and architecture maintainers"
maintenance: "hand-maintained"
adr_id: "0047"
decision_status: "accepted"
date: "2026-08-09"
---

# ADR 0047: typed zone-object keyword results

## Context

Some resolving instructions place a fixed counter on a target and then grant a
keyword without a turn-bounded duration. Reconstructing that result from Oracle
text at runtime would create a second compiler, while storing display rules text
as executable behavior would bypass typed capability closure. Treating the
grant as until end of turn would be rules-incorrect; attaching it to the source
would also incorrectly remove it when the source leaves.

The family needs one source-spanned compiler production, exact target identity,
printed result order, counter-replacement suspension, a persistent layer-6
result, transactional rollback, private continuation routing, and exact replay.

## Decision

Add the closed universal `grant_zone_object_keyword` semantic operation. Its
strict read-only handler accepts one direct target reference, one represented
keyword, and authoritative resolving-source context, then emits an immutable
typed intent. The rules-layer commit owner creates one replay-pinned continuous
effect locked to the target's physical and current logical battlefield identity.
It persists through cleanup, control change, and source departure, but stops
applying after the target changes zones or logical identity.

The compiler emits this result only as the second instruction of the represented
fixed target counter sequence. Counter placement remains owned by the canonical
replacement-aware transaction, and the later keyword result remains owned by
the continuous-effect journal. Each keyword declares its independent gameplay
capability, so this duration owner does not imply support for arbitrary granted
rules text. Optional, variable, compound, chosen, multi-target, conditional,
temporary, and unrepresented keyword forms remain material residuals.

`grant_zone_object_keyword` is a reviewed universal operation in the ratcheted
architecture baseline. It accepts no callback, arbitrary mutation, runtime
Oracle parser, card identity, hidden-zone query, or transport authority.

## Consequences

The four ordinary Chimera abilities share one generic compiler/runtime family.
Counter replacements may suspend and resume the sequence without duplicating
either result. A failure in the later continuous-effect commit rolls the entire
resolution back. Game Record v3 schemas remain unchanged; exact commands retain
the typed effect and logical identity needed for deterministic replay.

The aggregate continuous-effect, granted-ability, counter, combat, and keyword
families remain incomplete. Adding executable triggered or activated abilities
requires typed ability fragments and discovery integration rather than widening
this operation.

## Alternatives

Runtime Oracle interpretation was rejected because it creates competing
authorities. Reusing the until-end-of-turn grant was rejected because cleanup
would remove a legally persistent effect. Mutating a card's keyword annotation
directly was rejected because it would bypass layers, duration identity, replay,
and canonical mutation ownership. Card-specific Chimera handlers were rejected
because the wording is a reusable rules family.
