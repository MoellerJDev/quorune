---
title: "Compact CI card dependencies"
status: "generated"
authoritative_source: "tests/fixtures/compact-ci-fixtures.json and platform/test-shards.json"
verified: "c88ac6e79b505b19bb0ae0d52f1cf746b9efefef8dae090359fb5bd763344c8b"
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
| Fixture files | 26 |
| Cards | 291 |
| Rulings | 523 |
| Modules inspected | 281 |
| Static requirements | 749 |
| Declared dynamic requirements | 7 |
| Unresolved dynamic sites | 0 |
| Missing cards | 0 |
| Missing deck dependencies | 0 |
| Fixture identity conflicts | 0 |

## Shard closure

| Shard | Modules | Status |
| --- | ---: | --- |
| casting-costs-mana | 34 | closed |
| combat-declarations | 21 | closed |
| compiler-cardprogram | 41 | closed |
| core-domain | 14 | closed |
| counter-continuous-effects | 25 | closed |
| deterministic-game-regressions | 5 | closed |
| events-replacement-zone | 33 | closed |
| generated-validation | 29 | closed |
| main-smoke | 6 | closed |
| multiplayer-commander | 8 | closed |
| nightly-property | 3 | closed |
| server-replay-privacy | 14 | closed |
| state-actions-damage | 17 | closed |
| targets-choices-continuations | 21 | closed |
| triggers-turns-exact-decks | 19 | closed |
| windows-compat | 10 | closed |

The JSON companion contains canonical identities, fixture owners, source
provenance, unresolved dynamics, and exact missing dependencies.
