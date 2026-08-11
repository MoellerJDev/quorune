---
title: "Compact CI card dependencies"
status: "generated"
authoritative_source: "tests/fixtures/compact-ci-fixtures.json and platform/test-shards.json"
verified: "07a0164df9df9b2f6132aacc0aeb2a5491f1e3d24731cc22169585e2dc0c806b"
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
| Fixture files | 9 |
| Cards | 227 |
| Rulings | 467 |
| Modules inspected | 254 |
| Static requirements | 624 |
| Declared dynamic requirements | 0 |
| Unresolved dynamic sites | 0 |
| Missing cards | 0 |
| Missing deck dependencies | 0 |
| Fixture identity conflicts | 0 |

## Shard closure

| Shard | Modules | Status |
| --- | ---: | --- |
| casting-costs-mana | 28 | closed |
| combat-declarations | 20 | closed |
| compiler-cardprogram | 35 | closed |
| core-domain | 13 | closed |
| generated-validation | 28 | closed |
| main-smoke | 6 | closed |
| multiplayer-commander | 13 | closed |
| nightly-property | 3 | closed |
| rules-events-replacements | 50 | closed |
| server-replay-privacy | 14 | closed |
| state-actions-damage | 16 | closed |
| targets-choices-continuations | 20 | closed |
| triggers-turns-exact-decks | 17 | closed |
| windows-compat | 10 | closed |

The JSON companion contains canonical identities, fixture owners, source
provenance, unresolved dynamics, and exact missing dependencies.
