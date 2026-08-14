---
title: "ADR 0066: metadata-only exact-head CI certification reuse"
status: "ADR"
authoritative_source: "PR workflow and exact-head certification receipt"
verified: "2026-08-13"
audience: "CI, release, and architecture contributors"
maintenance: "hand-maintained"
adr_id: "0066"
decision_status: "accepted"
date: "2026-08-13"
---

# ADR 0066: metadata-only exact-head CI certification reuse

## Context

The PR workflow subscribes to description edits so template policy can be
corrected without a source commit. A post-green description edit therefore
started the entire Linux, Windows, package, generated, and browser matrix even
though the exact head and tracked source fingerprint had not changed. Removing
the `edited` event would leave pull-request policy stale; subscribing to
`ready_for_review` would create another metadata-only regression trigger.

## Decision

Plan always validates the current PR body. On `edited` only, it searches for a
live prior PR certification artifact with the same repository, pull request,
exact head, and tracked-source fingerprint. The artifact must parse as the
strict canonical receipt and validate against its publication run. If it does,
the expensive jobs skip and the stable `PR / Certification` job reissues a new
receipt. Any missing, expired, malformed, mismatched, or unavailable evidence
falls back to the full matrix.

Receipt schema 2 distinguishes its publication workflow run from the original
evidence workflow run and records `executed` or `reused` mode. Reuse chains
carry the original matrix run rather than laundering a metadata run into new
test evidence. Open, synchronize, and reopen always execute the matrix. The
workflow remains unsubscribed from `ready_for_review`.

## Alternatives

- Stop validating edited PR descriptions. Rejected because the merge policy
  would accept metadata that was never checked.
- Treat every edit as source impact. Rejected because exact-head certification
  already provides the stronger equivalence boundary.
- Copy the old receipt unchanged. Rejected because its artifact publication run
  would not match and reuse provenance would be ambiguous.

## Consequences

- Description corrections retain a stable required certification context
  without spending the full regression matrix twice.
- Source-changing events cannot use the reuse path.
- Main-smoke continues to verify exact tracked-source equivalence and can audit
  both the current publication run and original evidence run.
- PR bodies should still be final before the first push and should not be edited
  after green merely to replace a pending-CI sentence.

## Removal condition

Remove reuse if GitHub supplies an equivalent native immutable-head evidence
primitive or if branch protection no longer uses `PR / Certification`. Any
replacement must preserve current-body validation, exact-head fail-closed
evidence, and original matrix provenance.
