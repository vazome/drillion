# CI performance review — 2026-09-29

The current pipeline spends roughly seven minutes validating a PR and repeats that work after merge. The largest opportunity is to stop running unrelated checks for every change. Python validation currently determines completion time; browser jobs consume substantial runner time and would become a bottleneck after Python is improved.

This began as a review and handoff. The same worktree now contains the first CI changes based on the findings. The user requested the thermo-nuclear code quality review skill, specifically raised slow README changes and merges, and then emphasized the screen jobs.

## Scope and evidence

- Reviewed checkout: `8bf3a01` on `main`. Worktree: `/home/daniel/github/drillion-ci-review`, branch `docs/ci-performance-review`.
- Read CI, security, release and scorecard workflows, Dockerfile, image smoke script, browser configuration/specs, selfcheck implementation and relevant tests.
- Queried the latest 100 repository Actions runs during this review. That snapshot contained 34 `ci` runs from September 28–29, including one still running. Timing medians below use the 23 successful completed CI runs: 13 PRs, nine pushes and one scheduled run. Failed/cancelled runs are excluded from those medians.
- Read job and step timestamps, nine detailed job logs, PR #309's changed files, and the effective rules on `main`. Only `gate` is a required status check; strict up-to-date status checks are disabled. Squash is the allowed merge method.
- Wall time means run creation to the last completed active job, including queue and orchestration delays. Runner time means the sum of job start-to-completion intervals; it is not an invoice or a claim about billable minutes. Independent jobs overlap.
- Raw API responses and logs remain locally in `/tmp/drillion-ci-audit/`, with the original run snapshots in `/tmp/drillion-ci-runs.json` and `/tmp/drillion-release-runs.json`. These temporary files are optional supporting evidence, not required to understand this document.
- The baseline review used existing run data without executing browsers or local performance benchmarks. Existing CI logs do not provide individual pytest durations, so no particular Python test is claimed to dominate.

## Measurements

| Measurement | Median | Sample |
| --- | ---: | ---: |
| Successful PR wall time | 6m58s | 13 |
| Successful main-push wall time | 6m54s | 9 |
| Successful PR summed runner time | 20m27s | 13 |
| Python `check` job | 6m35s | 23 |
| Image job | 4m17s | 23 |
| Chromium functional/accessibility/screenshots job | 3m34s | 23 |
| Firefox + WebKit job | 3m09s | 23 |
| Chromium all-task render job | 2m09s | 23 |
| Web build/check job | 43s | 23 |

The three browser-job medians sum to about nine runner-minutes per full CI run. They run in parallel after the web job, so their sum is not elapsed waiting time. Python was the last substantive job to finish in all 23 successful runs.

Selected step medians: pytest **4m38s**, checkout selfcheck **1m33s**, Docker build action **1m59s**, image scan **40s**. Browser test steps alone took **2m15s** for Chromium, **2m00s** for Firefox/WebKit, and **56s** for catalogue rendering. Container initialization added a median **28–32s per browser job**, followed by checkout, Python/Node setup, installs and artifact retrieval.

### Concrete README example

[PR #309](https://github.com/vazome/drillion/pull/309) changed `README.md`, `AGENTS.md` and the description in `pyproject.toml`. It was a prose/metadata change, but it was not literally README-only.

- [Successful PR run](https://github.com/vazome/drillion/actions/runs/36502567552): **8m34s**, including **97s before the first job started**.
- [Post-merge run](https://github.com/vazome/drillion/actions/runs/36507457361): **6m55s**.
- [First cancelled attempt](https://github.com/vazome/drillion/actions/runs/36502122702) and [second cancelled attempt](https://github.com/vazome/drillion/actions/runs/36502221760), plus the two runs above: **67m01s summed CI runner time**, excluding the separate security workflows.

Adding README to the existing skip list would help genuinely README-only changes, but would not by itself fix this example because `pyproject.toml` also changed. Avoid claiming otherwise or skipping all package configuration changes as prose.

## Findings

### P1 — One change flag couples unrelated validation

Location: `.github/workflows/ci.yml:24–67`, `:96–97`, `:167–168`, `:239–240`; `tests/test_ci.py:17–38`.

The filter emits only `code=true/false`. A root README change deliberately produces `true`, launching Python, all browser jobs and the image. The fact that README is package metadata justifies checking packaging and relevant documentation contracts; it does not justify re-running every grader and browser interaction. Existing tests explicitly encode this broad behavior.

Replace the all-or-nothing policy with a small, explicit set of check groups: documentation/package checks, Python/curriculum validation, browser coverage and image validation. Keep unknown paths and unavailable diffs conservative. Include backend API, dependency and curriculum changes that genuinely affect the browser; do not equate browser impact solely with `web/` paths. Avoid a generic dependency-graph engine or a growing collection of content-sensitive exceptions.

The existing required `gate` should continue to execute and reject failed/cancelled prerequisites. Do not solve this with workflow-level path skipping: GitHub documents that required checks from a skipped workflow can remain pending. [GitHub guidance](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)

### P1 — Shared browser state forces serialization

Location: `web/playwright.config.ts:7–20`, `:32–48`; `.github/workflows/ci.yml:163–179`.

Every browser invocation shares one mutable server, task tree and progress database, and `workers: 1` applies to the entire suite. Firefox and WebKit are grouped into a single invocation and run sequentially. The matrix already isolates the three jobs, but it does not isolate tests within them.

In the README run, the main accessibility audit took **33.5s Chromium**, **41.8s Firefox**, and **34.3s WebKit**. Firefox/WebKit ran eight tests with one worker, totaling about 1.9 minutes inside Playwright. Each of the three jobs also pays for its own container and environment setup.

Give independent workers or suites isolated application roots, database state and ports, then enable bounded concurrency. Separate genuinely sequential journeys from independent specs; check reset/backup interactions and screenshot output paths as well as database collisions. Increasing workers on the current shared server is not a safe optimization. Splitting every small concern into another CI matrix job would multiply setup overhead.

Retain cross-browser accessibility coverage for relevant UI changes: recent WebKit-specific fixes demonstrate that it detects real regressions. First avoid launching these jobs for unrelated changes, then reduce the latency of necessary runs.

### P2 — Screenshot production is mixed with required functional testing

Location: `web/e2e/screens.spec.ts:1–4`, `:26–150`; `.github/workflows/ci.yml:220–226`.

The screenshot tour states that it is a review aid, not a visual regression test: no baseline images are compared. It took **35.5s** in the README PR run. It is nevertheless part of the required Chromium suite, on PRs, main pushes and scheduled runs.

Extract the valuable assertions (including submission, review, keyboard bindings and protection of checkout state) into required functional tests. Make screenshot capture opt-in for review or explicitly requested visual changes. Do not simply remove the whole spec and lose its behavior coverage. The follow-up test currently depends on state produced by the tour, which must be addressed during separation.

The catalogue render sweep is a separate concern: it navigates all 385 task pages in one test and took about one minute in that run. Retain a full sweep for shared renderer changes and scheduled validation; investigate changed-task coverage for curriculum-only edits without missing shared metadata or rendering dependencies.

### P1 — Whole-catalogue selfcheck extends the critical path after pytest

Location: `.github/workflows/ci.yml:92–93`; `.github/scripts/image-smoke.sh:25–26`; `src/drillion/runner.py:230–279`.

The `check` job runs pytest and then full selfcheck sequentially. The image smoke script independently runs the whole catalogue selfcheck in the packaged product. The checkout selfcheck adds a median 93 seconds after the slowest test stage.

Assess retaining full packaged selfcheck on relevant PRs while moving the additional checkout selfcheck to scheduled validation. The environments differ, so document what coverage would move: checkout/dev dependencies versus the installed production wheel. Keep focused tests of selfcheck itself. Parallelizing the existing commands in a shared checkout is not automatically safe because selfcheck creates temporary files inside task directories.

Add `--durations`/machine-readable timing to pytest before selecting expensive tests for restructuring. It already uses `-n auto`; recommending xdist as though it were absent misses the actual configuration. Existing Helm/SQL/tool integration tests execute real children and deserve profiling, not speculative deletion.

### P2 — Main pushes repeat the entire PR workload

Location: `.github/workflows/ci.yml:3–6`; `.github/workflows/security.yml:6–9`.

Merges launch the same full CI workflow again. This nearly doubles routine validation work across PR and merge events, although those events do not necessarily test identical trees. Cancellation prevents some obsolete work, but cannot recover work already performed.

Define an explicit purpose for post-merge validation: retain meaningful integration/image checks, and move redundant exhaustive sweeps to the scheduled path where appropriate. Do not blindly delete main validation. Strict up-to-date checks are currently disabled, so a PR may merge after its base changes. The release workflow also treats membership in main as evidence of validation rather than explicitly waiting for successful CI on the tagged commit (`release.yml:50–58`); any change to the validation policy must account for that assumption.

### P2 — Docker invalidates its whole runtime stage on every run

Location: `.github/workflows/ci.yml:259–263`; `.github/workflows/release.yml:121–126`; `Dockerfile:33–90`.

`no-cache-filters: runtime` forces the runtime stage to execute again so Debian updates remain fresh. That also repeats Python installation, wheel installation and grader provisioning. The README run spent **30.7s** in the runtime `doctor --fetch` layer and **1m39s** in the full build action.

Use a defined freshness policy for scheduled/release builds and ordinary layer reuse for PR validation. Keep refresh responsibility explicit; do not accidentally freeze OS packages indefinitely. The Dockerfile's tool cache mount also does not by itself provide cross-run persistence: Docker documents that BuildKit cache mounts are not preserved in the GitHub Actions cache by default. [Docker cache documentation](https://docs.docker.com/build/ci/github-actions/cache/)

Prefer fixing invalidation boundaries before adding another cache-restoration mechanism. The image remains the product and must retain packaged validation.

## Recommended order and handoff constraints

1. Implement and test a small change-selection policy, including root documentation versus curriculum README inputs, relevant backend changes, renames/deletions, unknown paths and unavailable diffs. Keep the required gate reliable. Treat `pyproject.toml` conservatively until there is a concrete, simple policy for metadata-only edits.
2. Remove or relocate duplicate checkout selfcheck only after confirming the packaged run covers the intended contract. Profile pytest rather than guessing at individual slow tests.
3. Separate screenshot capture from functional assertions. Isolate browser state and introduce bounded concurrency; preserve cross-browser checks on relevant changes.
4. Clarify post-merge versus nightly responsibilities and release validation assumptions.
5. Improve Docker cache invalidation and measure the effect on real Actions runs.

Record wall time, runner time and queue delay separately before and after changes. Do not promise a specific new CI duration from adding together overlapping stage savings. Aim for documentation changes to finish with only their relevant lightweight checks; first validate that policy against existing documentation and packaging contracts.

Lower priorities: sampled security PR/push workflows had a median wall time around **43s** and are outside the required `gate`. [Release v0.11.2](https://github.com/vazome/drillion/actions/runs/36031850551) completed in **3m09s** using native parallel architecture builds, compared with **12m00s** for [v0.11.1](https://github.com/vazome/drillion/actions/runs/36016838956). Do not optimize the current release as though it still used the older orchestration.

## Changes made after the review

- `.github/scripts/ci-changes.py` now selects documentation, Python, web, browser and image checks. README plus literal `pyproject.toml` metadata edits take a short documentation/package path; dependency and build-setting edits still select the full suite. Missing diffs, scheduled runs and unexpected input select all checks.
- `ci.yml` adds a documentation job for the Docker usage contract and sdist build. It retains the required `gate`, adds pytest duration reporting, and runs the checkout catalogue selfcheck on the nightly schedule while the built image still runs its packaged selfcheck on relevant PRs.
- The image runtime stage is refreshed in scheduled CI and release builds. Ordinary PR and main builds may reuse its cached layers.
- The screenshot tour is tagged `@capture` and excluded from required Chromium checks. Focused required browser specs now cover a passing submission, the git terminal, Vim/Emacs Run shortcuts and scratch-root write isolation. The tour remains available with `pnpm screens:capture` after building the web client.
- Firefox and WebKit now run concurrently inside their existing CI job, each with its own server port, scratch root and test output directory. This avoids another runner and removes their serial dependency; actual speed still needs a live CI measurement.
- Tests cover the real filter script against temporary Git histories, including the README plus metadata case, dependency edits, invalid TOML and missing diffs. Local actionlint, Ruff, targeted Python tests, web lint/unit tests, web build, sdist build and Playwright test listing were run; browser tests themselves were not executed because AGENTS.md requires explicit agreement for browser verification.

Further work needing fresh CI measurements: isolating state per browser test to enable more than one Playwright worker within Chromium, profiling expensive Python tests from the new `--durations` output, and deciding how much post-merge validation can safely move to the nightly schedule given the current non-strict branch rule and release assumption. No push, PR or ruleset change has been made.
