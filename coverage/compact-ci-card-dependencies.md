---
title: "Compact CI card dependencies"
status: "generated"
authoritative_source: "tests/fixtures/compact-ci-fixtures.json and platform/test-shards.json"
verified: "b96484cd6dcff7ecf8f6936d6142833d9c0a01b584317ebba07b6f61dfb950bd"
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
| Fixture files | 10 |
| Cards | 228 |
| Rulings | 468 |
| Modules inspected | 257 |
| Static requirements | 632 |
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
| core-domain | 14 | closed |
| generated-validation | 28 | closed |
| main-smoke | 6 | closed |
| multiplayer-commander | 13 | closed |
| nightly-property | 3 | closed |
| rules-events-replacements | 50 | closed |
| server-replay-privacy | 14 | closed |
| state-actions-damage | 16 | closed |
| targets-choices-continuations | 21 | closed |
| triggers-turns-exact-decks | 18 | closed |
| windows-compat | 10 | closed |

The JSON companion contains canonical identities, fixture owners, source
provenance, unresolved dynamics, and exact missing dependencies.
