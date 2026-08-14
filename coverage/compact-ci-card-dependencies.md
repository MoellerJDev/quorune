---
title: "Compact CI card dependencies"
status: "generated"
authoritative_source: "tests/fixtures/compact-ci-fixtures.json and platform/test-shards.json"
verified: "dd2c03abeee8d3727d95090c2488107d291e779fd62ca0636563e652dc349a64"
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
| Fixture files | 17 |
| Cards | 247 |
| Rulings | 475 |
| Modules inspected | 268 |
| Static requirements | 689 |
| Declared dynamic requirements | 0 |
| Unresolved dynamic sites | 0 |
| Missing cards | 0 |
| Missing deck dependencies | 0 |
| Fixture identity conflicts | 0 |

## Shard closure

| Shard | Modules | Status |
| --- | ---: | --- |
| casting-costs-mana | 33 | closed |
| combat-declarations | 20 | closed |
| compiler-cardprogram | 36 | closed |
| core-domain | 14 | closed |
| counter-continuous-effects | 20 | closed |
| deterministic-game-regressions | 5 | closed |
| events-replacement-zone | 33 | closed |
| generated-validation | 28 | closed |
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
