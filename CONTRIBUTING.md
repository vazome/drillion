# Contributing to drillion

## Development loop

```bash
uv sync                                      # dependencies (runtime + dev)
uv run drillion                              # serve on http://127.0.0.1:8765, opens the browser
uv run pytest tests -q                       # the app's own tests
uv run ruff check .                          # lint — CI fails if this fails
uv run drillion selfcheck                    # solve every task with its reference; must say 171/171
```

Requirements: Python 3.13 and [uv](https://docs.astral.sh/uv/). The frontend (React + Vite, in
`web/`) builds itself the first time `uv run drillion` runs; without `pnpm` on `PATH` the JSON
API still serves and only `/` 404s. To work on the frontend itself:

```bash
pnpm --dir web install                       # once
pnpm --dir web dev                           # Vite on 5173, proxying /api to the server on 8765
pnpm --dir web lint                          # lint — CI fails if this fails, same as ruff
pnpm --dir web screens                       # Playwright: renders all 171 task pages, photographs the rest
```

## Seeing the client without running it

Every pull request gets a **`client-screenshots`** artifact: the catalogue, a task, that task
after its tests have been run — failed and passed — and the progress page, captured from the
real client talking to the real API. Download it from the run's summary page and look. It is a
review aid, not a visual regression test: nothing is compared against a committed baseline, so
a UI change shows up as a different picture and never as a red build. When a run does fail, a
`client-traces` artifact comes with it; `pnpm --dir web exec playwright show-trace <zip>` replays
it step by step.

To produce the same PNGs locally:

```bash
pnpm --dir web exec playwright install chromium   # once, ~120 MB
pnpm --dir web screens                            # → web/screenshots/, both git-ignored
```

It starts and stops the server itself on port 8766, against a throwaway copy of `tasks/` in
your temp directory — never the checkout, so your own `progress.json` and task files cannot be
touched. The last test in `web/e2e/screens.spec.ts` asserts exactly that. Nothing has to be
running first, and a dev server on 8765 is left alone.

### Screenshots the docs keep

`pnpm screens` output is throwaway. The screenshots the README shows are committed, and live in
`docs/images/`, one light and one dark per screen.

Link them by absolute URL pinned to `main` — never a tag, never a relative path:

```
https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-light.png
```

Two reasons, and both matter. `README.md` is also the PyPI long description, and PyPI resolves
nothing relative, so a relative path is a broken image there. And a screenshot is reshot when it
is worth reshooting, not to match a release: a reader takes the picture as the current one, so
the link should mean the same thing. Pinning a tag would freeze a published page on whatever was
true that day and add a step to the release checklist that would eventually be missed.

The cost is that such a link cannot resolve until the image is on `main`. So land the images
first, in their own pull request, and link them in a second one — then the README renders while
it is still being reviewed, instead of after it is too late to look at.

Quantise to a 256-colour palette before committing — UI screenshots are flat colour, so it is
visually lossless and roughly a third of the bytes. `docs/images` is excluded from the sdist in
`pyproject.toml`; nothing inside the package reads them.

See [CONTEXT.md](CONTEXT.md) for the vocabulary every part of drillion uses, and
[`web/README.md`](web/README.md) for frontend-specific notes.

## Proposing a new task

The most useful contribution to drillion is a new task under `tasks/`. Open an issue with the
**New task** template before writing one — it captures the topic, tags, difficulty and the WHY
block a maintainer needs to say yes before you write code.

## The task-authoring contract

A task is a folder, `tasks/<NNN>_<name>/`, added by appending — never inserting — the next
number after the highest one in the catalogue. Copy the shape of an existing task rather than
starting from scratch. Full detail, including how to choose `tier`, `difficulty`, `track` and
`tags`, is in [docs/authoring-tasks.md](docs/authoring-tasks.md); here is the contract a
submission is graded against.

**`README.md`** — YAML frontmatter (`title`, `difficulty`, `tier`, `minutes` and `tags` are
required; `prereqs`, `practices`, `track`, `source` are optional), then GitHub-flavoured
Markdown that opens with exactly these four headings, in order:

```markdown
## Why
## You get
## You return
## Rules
```

`## Read first` and `## Hints` may follow. **`## Hints` must contain exactly three**
`### Hint` subsections, escalating — a nudge, then a strategy, then the same idea worked
through on different data. The server never sends a hint the learner has not unlocked, so a
wrong count breaks the grading, not just the display.

**`task.py`** — the learner's region (given code, then `solve()` as its last statement), a
machinery marker line, then the machinery: a `_gen` that builds inputs from a seeded
`random.Random`, a `_reference` implementation, and a `test_solve` that compares the two. The
app only ever edits the region above the marker; an edit that pastes the marker, or defines or
names `_reference`/`_gen`/`test_*`, is refused.

**Grading a submission**: `uv run drillion selfcheck` splices each task's own `_reference` into
its stub and runs the test — every task must go green this way before it is trusted, and the
count it prints (`N/N`) is the thing to watch. A folder the catalogue cannot parse (missing
frontmatter key, no machinery marker, a hint count that isn't 3) is silently skipped rather than
reported, so if your new task doesn't show up in the catalogue, run `uv run drillion doctor` — it
names every rule the folder breaks, which `selfcheck` cannot, because it never sees a folder the
catalogue dropped.

If the task is adapted from another source (Exercism or elsewhere), say so honestly in a
`source:` frontmatter field and a closing attribution line, and confirm the licence permits it —
see [NOTICE](NOTICE) for how the 84 Exercism-derived tasks already do this.

## Versioning

drillion is on `0.x`, which means anything may change. `1.0` will be a claim that the
`progress.json` schema has settled, not a badge.

The version is declared in **exactly one place**, `version` in `pyproject.toml`, and bumped by
hand. `drillion --version`, `GET /api/health` and the page's header all read it back from the
installed package metadata, so nothing in the source repeats the number. It is deliberately not
derived from git tags: the container build context carries the source but no git history, so a
VCS-derived version would build as a development placeholder inside the image.

Semantic versioning, defined against drillion's real public surface — the CLI, the HTTP API,
the `progress.json` schema, and the task-folder format:

- **MAJOR** — an existing `progress.json` stops loading or needs migrating, existing task
  folders stop being valid, or a CLI/HTTP contract breaks. A learner's saved progress is the
  thing they cannot afford to lose, so it is the thing MAJOR is about. The schema half of that
  promise is a number in the code and in every file written: `SCHEMA` in
  `src/drillion/state.py`, stamped as `"version"`. A MAJOR is what bumps it, and a build
  refuses a file from a schema above its own rather than rewriting it.
- **MINOR** — new features, new payload fields, new tasks. Task content is content; adding
  drills is not a breaking change.
- **PATCH** — fixes, no new surface.

Releasing: bump `pyproject.toml`, run `uv lock`, add the entry to
[CHANGELOG.md](CHANGELOG.md), merge that to `main`, then `git fetch` and tag
`<remote>/main` **by name**:

```bash
git fetch origin main
git tag -s v<version> origin/main -m "v<version>"
git push origin v<version>
```

`uv.lock` records drillion's own version, so a bump without `uv lock` fails every
`uv sync --locked` in CI — the whole matrix, not one job. Commit the lockfile with the bump.

Never tag a local branch, and never tag the release branch you just merged: a squash merge
rewrites the commit, so that branch's head is not what landed on `main` and the gate will refuse
it. The tag is the whole trigger — the `gate` job fails a tag whose name disagrees with the
declared version, and fails a commit that is not on `main`, because the `main` ruleset is what
proves the commit went green. Past the gate it publishes to PyPI and ghcr and cuts the GitHub
release, with the wheel and sdist attached and the changelog entry verbatim as its notes. A tag
with no matching `## <version>` section in the changelog fails rather than publishing a release
with nothing in it.

When a publish dies for a reason that is not the code — a network blip, a `pypi` approval that
arrives after the job timed out — rerun it from **Actions → release → Run workflow**, choosing the
tag rather than a branch.

Never move a published tag, and note that you could not if you wanted to: the `published version
tags` ruleset makes `refs/tags/v*` immutable with no bypass actors. A tag pushed at the wrong
commit therefore spends that version number for good — the gate refuses to publish it, and it can
neither be deleted nor repointed. Go to the next patch and say so in the changelog, the way 0.4.6
does about 0.4.5.

## Code style

- `ruff` must pass (`uv run ruff check .`); it runs in CI.
- The client's linter must pass (`pnpm --dir web lint`); it runs in CI beside `ruff`. The
  rules are in `web/.oxlintrc.json`, each with the mistake it is there to catch.
- Conventional commit titles, plain language: `fix(web): submission no longer causes crashes`.
- Comments describe how a thing is used, not a line-by-line narration.
- New functionality comes with tests in `tests/`, in the same change. A bug fix comes with
  the test that fails without it. Perfection is not the bar — a change that adds behaviour
  nothing exercises is.

## Pull requests

Keep the title short, imperative and focused on user impact — skip `feat:`/`fix:` style prefixes
in the title itself. Describe the change at the top of the PR body and reference the issue it
closes, if any.
