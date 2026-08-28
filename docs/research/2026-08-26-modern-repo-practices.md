# What a well-run repo has that drillion doesn't

> **Amended 2026-08-28. Read this as a snapshot of 2026-08-26, not as current.** Two days after it
> was written drillion went public under MIT and shipped 0.4.0 to PyPI and GHCR, which invalidates
> §1's verdict ("private and unlicensed") and closes §2.2 outright. The body below is left exactly
> as it was written — no verdict is edited in place — because its value is the reasoning of that
> day. What the pivot broke:
>
> - **Reversed in practice, and now in the tree.** Provenance attestations (`actions/attest` in
>   `release.yml`, `push-to-registry: true`), PyPI publishing with Trusted Publishing
>   (`pypa/gh-action-pypi-publish`, `environment: pypi`, `id-token: write`), the GHCR publish
>   workflow (`release.yml` pushes `ghcr.io/vazome/drillion`), `docker/build-push-action` with
>   buildx and `cache-from/to: type=gha` in `ci.yml` and `security.yml`, and
>   `package-ecosystem: docker` in Dependabot (#115, landed in #120 — the row's premise, "nothing
>   to bump until a major Python or Node release", was disproved by base-image CVEs in the
>   published 0.4.0 image).
> - **CodeQL: reversed, but not by a workflow file.** CodeQL analysis runs through GitHub's
>   **default setup**, configured in repository settings rather than in `.github/workflows/` —
>   default query suite, remote threat model, weekly, over actions, python and
>   javascript-typescript (`gh api repos/vazome/drillion/code-scanning/default-setup` →
>   `"state": "configured"`). Grepping `.github/` for `codeql` finds only
>   `codeql-action/upload-sarif`, which is Trivy's SARIF upload path and is **not** evidence that
>   CodeQL is absent. The row's premise ("unavailable on a private personal repo on Free") died
>   with the visibility flip.
> - **Premise gone, not yet done — open questions now, not settled noes.** SBOM (#125), the
>   OS/Python test matrix (#127), and OpenSSF Scorecard (#126). Each was rejected on a fact about
>   distribution ("nothing is published", "one runner *is* the supported environment") that
>   `pip install drillion` and `docker run ghcr.io/vazome/drillion` have made false.
> - **Still rejected, unchanged, do not re-litigate.** Coverage gates, `.pre-commit-config.yaml`,
>   `.github/CODEOWNERS`, release-please/semantic-release, and required PR reviews on `main`.
>   These were argued on facts the pivot did not touch — one maintainer, no reviewer, no coverage
>   gate to enforce — and those facts still hold.
>
> One row is done rather than reversed: the pull request template, added as
> `.github/pull_request_template.md` in the same change as this note (#132), on the grounds the
> row itself named — an outside PR can now arrive.

Research note, 2026-08-26. Scope: `vazome/drillion` GitHub setup — CI hardening,
dependency automation, supply chain, release/publish, contributor surface.
Every recommendation is judged against AGENTS.md: categorical pragmatism, YAGNI,
"do not introduce machinery because it looks architecturally impressive".

All action versions below were read from the GitHub Releases API on 2026-08-26.

## 1. Verdict

The biggest gap is not CI hardening — it is that drillion is **private and
unlicensed**, which makes value #1 ("Always open source") legally untrue today
and simultaneously locks out every free GitHub security feature, since rulesets,
code scanning, secret scanning, dependency review and free Actions minutes are
all gated on *public*. Second, the CI job is a single unhardened block: no
`permissions`, no `concurrency`, no `timeout-minutes`, it uses `uv sync --frozen`
(which explicitly does **not** verify the lockfile matches `pyproject.toml`), and
it never builds the Dockerfile — the artifact that the "docker run and you're
ready" promise in AGENTS.md depends on. Third, there is zero dependency
automation and the pinned actions are three to five majors stale
(`checkout@v4` vs v7, `setup-uv@v5` vs v10), which for a single maintainer means
either manual bumping forever or silent rot.

## 2. Worth doing

Ordered by value per unit of effort. Items 3–6 are one commit and about fifteen
minutes total; do those first regardless of what is decided about going public.

---

### 2.1 Add a `LICENSE` file

**What it is.** A root `LICENSE` file that GitHub's Licensee detects and shows in
the sidebar.

**What breaks without it, here.** AGENTS.md opens with "Always open source …
Everybody can freely use drillion and contribute." That is currently false as a
matter of law. GitHub states it plainly: "without a license, the default
copyright laws apply, meaning that you retain all rights to your source code and
no one may reproduce, distribute, or create derivative works from your work"
(<https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository>).
A learning platform that people are meant to clone, self-deploy and fork cannot
ship without one. This also affects `tasks/` — 171 practice tasks with no stated
terms.

**Concrete change.** Pick MIT (shortest, matches "everybody can freely use") or
Apache-2.0 (adds a patent grant and an explicit contribution clause, which is the
better default if outside contributors are expected). Then:

```bash
gh repo edit vazome/drillion --description "Spaced-repetition Python practice: pytest-graded tasks on a Leitner ladder, in a browser"
# add the LICENSE file itself via the GitHub "Add file → Create new file →
# type LICENSE" flow, which offers a license template picker, or paste the
# text from https://choosealicense.com/licenses/mit/
```

Detection needs the file at the repo root named `LICENSE`, `LICENSE.txt` or
`LICENSE.md` (same source).

**Effort.** 5 minutes. It is the single highest-value line in this document.

---

### 2.2 Decide whether to make the repo public — it gates half of this list

**What it is.** Repository visibility. Not a "practice", but the precondition for
most of them.

**What breaks without it, here.** On a **Free personal plan, private** repo:

| Feature | Available? | Source |
|---|---|---|
| Rulesets (branch protection) | **No** — "Rulesets are available in public repositories with GitHub Free … and in public and private repositories with Pro, Team, and GitHub Enterprise Cloud" | <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets> |
| Code scanning / CodeQL | **No** — public repos on github.com, or org-owned with GitHub Code Security | <https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning> |
| Secret scanning | **No** — "Public repositories: secret scanning runs automatically for free"; user-owned private repos need GHEC + EMU | <https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning> |
| Dependency review | **No** — public repos on github.com only, on Free | <https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-dependency-review> |
| Artifact attestations | **No** — "If you are on a Free, Pro, or Team plan, artifact attestations are only available for public repositories" | <https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations> |
| Actions minutes | **2,000/month**, vs "GitHub Actions usage is free … for public repositories that use standard GitHub-hosted runners" | <https://docs.github.com/en/billing/concepts/product-billing/github-actions> |
| Dependency graph | Yes (private supported) | <https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-the-dependency-graph> |
| Dependabot version updates | Yes — "All repositories on GitHub" | <https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/about-dependabot-version-updates> |

The 403s the audit saw on rulesets are this, not a bug. Note the Actions billing
line too: the current `on: [push, pull_request]` double-runs every PR branch, and
on a private Free repo that burns a finite budget.

**Concrete change.** `gh repo edit vazome/drillion --visibility public
--accept-visibility-change-consequences`, after the LICENSE lands and after a
`git log -p | grep`-style sweep for anything personal in the 171 task folders.

**Effort.** 5 minutes of typing, one decision. Everything marked *(public only)*
below depends on it.

---

### 2.3 Harden the CI workflow: `permissions`, `concurrency`, `timeout-minutes`, narrower `on:`

**What it is.** Four top-level keys the workflow currently omits.

**What breaks without it, here.** The workflow has no `permissions:` block, so
`GITHUB_TOKEN` runs at the repository default. GitHub's guidance: "It's good
security practice to set the default permission for the GITHUB_TOKEN to read
access only for repository contents. The permissions can then be increased, as
required, for individual jobs"
(<https://docs.github.com/en/actions/reference/security/secure-use>). With no
`concurrency` group, pushing three times to a branch runs three full jobs
including a Node build; `cancel-in-progress: true` kills the stale ones — real
money on a private Free repo, and real wall-clock either way. With no
`timeout-minutes`, a hung `pytest` on the 171-task suite or a wedged `uvicorn` in
`selfcheck` burns the default 360 minutes (six hours) before GitHub cancels it
(<https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax>).
And `on: [push, pull_request]` runs the job twice for every PR opened from a
branch in this repo — once for the branch push, once for the PR.

**Concrete change.** Replace the header of `.github/workflows/ci.yml`:

```yaml
name: ci

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      ...
```

**Effort.** 5 minutes. Zero risk.

---

### 2.4 `uv sync --locked`, not `--frozen`

**What it is.** A one-word change to the existing install step.

**What breaks without it, here.** uv's docs are unambiguous: `--locked` means "if
the lockfile is not up-to-date, uv will raise an error instead of updating the
lockfile", while `--frozen` means "use the lockfile without checking if it is
up-to-date" (<https://docs.astral.sh/uv/concepts/projects/sync/>). Today, editing
a dependency bound in `pyproject.toml` — e.g. bumping `fastapi>=0.141.1` — and
forgetting to re-lock produces a **green CI run** that installed the old
resolution. The Dockerfile then builds from `uv.lock` and gets a different set of
packages than the pyproject claims. uv's own GitHub Actions guide uses
`uv sync --locked` in its example
(<https://docs.astral.sh/uv/guides/integration/github/>).

**Concrete change.**

```yaml
- run: uv sync --locked
```

`uv lock --check` is the standalone equivalent if a separate step is ever wanted;
it is "equivalent to the `--locked` flag for other commands" (same source). Don't
add it — `--locked` on the sync covers it.

**Effort.** 1 minute. This is the highest-value character in the workflow file.

---

### 2.5 `ruff format --check .`

**What it is.** One more line next to the existing `ruff check`.

**What breaks without it, here.** AGENTS.md says "We use `ruff`. Build should not
fail ruff" — but only the linter runs. Formatting drifts silently, and with
171 `tasks/*/task.py` files plus agent-authored diffs, format churn shows up as
noise in every future review. `ruff` is already a dev dependency; there is no new
tool. `ruff format --check` "exits with 0 if successful and no files would be
formatted, 1 if one or more files would need formatting"
(<https://docs.astral.sh/ruff/formatter/>).

**Concrete change.**

```yaml
- run: uv run ruff format --check .
```

Run `uv run ruff format .` once locally first and commit the result, or the first
CI run is a large diff. Watch `tasks/*/task.py` — the learner-owned regions and
the below-marker imports already carry per-file lint ignores; check the formatter
doesn't reflow those in a way that hurts the exercise.

**Effort.** 2 minutes plus one reformat commit.

---

### 2.6 Build the Docker image in CI

**What it is.** One `docker build` step in the existing job.

**What breaks without it, here.** AGENTS.md value #3 is "Local ready … clone the
repo and self-deploy or docker run". The Dockerfile is a multi-stage build
(node:24-slim web build → python:3.13-slim runtime with uv, non-root user,
HEALTHCHECK) and **nothing in CI touches it**. A change to `pyproject.toml`
extras, to the `web/` build output path, to the console-script entry point, or to
the non-root user's permissions breaks the primary distribution channel and CI
stays green. This is the highest-consequence untested surface in the repo.

**Concrete change.** `docker` is preinstalled on `ubuntu-latest`; no buildx, no
registry, no cache config needed.

```yaml
- run: docker build -t drillion:ci .
- run: docker run --rm drillion:ci drillion selfcheck
```

Deliberately *not* `docker/build-push-action` (currently v7.3.0) — that action
earns its keep for multi-platform builds, registry cache and pushes, none of
which apply until there is somewhere to push. Plain `docker build` is the lazy
correct answer here.

**Effort.** 10 minutes, plus ~1–2 minutes of CI time per run.

---

### 2.7 `.github/dependabot.yml`

**What it is.** Native GitHub dependency update PRs. Available on all
repositories including private ones on Free ("Dependabot version updates is
available for … All repositories on GitHub").

**What breaks without it, here.** Three lockfiles (`uv.lock`,
`web/pnpm-lock.yaml`, plus the pinned actions) and one maintainer. Right now the
actions are 3–5 majors behind; that is what "no automation" looks like after a
year. Grouped monthly PRs are the right cadence for a learning tool — not daily
noise. Dependabot already applies "a default cooldown period of 3 days to version
updates, even when `cooldown` is not configured"
(<https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference>),
so a fresh-malware window is handled without extra config.

Ecosystem values, from
<https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories>:
`uv` (uv v0.11, version updates supported), `npm` (pnpm v7–v10 use the `npm`
value — pnpm has no separate value), `github-actions`.

**Concrete change.** `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: monthly
    groups:
      actions:
        patterns: ["*"]

  - package-ecosystem: uv
    directory: /
    schedule:
      interval: monthly
    groups:
      python:
        patterns: ["*"]

  - package-ecosystem: npm
    directory: /web
    schedule:
      interval: monthly
    groups:
      web:
        patterns: ["*"]
```

One grouped PR per ecosystem per month, three review moments a month, CI proves
them. Skip `package-ecosystem: docker` — the Dockerfile pins floating major tags
(`node:24-slim`, `python:3.13-slim`), so there is nothing for Dependabot to bump
until a major changes, which is a decision, not a PR.

**Effort.** 10 minutes.

---

### 2.8 Bump the actions to current majors, then SHA-pin them

**What it is.** Version currency plus immutable references.

**What breaks without it, here.** Current latest majors, checked today:

| Action | In `ci.yml` | Latest | Note |
|---|---|---|---|
| `actions/checkout` | v4 | **v7.0.1** (2026-07-20) | 3 majors behind |
| `actions/setup-node` | v4 | **v7.0.0** (2026-07-14) | 3 majors behind |
| `astral-sh/setup-uv` | v5 | **v10.0.1** (2026-08-14) | 5 majors behind; `enable-cache` now defaults to `auto` (on for GitHub-hosted runners), so the explicit `enable-cache: true` is redundant on v10 |
| `pnpm/setup` | not used | **v2.0.2** (2026-08-09) | see 2.9 |

On SHA-pinning, GitHub is direct: "Pinning an action to a full-length commit SHA
is currently the only way to use an action as an immutable release … Pinning to a
particular SHA helps mitigate the risk of a bad actor adding a backdoor to the
action's repository"
(<https://docs.github.com/en/actions/reference/security/secure-use>). The
repo's Actions settings currently have `allowed_actions: all` and
`sha_pinning_required: false`.

**Judgement:** SHA-pinning is only worth it *because* 2.7 exists. Without
Dependabot, SHA pins are strictly worse than tags — they rot and nobody notices.
With Dependabot, it is free: it rewrites the SHA and the `# vN.N.N` comment for
you. So do these two together, in that order. setup-uv's own README already shows
the pinned form:

```yaml
- uses: astral-sh/setup-uv@20cfd1bf945f4377ade1205e4dbc17946fc9a30d # v10.0.1
```

Don't bother turning on the repo-level `sha_pinning_required` policy — with one
maintainer and one workflow file, the policy enforces a rule against nobody.

**Effort.** 15 minutes for the bump + pin. Test the majors: `setup-uv` v5→v10 and
`setup-node` v4→v7 are five and three majors of breaking changes; read the
release notes rather than assuming.

---

### 2.9 Upgrade pnpm to 11 and cache the pnpm store

**What it is.** A package-manager bump that is also the repo's only real npm
supply-chain control, plus the cache CI currently doesn't have.

**What breaks without it, here.** Two separate problems.

*Supply chain.* `web/` has 11 direct npm dependencies and a large transitive tree
(React 19, Vite 7, CodeMirror, remark). The npm ecosystem's live threat is
malicious versions published and yanked within hours. pnpm 11 defaults
`minimumReleaseAge` to `1440` — "the minimum number of minutes that must pass
after a version is published before pnpm will install it"
(<https://pnpm.io/supply-chain-security>). drillion pins `pnpm@10.17.1` via
`packageManager`, so it gets none of this. This is the one supply-chain measure
on the list that costs a version bump rather than a pipeline. (pnpm latest is
11.24.0 as of today; the same page also documents `trustPolicy: no-downgrade` and
`blockExoticSubdeps` — both cheap one-liners in `web/pnpm-workspace.yaml`, which
already exists.)

*Speed.* The uv cache is enabled; the **pnpm store is not cached at all**. Every
CI run re-downloads the entire `web/` tree.

**Concrete change.** After bumping `packageManager` to `pnpm@11.x`, the
`setup-node` + `corepack enable` + `pnpm install` trio collapses into one step —
this is pnpm's own current CI recommendation
(<https://pnpm.io/continuous-integration>):

```yaml
- uses: pnpm/setup@v2      # v2.0.2
  with:
    runtime: node@24
    cache: true
    package-json-file: web/package.json
    cache-dependency-path: web/pnpm-lock.yaml
- run: pnpm build
  working-directory: web
```

`pnpm/setup@v2` installs pnpm's self-contained binary (verified against the npm
signature), installs the Node runtime itself — replacing `actions/setup-node` —
reads the version from `packageManager`, and runs `pnpm install` automatically.
Note the constraint from its README: **"`pnpm/setup@v2` installs pnpm v11 and
newer only"**; on pnpm 10 you must stay on `pnpm/action-setup` (v6.0.10) or
corepack. So the version bump is the gate.

If the pnpm 11 upgrade turns out to be disruptive, the fallback that still fixes
the caching is `actions/setup-node@v7` with `cache: pnpm` — but its README notes
the "package manager should be pre-installed", so `corepack enable` must still
run first, which is the shape the workflow already has.

Node 24 is the current LTS ("Krypton", 24.19.0), so the existing `node-version:
24` is correct and should stay.

**Effort.** 30–60 minutes, most of it verifying the pnpm 10→11 upgrade against
the CodeMirror/Vite tree. `web/package.json` already sets
`pnpm.onlyBuiltDependencies: [esbuild]`, so the postinstall-script surface is
already minimal — good.

---

### 2.10 One ruleset on `main` *(public only)*

**What it is.** A repository ruleset targeting `main`.

**What breaks without it, here.** With one maintainer and no protection, a
mistaken `git push --force` or a local merge that skipped CI lands directly on
the branch that everyone clones. AGENTS.md already says "Never push directly to
`main`" — a ruleset makes that a property of the repo rather than a note in a
file agents may or may not read. Unavailable while private on Free (see 2.2).

**Concrete change.** Enable exactly three rules on `main`: block force pushes,
block branch deletion, require the `check` status check to pass. Do **not** turn
on "require a pull request before merging" with required approvals — one
maintainer means zero available reviewers, and the rule would only be satisfied
by bypassing it, which trains you to bypass. Status-check-without-PR-requirement
is the version that actually holds.

**Effort.** 10 minutes in Settings → Rules.

---

### 2.11 Repo description, topics, and a task-shaped contributor surface *(at go-public time)*

**What it is.** The metadata and two files that turn "the code is visible" into
"someone can contribute".

**What breaks without it, here.** The repo has no description and no topics.
AGENTS.md value #2 is "Categorical pragmatism … clearly tagging practices with
respective topic names … Transparency is key" — a repo that tags its own tasks
but not itself is inconsistent. And the plausible contribution to drillion is not
a code PR, it is *a new task folder*; without a CONTRIBUTING that says how a
`tasks/` entry is structured (README frontmatter, `task.py`, the learner region
marker, `_lib` imports) and that `uv run drillion selfcheck` must pass, every
outside attempt is a guess.

**Concrete change.**

```bash
gh repo edit vazome/drillion \
  --description "..." \
  --add-topic python --add-topic learning --add-topic spaced-repetition \
  --add-topic fsrs --add-topic self-hosted --add-topic fastapi
```

Then two files. `CONTRIBUTING.md`: how to run `uv sync --locked && uv run pytest`,
the anatomy of a `tasks/` folder, the WHY / YOU GET / YOU RETURN docstring
convention, and the conventional-commit rule already in AGENTS.md. Plus
`.github/ISSUE_TEMPLATE/new-task.yml` — a YAML issue form with fields for topic
tags, difficulty and the business scenario
(<https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository>).
One form, not three. Recognized locations for community health files are "the
`.github` folder, the root of the repository, or the `docs` folder", except issue
templates which "must be in a folder called `.github/ISSUE_TEMPLATE`"
(<https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file>).

**Effort.** 5 minutes for the metadata, 45–60 minutes for CONTRIBUTING + one
issue form. Skip until public — writing a contributor guide for a private repo is
writing for nobody.

## 3. Rejected as overkill

| Practice | Why not here |
|---|---|
| SLSA Build L3 / provenance attestations | Nothing is published, so nothing consumes provenance; also unavailable on Free for private repos (<https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations>). |
| SBOM generation + attestation | `uv.lock` and `web/pnpm-lock.yaml` *are* the bill of materials, and no downstream consumer ingests an SPDX file. |
| release-please / semantic-release / changesets | Version is `0.1.0` and distribution is `git clone`; a git tag is the entire release process a single maintainer needs. |
| PyPI publishing + Trusted Publishing (<https://docs.pypi.org/trusted-publishers/>) | Only earns its keep if `uvx drillion` becomes a supported entry point. Open question, not a default. |
| GHCR container publish workflow | The documented path is clone + `docker build`; a registry adds a tagging scheme, a retention policy and `packages: write` for zero users today. |
| `docker/build-push-action` for the CI build check | Buildx, layer cache and multi-platform are all things a plain `docker build -t drillion:ci .` doesn't need when there is no push. |
| Test matrix (OS × Python × Node) | `requires-python = ">=3.13"`, the Dockerfile pins `python:3.13-slim` and `node:24-slim`. One runner *is* the supported environment; a matrix would test configurations nobody ships. |
| CodeQL / code scanning | Unavailable on a private personal repo on Free, and the threat model is a localhost learning tool with no untrusted network surface. Revisit only if drillion ever runs multi-tenant. |
| Coverage reporting (Codecov / Coveralls) | A solo repo has no coverage gate to enforce and no PR audience to show a delta to; adds a third-party token to a repo that has none. |
| `.pre-commit-config.yaml` | Duplicates `ruff check` and `ruff format` which CI already runs — two places to keep in sync for one person. `uv run ruff format .` before committing is the same result with no config file. |
| `.github/CODEOWNERS` | One owner. The file would say "everything → the person who wrote everything." |
| `CODE_OF_CONDUCT.md` / `SECURITY.md` | Write them when there is a community to govern and a vulnerability to report. GitHub's default templates are one click away then (<https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository>). |
| `.github/PULL_REQUEST_TEMPLATE.md` | Adds ceremony to the maintainer's own PRs before an outside PR has ever arrived. |
| OpenSSF Scorecard / Allstar | Scores a governance surface (multi-maintainer review, branch policies, published artifacts) this repo deliberately doesn't have; optimizing the score would mean building the machinery this document rejects. |
| Renovate | Dependabot handles `uv`, `npm` and `github-actions` natively with no hosting and no config file beyond 20 lines. Renovate wins only for grouped auto-merge policies Dependabot can't express — not a problem drillion has. |
| `package-ecosystem: docker` in Dependabot | Base images are pinned to floating major tags; there is nothing to bump until a major Python or Node release, which is a decision, not a PR. |
| Required PR reviews / required signed commits on `main` | One maintainer, no available reviewer; a rule that can only be satisfied by bypassing it teaches bypassing. |
| Repo-level `sha_pinning_required` Actions policy | Enforces a rule against a population of one, on a single workflow file. |
| Dependency review action, secret scanning push protection | Not config to write — they turn on automatically once the repo is public. Nothing to do but flip visibility. |
| A second `typecheck` CI step | Already covered: `web/package.json` defines `"build": "tsc -b && vite build"`, so the existing `pnpm build` typechecks. |

## 4. Open questions for the maintainer

1. **Is the repo going public, and when?** It gates 2.2, 2.10, 2.11, plus every
   free security feature. Everything else in section 2 is worth doing either way.
2. **Is `git clone` + local `docker build` the permanent distribution story, or
   is PyPI (`uvx drillion`) or GHCR (`docker run ghcr.io/vazome/drillion`)
   intended?** If a registry is ever the answer, the release/publish section of
   this document changes shape entirely — trusted publishing and attestations go
   from "rejected" to "table stakes". Right now they are rejected on the
   assumption that clone-and-build is the only path.
3. **Are outside contributions actually wanted, or is "open source" about the
   license and readability?** These are different projects. The second one needs
   only 2.1; the first needs 2.11 and eventually a CoC.
4. **Is a new `tasks/` folder the expected contribution?** If yes, does
   `uv run drillion selfcheck` already validate a task folder's structure
   (frontmatter, learner region markers, `_lib` imports)? If it does, the
   CONTRIBUTING is short and CI already gates contributions. If it doesn't, that
   check is worth more than anything else in section 2.
5. **Any known blocker to pnpm 10.17.1 → 11.x?** 2.9's supply-chain and CI-speed
   wins both hinge on it, and I could not test the upgrade against the
   CodeMirror/Vite/React 19 tree from here.
