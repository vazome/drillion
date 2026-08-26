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
pnpm --dir web check 8765                    # renders all 171 task specs against a running server
```

See the root [README](README.md) for the full architecture and vocabulary, and
[`web/README.md`](web/README.md) for frontend-specific notes.

## Proposing a new task

The most useful contribution to drillion is a new task under `tasks/`. Open an issue with the
**New task** template before writing one — it captures the topic, tags, difficulty and the WHY
block a maintainer needs to say yes before you write code.

## The task-authoring contract

A task is a folder, `tasks/<NNN>_<name>/`, added by appending — never inserting — the next
number after the highest one in the catalogue. Copy the shape of an existing task rather than
starting from scratch. Full detail, including the vocabulary for `tier`, `difficulty`, `track`
and `tags`, is in the README's [Vocabulary](README.md#vocabulary) and
[The tasks](README.md#the-tasks) sections; here is the contract a submission is graded against.

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
reported, so if your new task doesn't show up in the catalogue, `selfcheck`'s count is the first
thing to check.

If the task is adapted from another source (Exercism or elsewhere), say so honestly in a
`source:` frontmatter field and a closing attribution line, and confirm the licence permits it —
see [NOTICE](NOTICE) for how the 84 Exercism-derived tasks already do this.

## Code style

- `ruff` must pass (`uv run ruff check .`); it runs in CI.
- The client's linter must pass (`pnpm --dir web lint`); it runs in CI beside `ruff`. The
  rules are in `web/.oxlintrc.json`, each with the mistake it is there to catch.
- Conventional commit titles, plain language: `fix(web): submission no longer causes crashes`.
- Comments describe how a thing is used, not a line-by-line narration.

## Pull requests

Keep the title short, imperative and focused on user impact — skip `feat:`/`fix:` style prefixes
in the title itself. Describe the change at the top of the PR body and reference the issue it
closes, if any.
