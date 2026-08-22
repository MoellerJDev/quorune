---
title: "Compact CI card dependencies"
status: "generated"
authoritative_source: "tests/fixtures/compact-ci-fixtures.json and platform/test-shards.json"
verified: "30ac08a5fa583a874ba833593c26485b072152b8c6ba1af9022c9f994b4beb43"
audience: "maintainers and contributors"
maintenance: "generated"
---

# Compact CI card dependencies

This report measures whether every test module assigned to a compact-card
database shard has a statically discovered or explicitly declared card and
deck dependency that resolves through the canonical fixture manifest.

Overall closure: **closed**.

| Measure | Value |
| --- | ---: |
| Fixture files | 32 |
| Cards | 391 |
| Rulings | 727 |
| Modules inspected | 301 |
| Static requirements | 796 |
| Declared dynamic requirements | 8 |
| Unresolved dynamic sites | 0 |
| Missing cards | 0 |
| Missing deck dependencies | 0 |
| Fixture identity conflicts | 0 |

## Shard closure

| Shard | Modules | Status |
| --- | ---: | --- |
| casting-costs-mana | 41 | closed |
| combat-declarations | 21 | closed |
| compiler-cardprogram | 46 | closed |
| core-domain | 14 | closed |
| counter-continuous-effects | 26 | closed |
| deterministic-game-regressions | 5 | closed |
| events-replacement-zone | 36 | closed |
| generated-validation | 30 | closed |
| main-smoke | 6 | closed |
| multiplayer-commander | 9 | closed |
| nightly-property | 3 | closed |
| server-replay-privacy | 14 | closed |
| state-actions-damage | 17 | closed |
| targets-choices-continuations | 23 | closed |
| triggers-turns-exact-decks | 19 | closed |
| windows-compat | 10 | closed |

The JSON companion contains canonical identities, fixture owners, source
provenance, unresolved dynamics, and exact missing dependencies.
