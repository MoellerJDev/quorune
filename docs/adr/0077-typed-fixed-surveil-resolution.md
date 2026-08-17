---
title: "ADR 0077: typed fixed Surveil resolution"
status: "ADR"
authoritative_source: "fixed Surveil compiler, private ordered-partition choice, typed intent continuation, and canonical zone-transition owner"
verified: "2026-08-17"
audience: "rules, compiler, runtime, browser, privacy, replay, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0077"
decision_status: "accepted"
date: "2026-08-17"
---

# ADR 0077: typed fixed Surveil resolution

## Context

The pinned Commander corpus contains one repeated mandatory fixed-count Surveil
instruction across spells, ordinary self-entry triggers, activated abilities,
and independently typed two-clause effects. Scry already owns a private ordered
library partition, while Mill and the canonical zone-transition owner establish
replacement-aware library-to-graveyard movement. Treating Surveil as prose at
runtime would duplicate both boundaries and make hidden Oracle text
behavior-authoritative.

Surveil differs materially from Scry. Selected cards change zones and may be
redirected by destination replacements; retained cards stay hidden and must be
ordered on top; a positive instruction produces a Surveil event even when the
library is empty; and CR 701.25d places event consumers only after the complete
process. A replacement choice may suspend after the private partition, so the
continuation must preserve the exact looked-at incarnations without exposing
authoritative IDs to another principal.

## Decision

Add one reviewed universal semantic operation, `surveil`, for a mandatory
positive fixed-count instruction affecting only the resolving controller.
`compiler/surveil_templates.py` lowers the exact instruction to a source-spanned
typed effect and `library.surveil.fixed_controller` supplies capability closure.

Generalize `LibraryPartitionChoice` so the server issues two named destination
groups and their order semantics. Scry continues to issue `top` and `bottom`
with its historical compatibility hint. Surveil issues `top` and `graveyard`.
The browser renders only those issued groups and does not derive mechanic or
card behavior.

`SurveilChoiceHandler` captures the current top card references plus physical
and logical identities in a private continuation. `SurveilLibraryIntent`
supports the existing semantic replacement-continuation codec. The Surveil
commit owner revalidates the exact library top, sends the selected cards through
one canonical simultaneous destination-replacement zone transaction, applies
the retained top order through the shared library-partition mutation owner, and
then emits `player.surveilled`. Public journaling names only cards whose actual
destination is public.

Surveil-event consumer grammar is not inferred from the emitted event. A card
with an unsupported consumer or sibling remains outside trusted CardProgram
admission. Zero, dynamic, targeted, optional, cost, repeated, copied, granted,
additional-look, and linked-result forms remain material residuals.

## Alternatives

- Reuse `scry` as the operation name with a graveyard flag. Rejected because it
  would make one mechanic identifier mean two different rules actions and blur
  capability, event, replay, and conformance evidence.
- Add a Surveil-specific browser control. Rejected because the ordered
  partition is a generic server-issued choice shape already shared with Scry.
- Commit each selected card as an independent move. Rejected because Surveil
  moves the selected set simultaneously and replacement/APNAP preparation must
  finish before the first mutation.
- Include Surveil-trigger consumers in the same tranche. Rejected because event
  binding is a distinct compiler family; the normalized event can exist while
  unsupported consumer grammar remains fail-closed.

## Consequences

- The governed census promotes a broad fixed Surveil harvest while preserving
  precise residuals for every excluded variant.
- One new reviewed universal operation and choice handler are registered. The
  exact architecture baseline binds only that operation and the typed owners in
  this decision.
- `CommanderEngine` does not grow. The shared partition extraction keeps direct
  writes flat and introduces no unowned mutation, runtime Oracle interpretation,
  card-name branch, Oracle-ID branch, or competing library/zone authority.
- Four-player projection, private replacement choices, rollback, replay,
  compiler and runtime mutation evidence, and fail-closed CardProgram admission
  cover the represented boundary.
- This decision introduces neither a family-specific layer-6 ability-presence
  check nor a dynamic characteristic count. Those cross-cutting boundaries are
  unchanged.

## Removal condition

Remove the architecture exception when universal-operation registration no
longer requires an exact reviewed baseline. Retain the Surveil operation and
owners only while the fixed grammar, controller relation, private identity pin,
simultaneous replacement-aware movement, shared ordered partition, normalized
event timing, rollback, privacy, replay, and fail-closed exclusions remain
enforced. A broader library-inspection family may supersede this operation only
if it preserves those contracts without reintroducing runtime prose or client
legality.
