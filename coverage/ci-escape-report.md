---
title: "CI escape report"
status: "generated"
authoritative_source: "platform/ci-escape-source.json"
verified: "864edabb445ff557cb45ffdb955375a0ba719ef402450711854df8356794527c"
audience: "maintainers and contributors"
maintenance: "generated"
---

# CI escape report

This report classifies observed deterministic failures that escaped the local quick gate. Null measurements are unavailable and are never estimated.

## Summary

- Escapes: 19
- Deterministic escapes: 14
- Current missing impact edges: 0
- Known flaky tests: 0
- Average pushes per merged PR: None
- Exact-head pass rate: 1.0
- Average observed critical path: 840.5 seconds
- Average Slot B inactive time: None

## Escapes

| ID | Run | Category | Impact edge | Resolution |
|---|---:|---|---|---|
| `ci-20260804-01` | [30916877307](https://github.com/NullPriority/quorune/actions/runs/30916877307) | `missing_affected_test` | `added` | The fixture was made portable and the compiler family remains explicitly routed to compiler-cardprogram and generated validation. |
| `ci-20260804-02` | [30918937537](https://github.com/NullPriority/quorune/actions/runs/30918937537) | `generated_artifact_drift` | `added` | Platform and coverage sources now select their exact generated freshness checks through the path policy. |
| `ci-20260804-03` | [30930608139](https://github.com/NullPriority/quorune/actions/runs/30930608139) | `source_correctness` | `added` | Protection, compiler, damage, and continuous-effect paths now select every affected functional shard through explicit rules. |
| `ci-20260804-04` | [30931679921](https://github.com/NullPriority/quorune/actions/runs/30931679921) | `source_correctness` | `added` | The exact protection consumers are covered by both replacement and damage shards in the machine-readable policy. |
| `ci-20260804-05` | [30940720886](https://github.com/NullPriority/quorune/actions/runs/30940720886) | `browser_integration` | `not_applicable` | The production auto-pass race was fixed and the public full-browser gate remains authoritative for headless journeys. |
| `ci-20260804-06` | [30952062448](https://github.com/NullPriority/quorune/actions/runs/30952062448) | `flaky_test` | `not_applicable` | The journey now accepts either a form-backed choice or an authoritative immediate-action revision while preserving forced form submission when needed. |
| `ci-20260805-07` | [30974377805](https://github.com/NullPriority/quorune/actions/runs/30974377805) | `flaky_test` | `not_applicable` | The journeys now wait for authoritative projected results across persisted transitions and retain bounded whole-test budgets; both focused witnesses pass headlessly against the CI compact database. |
| `ci-20260805-08` | [30982463835](https://github.com/NullPriority/quorune/actions/runs/30982463835) | `flaky_test` | `not_applicable` | One shared coordinator now advances only the currently authorized server pass until a strategic decision, seat-qualified opportunity, or projected result is reached; the two witnesses pass together in one headless worker against the CI compact database. |
| `ci-20260805-09` | [30988263099](https://github.com/NullPriority/quorune/actions/runs/30988263099) | `flaky_test` | `not_applicable` | Authorized pass submissions are now keyed by decision ID, land confirmation snapshots the hand only after the card is currently playable, and the witness verifies distinct precombat and postcombat main-phase commander offers; both focused journeys passed together headlessly in 27.9 minutes against the CI compact database. |
| `ci-20260805-10` | [30998174979](https://github.com/NullPriority/quorune/actions/runs/30998174979) | `missing_affected_test` | `added` | Both handler inventories now ratchet at nineteen and the handoff links to generated frontier and architecture reports instead of copying grouped numerical metrics. |
| `ci-20260805-11` | [30987626101](https://github.com/NullPriority/quorune/actions/runs/30987626101) | `infrastructure` | `not_applicable` | The provenance-validating nightly mutation-and-soak job now fetches complete history, and the workflow policy test ratchets that exact job boundary. |
| `ci-20260806-12` | [31099433278](https://github.com/NullPriority/quorune/actions/runs/31099433278) | `flaky_test` | `not_applicable` | The seat-opportunity helper now anchors the expected active seat and exact projected phase while its strategic offer settles, preventing the test driver from consuming the opportunity under observation or matching the next player's same-named main phase. |
| `ci-20260806-13` | [31132735817](https://github.com/NullPriority/quorune/actions/runs/31132735817) | `flaky_test` | `not_applicable` | The journey now arms the defender's stop before each preceding turn-transition command, advances only intervening responses, and holds a seat-qualified precombat main phase while its exact land action settles instead of submitting the pass under observation. |
| `ci-20260809-14` | [31260380655](https://github.com/NullPriority/quorune/actions/runs/31260380655) | `generated_artifact_drift` | `added` | A strict ownership manifest now orders all tracked generators, one finalizer writes them to a bounded fixed point, AGENTS.md requires that command before the final commit, and a repository pre-push hook rejects omitted generated changes. |
| `ci-20260810-15` | [31416024863](https://github.com/NullPriority/quorune/actions/runs/31416024863) | `missing_affected_test` | `added` | The Bloodthirst-focused module now verifies exact component registration, while the global trust test checks unique handler identities and the complete family set instead of a maintenance-only total count. |
| `ci-20260811-16` | [31472531758](https://github.com/NullPriority/quorune/actions/runs/31472531758) | `missing_affected_test` | `added` | The canonical compact-CI fixture manifest now includes one generated three-card Amass fixture, token lookup uses the exact Scryfall name, and the full Amass module passes against a freshly built compact database. |
| `ci-20260811-17` | [31483829105](https://github.com/NullPriority/quorune/actions/runs/31483829105) | `missing_affected_test` | `added` | The immediate Echo correction added the two cards to the canonical fixture set. The compact dependency closure now structurally discovers card, Oracle-ID, helper, and deck requirements and blocks pull-request matrices before long shards when the canonical manifest is incomplete. |
| `ci-20260813-18` | [31733942575](https://github.com/NullPriority/quorune/actions/runs/31733942575) | `missing_affected_test` | `added` | The declaration-focused witness now verifies the three exact registered families and their shared capability dependency, the global ratchet includes those families, and AGENTS.md requires that exact global inventory test in any authorized focused check for registration changes. |
| `ci-20260815-19` | [31872123798](https://github.com/NullPriority/quorune/actions/runs/31872123798) | `source_correctness` | `not_applicable` | The regression now asserts exact status and zero material residuals. The path policy already selected compiler-cardprogram, so no missing impact edge existed; the incident remains recorded to prevent stale promotion assertions from being overlooked during focused compiler harvest review. |

## Measurement limitations

- Average pushes per merged PR: GitHub retained workflow runs are not equivalent to pushes, so push counts remain null rather than estimated.
- Slot B inactive time: GitHub Actions does not observe local worktree activity, so this value remains null rather than estimated.
