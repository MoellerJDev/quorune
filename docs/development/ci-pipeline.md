---
title: "CI pipeline and two-slot development"
status: "current"
authoritative_source: "GitHub workflows, platform/test-shards.json, and local gate scripts"
verified: "2026-08-09"
audience: "contributors and maintainers"
maintenance: "hand-maintained"
---

# CI pipeline and two-slot development

The repository uses narrow, opt-in local feedback and exact-head public
certification. GitHub Actions is the ordinary broad-test and merge authority.
The workflow never requires a visible browser.

## Two development slots

Keep at most two substantive branches active:

- Slot A is pushed and undergoing pull-request certification.
- Slot B is a separate worktree containing the next independent rules batch.

Create Slot B from current remote `main` while Slot A is running:

```powershell
git fetch origin --prune
git worktree add ..\quorune-next -b <next-branch> origin/main
Set-Location ..\quorune-next
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e . -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts\worktree_bootstrap.py --install-hook `
  --db "C:\path\to\the\pinned\scryfall-current.sqlite3"
```

The readiness command is read-only except for the explicit hook-install mode,
which changes only repository-local Git configuration and refuses to overwrite
a foreign hook policy. Database lookup uses `--db`, `MTG_CARD_DB`, then the
worktree-local `data/scryfall-current.sqlite3`. The command compares that
database with the tracked compiler-corpus snapshot, distinguishes missing,
stale, and invalid inputs, validates primary test-shard ownership, and prints
the exact finalizer command for the detected platform. Run it without
`--install-hook` to recheck an existing worktree.

Never rebase or rewrite Slot A while its exact head is being certified. If its
CI fails, preserve coherent Slot B work, fix Slot A in its own worktree, push a
new immutable head, and let stale runs cancel. After Slot A merges, fetch and
rebase Slot B only when its changes actually overlap the merged work.

Clean up a merged slot only after confirming its pull request and `main` SHA:

```powershell
git fetch origin --prune
git worktree remove <merged-worktree-path>
git branch -d <merged-branch>
git push origin --delete <merged-branch>
```

Do not delete a branch with unique work, an active run, or an unmerged pull
request.

## Local impact inspection

Do not run broad local suites as the ordinary workflow. If feedback is
materially useful, run only the exact new test and smallest adjacent impacted
selection. Before push, inspect what CI will select:

```powershell
.\.venv\Scripts\python.exe scripts/quick_gate.py --dry-run
```

`platform/change-impact-policy.json` is the versioned many-to-many path/check
policy consumed by `scripts/change_impact.py`, `scripts/quick_gate.py`, and
`scripts/ci_plan.py`. It maps normalized paths to the manifest in
`platform/test-shards.json`, generated checks, and platform gates. Internal
rules modules are never classified by generic words such as `action` or
`choice`; browser-facing protocol, projection, action-catalog, choice-form,
server, lifecycle, and persistence paths are explicit. `engine.py` and
`session.py` no longer imply every browser journey by path alone: the typed
subsystem changed alongside them selects any focused public behavior. A
compiler-only change with no browser-facing runtime or schema change therefore
keeps the compact smoke only. For responsibilities still inside the legacy
engine, the planner maps changed Python hunks in both the base and candidate
trees to qualified function owners. Changes to the enumerated priority, yield,
and action-opportunity methods require complete browser E2E; unrelated engine
orchestration does not inherit that cost. Cross-cutting protection and
attachment sources deliberately select compiler, replacement, targeting, and
state-action owners so a source-correctness regression cannot escape through a
single narrow shard. When explicitly executed for diagnosis,
`scripts/quick_gate.py` includes
committed and working-tree changes, validates Python 3.12, compiles Python,
builds the compact card database when necessary, runs directly changed tests
and affected functional shards, and selects relevant generated, architecture,
rules, repository, package, or browser-build checks.

The local quick gate does not run Playwright journeys. Browser-sensitive work
gets generated-type, typecheck, and production-build checks locally; isolated
headless Chromium belongs to CI. Never add a command that opens, focuses, or
navigates the user's browser.

## Generated artifact finalization

The finalizer is development-time certification, not an application runtime
dependency. Neither the server nor browser invokes it. Its purpose is to keep
tracked coverage, architecture, protocol, and status artifacts synchronized
with their authoritative source before Git publishes a commit.

`platform/generated-artifacts.json` is the canonical ownership and dependency
manifest for every tracked generated artifact. Its versioned discovery policy
finds artifacts through generated path prefixes, top-level pinned-rules JSON,
generated-document metadata, explicit binary/report paths, and embedded
third-party generator markers. The completeness validator rejects unowned
discovered artifacts, duplicate owners, repository escapes, missing registered
outputs, registered outputs that are not Git-tracked or independently
discoverable, and dependency cycles before any writer runs.

The manifest does not replace specialized source authorities. Pinned rules
snapshots, browser protocol bindings, durable baseline history, and the public
protocol demo remain deliberate manual or separately generated assets, while
their paths and checks still have one manifest owner. Deterministic Python
reports declare their writer and checker and whether writing is automatic,
database-backed, or a deliberate manual baseline operation. CI and the local
impact plan invoke the same interface. Adding a file below `coverage/` or
`demo/`, a top-level `rules/*.json` file, a generated-status Markdown document,
or a file with a registered generator marker requires adding that output to its
owner in the same change.

Run write mode after the coherent source/test/documentation worktree is complete
and before the final commit; inspect and stage its outputs with the source
change:

```powershell
.\.venv\Scripts\python.exe scripts\finalize_generated.py --write
```

Compiler, capability, CardProgram, and card-support changes require the pinned
database census in the same finalization run:

```powershell
.\.venv\Scripts\python.exe scripts\finalize_generated.py --write --db data\scryfall-current.sqlite3
```

Write mode runs generators in topological order and repeats only changed
generators and their downstream automatic or derived-only consumers until a
bounded pass changes nothing. A requested database-backed corpus rebuild occurs
only on the first pass because the DAG already orders all of its consumers
afterward. It then runs all freshness checks, documentation validation, and
diff hygiene. Pass `--db <path>` or set
`MTG_CARD_DB` when a card-data-backed frontier or full reusable-piece rebuild is
required. The manifest owns the full/Commander Oracle and CardProgram census
before the card-unlock frontier, so the frontier cannot compare current source
against stale status counts. The reusable-piece writer can refresh
architecture-derived delta metadata without rebuilding the pinned corpus.
The automatic `rules-derived` owner rebuilds conformance cases, pinned manifest
hashes, the mechanic registry, and rules/mechanics coverage from authoritative
review overlays and mechanic contracts without downloading or reparsing the
Comprehensive Rules. The rules scheduler and platform status explicitly depend
on that owner, so a rules review or contract edit cannot leave their inputs
stale while the finalizer still reports success.
Performance baselines remain
manual because observed latency is review evidence, not an automatic rewrite.
Use `--check` for read-only diagnosis and in CI; a successful `--write` already
performs that verification, so do not run both commands consecutively.

If a full database-backed write fails at a later registered owner, correct the
source problem and use `--resume-from <generator-id>` only when the correction
cannot affect earlier owners. The canonical coordinator reruns that owner and
all descendants, then performs every normal freshness and policy check. This
avoids repeating the expensive corpus while preserving dependency and final
verification guarantees; do not invoke individual writers by hand. The normal
first run and pre-push hook never use resume mode.

The final verification phase includes the architecture policy validator, not
only generated-file freshness. This closes the failure mode where every report
was current but a new semantic operation, direct write, or oversized boundary
had not been added to the reviewed architecture baseline. Run write mode before
the final commit. A successful write stores a worktree-local receipt in Git
metadata. The pre-push hook verifies that receipt and blocks publication on
either generated drift or architecture-policy failure without repeating the
full corpus when the finalized inputs and outputs are identical.

The worktree readiness command installs and verifies the tracked pre-push hook.
The hook-only installer remains available when repairing an existing setup:

```powershell
.\.venv\Scripts\python.exe scripts\install_dev_hooks.py
```

This is deliberately a pre-push hook, not a pre-commit generator. Derived
changes must be reviewed and committed with their authoritative source, while
database-backed corpus generation is too expensive for every checkpoint
commit. Maintainers and coding agents run the finalizer before the final commit;
the hook accepts an exact receipt or falls back to `--write --fail-on-change`
and rejects publication if any writer still changes the tree. The receipt is
bound to tracked source blobs, every registered output, manifest completeness,
and the selected database file identity. A commit containing the already
finalized bytes preserves the receipt; any later relevant edit invalidates it.
New files intended for that commit must already be Git-tracked or staged when
the finalizer runs so they participate in the source fingerprint.
A configured worktree reports `.githooks` from `git config --get
core.hooksPath`.

The installer sets the local `core.hooksPath` to `.githooks` and refuses to
overwrite another hook policy. The hook is a backstop that uses the
worktree-local Python. It first runs `scripts/test_shards.py validate`, because
an unassigned discovered test module makes PR planning fail before any matrix
job can run. It then automatically uses `data/scryfall-current.sqlite3` when
present (or `MTG_CARD_DB` when set), runs generated write mode, and rejects the
push when generated outputs need a commit. It never amends a commit.
Pull-request CI remains check-only and authoritative.

Keep generated-governance tests tied to identities from the canonical manifest
or registry rather than separately maintained totals or copied identifier sets.
Those literals turn every legitimate promotion into an unrelated CI repair.
Compiler-only tests should construct their input `CardRecord` directly; only
runtime integration tests should require the compact CI card database. When a
database-backed fixture is genuinely required, identify every workflow and
local-gate database builder that consumes it before publishing the branch.

`tests/fixtures/compact-ci-fixtures.json` is the single machine-readable input
set for the shared compact CI database. Every Linux, Windows, generated,
browser, main-smoke, nightly, quick-gate, and local-gate build invokes:

```text
python scripts/build_test_database.py build-ci --output <job-specific-path>
```

`python scripts/build_test_database.py validate-ci` fails when the manifest is
malformed, contains duplicate, missing, escaping, or noncanonical paths, or a
registered consumer reintroduces its own `--fixture` list. Add a required
fixture once to the manifest; all consumers retain isolated output paths while
receiving the same composed card set automatically.

The full `scripts/local_merge_gate.py` is not a default development step. Run a
broad local gate only when the user explicitly asks or while diagnosing a
CI-only/release-critical persistence, replay, privacy, or packaging failure.
Otherwise push the coherent exact head and use the CI window for independent
Slot B work.

## Pull-request certification

`.github/workflows/ci.yml` runs these independent jobs:

- ten balanced Ubuntu functional shards;
- canonical generated-artifact finalization checks from the ownership
  manifest, followed by rules, documentation, repository, and architecture
  validation;
- wheel build and clean-install verification;
- a focused Windows compatibility overlay for ordinary changes;
- for platform-sensitive changes or the `windows-full` label, all eleven
  authoritative primary shards on isolated Windows runners and Python
  processes, with `fail-fast: false`, at most five concurrent workers,
  per-shard compact databases and runtime roots, and no shared writable state;
- one separate Windows wheel build and clean-install verification, followed by
  `PR / Windows Certification`, which fails closed on the wrong mode, missing,
  skipped, failed, duplicate, or zero-test shard results, a manifest partition
  gap, or package failure;
- browser build plus a compact authoritative four-context lifecycle smoke;
- focused `mana-action`, `combat`, or `turn-draw` Playwright journeys selected
  by the affected typed rules owner (or the matching `browser-*` label);
- three deterministic complete Playwright groups for browser, protocol, projection,
  reconnect, room, WebSocket, lifecycle, persistence, browser-facing choice or
  action schema changes, workflow changes, natural-winner critical rules, or
  the `browser-full` label. The nonempty `lifecycle`, `rules`, and `soak`
  groups use distinct ports, runtime directories, and SQLite databases.

The compact smoke is the bounded reconnect/lifecycle journey: it starts the
real server, creates four seat-isolated tabs, validates private hands, submits
accepted mulligan commands including an exact retry, survives pause/resume and
reconnect, and closes every context. It does not play a natural game to a
winner. Natural completion remains in the `soak` group and runs when browser,
persistence, replay, Commander-damage, combat-completion, state-based-loss, or
workflow ownership changes. Focused journey tags are closed policy values in
`platform/change-impact-policy.json`; adding an arbitrary test title cannot
silently expand or bypass the gate.

The final `PR / Certification` job receives the stable Windows certification
result and every other required job through `needs`, and fails unless all
succeeded. Protect `main` with the exact required status context
`PR / Certification`. After verifying those dependencies, the job publishes an
untracked `exact-head-certification-<run-id>` artifact. Its strict receipt pins
the repository, pull request, exact PR-head SHA, workflow run, complete required
check suite, fingerprint algorithm, and tracked source-tree fingerprint. It
does not contain or predict the eventual merge SHA.

The pre-sharding public baseline is run `31025126367`: its single Windows
discovery process executed the complete test allocation in 2,265.245 seconds
(37 minutes, 45.245 seconds) before reporting the already-corrected
generated-audit drift.
Use the exact-head matrix metrics—not that historical total—to decide whether
the five-runner ceiling or shard allocation should change.

Do not use `gh pr merge --auto` until branch protection is confirmed. Without a
required check, GitHub may merge immediately while jobs are still running.
Once protection is active, auto-merge is safe only for the immutable SHA whose
certification is in progress.

The nonblocking metrics job records observed queue, job, step, and critical-path
durations plus Playwright journey duration, status, retries, failure class,
browser-context count, accepted command count, authoritative/projected
revisions, and measured persistence/review time. It also reports each Windows
shard's queue, setup, test and total duration, executed test count, the one-time
package duration, the Windows critical path, and actual overlapping test-runner
concurrency. Raw JSON reports and the combined `ci-metrics` artifact are
retained for 14 days so future shard changes use measured history. Cache-hit
rate, agent idle time, and stale-run cancellation remain `null` when GitHub
does not expose measured data; the reporting code never estimates them as
observations.

Long browser journeys use one shared progress driver rather than nested timeout
loops. It observes the decision ID, phase/step, active and priority players,
view/state revisions, accepted command and event counts, latest event, actor
queue, and pending persistence. Ninety seconds without a real change fails with
a compact snapshot and exact one-test rerun command. Ordinary command
acknowledgements still wait for authoritative durability, while review artifacts
remain derived and are generated only for paused or terminal records.

`platform/readiness-source.json` contains durable product and certification
policy only. Pull-request numbers, exact heads, workflow runs, merge SHAs,
runtime branches, and transient integration chronology belong to GitHub and the
untracked certification receipt. The generated readiness report fingerprints
its actual source, package, stable test-shard inventory, rules, and CardProgram
inputs. Exact tracked-source equivalence belongs only to the certification
receipt and main-smoke verification. Environment-sensitive executed-test totals
remain CI metrics rather than tracked readiness state.

Deterministic failures that escape the quick gate are recorded in
`platform/ci-escape-source.json`. The generated
`coverage/ci-escape-report.json` and `.md` classify each failure, its direct
regression, and the impact-edge disposition. Push counts and Slot B idle time
remain null when they cannot be observed; workflow-run counts are not relabeled
as pushes.

## Pull-request description gate

`PR / Plan` runs `scripts/validate_pr_body.py` before change-impact planning or
any expensive matrix job. It reads the pull-request event payload without a
GitHub API call and fails deterministically when the tracked template is still
untouched, a required section or evidence result is blank, an N/A has no
reason, or a safety assertion remains unchecked. Editing the description
restarts the gate, so a contributor can correct metadata without changing the
certified source tree.

Generated work named in the description must cite the canonical
`scripts/finalize_generated.py --write` command. A claimed broad local pass
must include its exact command and numeric result. A claimed broad CI pass must
link the authoritative GitHub Actions run; before that run exists, state that
required exact-head CI is pending rather than predicting its outcome.

The same gate compares the candidate versions of
`platform/readiness-source.json` and
`platform/architecture-audit-source.json` with the pull request's base. Newly
written PR numbers, branch coordinates, workflow runs, exact heads, or merge
SHAs fail closed. Unchanged historical content is not reinterpreted, and
`platform/ci-escape-source.json` remains the intentional durable ledger for
observed CI incidents.

## Main and nightly assurance

`.github/workflows/main-smoke.yml` runs after each push to `main`. It checks a
compact replay/server suite, generated integration state, pinned rules, wheel
metadata, and the production browser build. It is an integration alarm, not a
second complete pre-merge suite. Before those checks, it resolves the pull
request associated with the current merge commit, finds a successful PR workflow
for that exact head, downloads its live certification receipt, and requires the
current tracked source tree to have the same fingerprint. A squash merge passes
without a follow-up status commit because commit identity is deliberately not
the equivalence boundary; a materially different tree, missing/stale receipt,
failed gate, direct push, or mismatched GitHub coordinate fails closed.

`.github/workflows/nightly.yml` owns expensive breadth:

- complete deterministic Python suites on Ubuntu and Windows;
- all three isolated headless Chromium groups, including the natural-winner
  soak;
- at least 100,000 deterministic property transitions across parallel jobs;
- focused implementation mutations, natural-winner/persistence soak, and
  performance/repository checks;
- current Scryfall ingestion and full/Commander Oracle and CardProgram
  censuses as artifacts;
- Python and npm dependency audits.

Nightly failures are real regressions or assurance debt. Fix them on a focused
branch; do not weaken the nightly budget to make a failure disappear.

## Headless browser commands

The public workflow is authoritative, but a focused local reproduction may be
run headlessly after assigning isolated paths and ports. None of these commands
opens a visible browser or HTML report:

```powershell
$env:MTG_CARD_DB = "data/test-ci-smoke.sqlite3"
$env:MTG_E2E_SERVER_PORT = "18081"
$env:MTG_E2E_WEB_PORT = "15171"
$env:MTG_E2E_RUNTIME_DIR = "../local/playwright-smoke"
$env:MTG_PLAYWRIGHT_JSON = "../local/playwright-smoke.json"
npm run e2e:smoke --prefix web

Set-Location web
npx playwright test --grep "@browser-lifecycle"
npx playwright test --grep "@browser-rules"
npx playwright test --grep "@browser-soak"
```

Use different database, runtime, and port values when groups run concurrently.
On failure, prefer the exact `--grep` command printed by the progress diagnostic.

## Shard maintenance

Every `tests/test_*.py` module belongs to exactly one primary shard in
`platform/test-shards.json`. Overlay suites such as `main-smoke`,
`windows-compat`, and `nightly-property` may intentionally reuse modules.

Before the final commit and push, validate ownership after adding, renaming, or
deleting a test module:

```powershell
.\.venv\Scripts\python.exe scripts/test_shards.py validate
```

Every primary shard is directly reproducible on Windows and can write the same
compact result record consumed by public certification and metrics:

```powershell
.\.venv\Scripts\python.exe scripts/test_shards.py run core-domain `
  --result-json local/windows-results/core-domain.json
```

`generated-validation` is a primary shard, not a second full-discovery pass.
The complete Windows matrix therefore executes every discovered test module
exactly once. `windows-compat` remains an intentionally overlapping focused
suite and never runs alongside the full matrix.

Keep functional shard weights close enough to use parallel capacity. Split by
coherent subsystem ownership, not by individual test methods. The generated
inventory shard is separate because thousands of small generated cases have a
different runtime profile from behavioral tests.

## Recovery and inspection

Inspect current repository activity without opening a browser:

```powershell
gh pr list --state open --limit 50
gh run list --limit 20
gh run view <run-id> --json status,conclusion,headSha,url
gh run view <run-id> --json jobs --jq '.jobs[] | {name,status,conclusion}'
```

If the stable certification context is missing, first inspect the workflow job
graph and `scripts/verify_ci_needs.py`. If the quick gate selects an unexpected
surface, add a deterministic classifier regression before changing the mapping.
Never bypass a failing required check or represent unavailable CI metrics as
observed values.
