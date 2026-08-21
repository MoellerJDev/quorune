---
title: "Compact CI card dependencies"
status: "generated"
authoritative_source: "tests/fixtures/compact-ci-fixtures.json and platform/test-shards.json"
verified: "9241250042a1b1d94b394b51f78e88c674930bda2768da6fa4b0b1e80dd7004b"
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
| Modules inspected | 298 |
| Static requirements | 792 |
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
| events-replacement-zone | 35 | closed |
| generated-validation | 29 | closed |
| main-smoke | 6 | closed |
| multiplayer-commander | 8 | closed |
| nightly-property | 3 | closed |
| server-replay-privacy | 14 | closed |
| state-actions-damage | 17 | closed |
| targets-choices-continuations | 23 | closed |
| triggers-turns-exact-decks | 19 | closed |
| windows-compat | 10 | closed |

The JSON companion contains canonical identities, fixture owners, source
provenance, unresolved dynamics, and exact missing dependencies.
