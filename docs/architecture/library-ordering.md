---
title: "Library inspection and ordering"
status: "current"
authoritative_source: "typed library-choice and mutation owners"
verified: "2026-08-09"
audience: "rules, compiler, replay, and browser maintainers"
maintenance: "hand-maintained"
---

# Library inspection and ordering

Quorune represents private library inspection as a typed choice followed by a
separate authoritative mutation. A choice handler may read only the projected
top of the instructed player's library, reveal those identities only to that
player and the analyst record, and issue a strict schema. The response is
revalidated against the exact looked-at identities before any library order is
changed.

## Fixed Scry

`library.scry.fixed_controller` owns one positive fixed-count Scry instruction
for its controller. `LibraryPartitionChoice` requires a complete, duplicate-free
partition of every looked-at card into:

- `top`, ordered from the new top downward; and
- `bottom`, ordered from the new bottom upward.

`ScryArrangement` freezes that response. `commit_scry_arrangement` verifies that
the physical cards are still the current library top, then commits the complete
arrangement with one list mutation. The public event reveals only counts; card
identities and the resulting hidden order remain seat-scoped. Scry 0 and Scry
with an empty library create no Scry event.

The schema retains the historical `destination: library_bottom` hint and the
handler accepts the former bottom-subset response for Game Record v3 command
replay. New clients should use the ordered partition. Runtime code does not
parse Oracle text, and ordinary top-card reordering remains a separate typed
operation rather than a second Scry implementation.

## Deliberate boundary

The current family excludes simultaneous instructions for multiple players,
dynamic counts, effects that add cards while Scrying, Scry-trigger compilation,
Surveil, fateseal, and non-Scry library ordering. In particular, CR 701.22c
requires a future APNAP decision coordinator and simultaneous commit; a normal
four-player game in which one player Scrying has opponents is not that case.

