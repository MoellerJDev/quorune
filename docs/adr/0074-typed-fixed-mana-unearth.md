---
title: "ADR 0074: typed fixed-mana Unearth"
status: "ADR"
authoritative_source: "typed Unearth compiler, activation, zone-replacement, continuous-effect, and delayed-trigger owners"
verified: "2026-08-16"
audience: "rules, compiler, runtime, privacy, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0074"
decision_status: "accepted"
date: "2026-08-16"
---

# ADR 0074: typed fixed-mana Unearth

## Context

Unearth is a graveyard activated ability with several linked consequences. It
uses sorcery timing and an ordinary activation stack object. On resolution the
same card returns to the battlefield, gains haste, receives a delayed exile
trigger for the next end step, and has any earlier battlefield departure
replaced with exile. The leave replacement is mandatory and applies before
another destination replacement controlled by a different player.

Treating the reminder prose as a runtime recipe would duplicate activation,
zone movement, continuous effects, replacement ordering, and delayed triggers.
Granting only Haste or scheduling only the delayed trigger would leave the
mechanic observably incomplete. Returning a card whose other material behavior
is residual could also expose unsupported entry or battlefield behavior.

## Decision

Compile only a complete ordinary `Unearth {fixed ordinary mana}` line. The
source-spanned `OrdinaryUnearthAbilitySpec` carries one closed mana vector,
graveyard zone, and sorcery timing. Its descriptor explicitly requires a
complete-card admission certificate. The generic program compositor emits that
certificate from the same Oracle IR compilation, so runtime can admit a card
without recompiling or consulting Oracle prose. Morph uses the same certificate
because turning a card face up has the same complete-card boundary.

The ordinary activation proposal and commit owners advertise, revalidate, pay,
and place the ability on the stack. Resolution emits one typed `UnearthIntent`.
The Unearth coordinator delegates the graveyard-to-battlefield move to the
canonical zone owner, records a public noncopiable `unearthed` designation,
creates a source-pinned zone-object Haste effect, and schedules an identity-
pinned next-end-step delayed trigger through the existing trigger owner.

While the designated incarnation remains on the battlefield, zone-replacement
discovery contributes one self-replacement that changes every non-exile
destination to exile. The canonical replacement ordering therefore selects it
before competing destination replacements. Any zone change clears the
designation and continuous effect through the zone-object reset boundary. The
delayed trigger checks physical and logical identity and does nothing if the
object is stale or phased out.

Projection exposes only the public designation and resulting battlefield or
zone facts. It does not expose authoritative physical identity. Save/load and
exact Game Record replay use the typed activation, continuous-effect journal,
designation, replacement journal, and delayed-trigger state.

## Alternatives

- Reinterpret Unearth reminder text at activation or resolution. Rejected
  because current-game prose is not behavior authority.
- Move the card immediately as an activated cost. Rejected because Unearth
  uses the stack and may be countered or become stale before resolution.
- Store a private `exile_on_leave` marker and bypass replacements. Rejected
  because replacement ordering, journaling, replay, and competing effects
  belong to the canonical replacement owner.
- Admit every independently exact Unearth line on a partial card. Rejected
  because returning that permanent can immediately expose residual behavior.

## Consequences

- The bounded slice represents 55 Commander-legal fixed ordinary-mana Unearth
  abilities and promotes the 20 cards for which Unearth is the last material
  blocker.
- Countered and stale activations leave the card in its current zone. Control
  change and phasing retain the designation; a new zone incarnation does not.
- Haste, replacement selection, delayed-trigger placement, zone mutation,
  projection, rollback, and replay remain shared owners rather than Unearth
  implementations.
- Variable, hybrid, Phyrexian, snow, and nonmana costs; copied, granted,
  modified, or multiple Unearth instances; multiface cards; and cards with
  other material residuals remain fail closed.

## Removal condition

Retain this boundary while Unearth remains one linked graveyard activation,
battlefield designation, Haste result, leave replacement, and delayed trigger.
A broader graveyard-action subsystem may supersede it only if it preserves the
source-pinned complete-card certificate, ordinary stack timing, canonical
replacement ordering, incarnation isolation, privacy, rollback, and exact
replay.
