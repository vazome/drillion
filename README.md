# drillion — spaced-repetition Python tasks with a local web UI

A single-user practice tool: a catalogue of small, tagged Python tasks, each graded by its own
pytest test against a reference solution on **fresh random data every sitting**, scheduled by a
5-box Leitner ladder, with gated hints and a gated solution. You open it in a browser, write
`solve()` in the editor, press Run, and the app grades, schedules and archives the attempt.

Design brief for the UI: [DESIGN.md](DESIGN.md).

The task files on disk are the source of truth; the app edits only the learner's region of each
`task.py` — everything above its machinery marker — and the guidance beside the editor is the
task's `README.md`, rendered as Markdown.

## Quick start

```bash
uv run drillion              # start the server on http://127.0.0.1:8765 and open the browser
uv run drillion selfcheck    # prove every task passes with its own reference solution
docker compose up            # the same app in a container (tasks and progress mounted from ./)
```

Requirements: Python 3.13 and [uv](https://docs.astral.sh/uv/). Docker is optional. The frontend
(React + Vite, in `web/`) builds itself on start: `uv run drillion` runs `pnpm build` when `web/dist`
is missing or older than anything in `web/src/`, or than `web/package.json`, `web/index.html` or
`web/vite.config.ts`. Without pnpm the JSON API still serves and only `/` 404s.

## How a session works

1. **Today** shows due reviews first (most overdue first), then up to 2 new tasks whose
   prerequisites you have passed. The whole catalogue is open too — the queue is a suggestion.
2. Opening a task starts an **attempt** (fresh seed, active-seconds timer that pauses when the
   tab is hidden). The left pane renders the task's `README.md`: Why / You get / You return /
   Rules / Read first, with code blocks, tables, diagrams and images. The right pane is the editor
   with the stub.
3. **Run** saves your region into the file and runs that file's pytest test with the attempt's
   seed. Failures come back with the assertion lines mapped to editor line numbers.
4. **Hints** unlock one level per 60 active seconds; the **solution** unlocks after 3 attempts and
   10 minutes, and taking it means the pass cannot promote the card.
5. **Pass** → computed grade → card moves on the ladder → your code is archived into
   `progress.json` → the file is reset to the stub, so the next review starts blank.

State lives in `progress.json` (cards, open attempts, log, archived solutions) and is committed
with the repo on purpose: it is your work.

## Why it's built this way

**Fresh data every sitting.** Each task ships a generator, so when a task comes back in 8 days
the IPs, names and numbers are different. You can't recall the answer because that exact answer
never existed. This is the one feature that stops spaced repetition from degrading into memorising
files.

**A 5-box ladder, not a fancy algorithm.** Pass a task and it returns in 2 → 4 → 8 → 16 → 28
days. Only a pass moves a card: a failing run costs an attempt and nothing else, and a pass you
took the solution for grades `struggled`, which leaves the card exactly where it was.

The obvious choice was FSRS (what Anki uses). Tested it: with default settings a task you get right
three times comes back in 46 days, then 90. It's tuned for people memorising vocabulary over years,
where the cost of a lapse is one word. Fixed intervals are the *more* correct choice here: over a
season of practice the research (Cepeda 2008) puts the optimal gap at 10–20% of the retention
interval, which is a number you can just write down.

**Grades are computed, not self-reported.** First try under par = `quick` (+2 boxes). Two tries =
`pass` (+1). Slow, or three-plus tries = `struggled` (stays put). Looked at the solution = never
promotes, regardless of the tests going green. That last rule is the important one: hint-assisted
passes are how people finish a curriculum and still can't code.

**Par time is the grader's, not yours.** `minutes:` lives in each task's frontmatter because
`grade_of()` needs it to decide `quick`, and it stops at the server: it is not in the browser
payload and not on any screen. So the timer counts up and never turns a colour at some number you
were supposed to beat. Watching a clock you cannot meet is not information, it is pressure.

**Hints are gated.** Three levels — a nudge, then a strategy, then the same idea worked through on
*different* data. Levels are 60 s apart because clicking through hints is the best-documented way
to feel productive while learning nothing.

**Reviews come before new material,** capped at 2 new tasks a day. Reviews arrive interleaved
rather than blocked — mixing confusable topics is the largest effect in the whole literature
(d ≈ 0.83), and it will feel worse than drilling one thing at a time. That feeling is documented
and wrong.

## Layout

```
src/drillion/         the application package (`drillion` console script)
  cli.py              serve (default) | selfcheck; logging
  settings.py         DRILLION_ROOT / DRILLION_HOST / DRILLION_PORT / DRILLION_OPEN_BROWSER
  state.py            progress.json load/save (atomic)
  catalogue.py        tasks(): each task's README.md frontmatter, spec and hints
  region.py           the learner's region: cut/splice/stub/validate/etag, atomic file writes
  scheduler.py        ladder, due/new queue, grading, rescheduling
  attempts.py         open/run/pass/abandon/hint/solution lifecycle, active-seconds timer
  runner.py           pytest subprocess, failure summariser, selfcheck
  api.py              FastAPI JSON API + static frontend, serve()
tests/                unit + ASGI tests (plain pytest, no fixtures)
tasks/                one folder per task and _lib.py (seeded Random)
  <NNN>_<name>/
    README.md         frontmatter (title, difficulty, tier, tags, …) + Markdown guidance
    task.py           the learner's region, the machinery marker, the machinery
    assets/           optional images, diagrams and clips the README points at
web/                  the frontend (React + Vite), served from web/dist
progress.json         your cards, attempts, log and archived solutions
Dockerfile, compose.yaml, .github/workflows/ci.yml
```

## Configuration

| variable | default | meaning |
|---|---|---|
| `DRILLION_ROOT` | cwd if it has `tasks/`, else the repo | where `tasks/` and `progress.json` live |
| `DRILLION_HOST` | `127.0.0.1` | bind address (`0.0.0.0` inside Docker) |
| `DRILLION_PORT` | `8765` | port |
| `DRILLION_OPEN_BROWSER` | `1` | open the browser on start (`0` in Docker) |
| `DRILLION_SEED` | — | pin the data seed when running a task by hand |

The server binds to loopback, accepts only `127.0.0.1`/`localhost` host headers, rejects bodies
over 256 KB, and runs task code only inside a pytest subprocess with a timeout.

## Development

```bash
uv sync                                      # dependencies (runtime + dev)
uv run pytest tests -q                       # the app's tests
uv run ruff check .                          # lint
uv run drillion selfcheck                    # every task green with its reference
uv run pytest tasks/018_counter              # one task by hand (NotImplementedError on a stub)
DRILLION_SEED=42 uv run pytest tasks/018_counter   # same task, fixed data
```

And the frontend:

```bash
pnpm --dir web install                       # once
pnpm --dir web dev                           # Vite on 5173, proxying /api to the server on 8765
pnpm --dir web build                         # emits web/dist, which the server serves at /
pnpm --dir web check 8765                    # renders all 171 specs against a running server
```

CI runs ruff, pytest and selfcheck on every push. The rest of the frontend — the vendored design
system, and why there is no Tailwind and no router — is in [`web/README.md`](web/README.md).

## Vocabulary

Every word the code, the API and the UI use is defined in [CONTEXT.md](CONTEXT.md), together with
the synonyms to avoid. This section is the other half: how to **choose** a tier, a difficulty, a
track or a tag when you write a new task.

**task** — the unit: one folder under `tasks/`, one spec, one `solve()`, one test. One noun, used
everywhere: the code, the API, the UI and these docs never reach for a synonym. There are 171.

**tier** — how far into the language a task reaches. Exactly one of three, and the catalogue lists
them in this order:

| tier | what belongs in it | today |
|---|---|---|
| `core` | the language and its standard library, and every coder needs it: syntax, data structures, files and text, errors, `itertools`, `pathlib` | 139 |
| `advanced` | still the standard library, but you can work a long while without it: `asyncio`, concurrency, generators, decorators, closures, `functools` | 17 |
| `packages` | solving it needs something `pip` installs: `requests`, `responses`, `boto3`, `moto`, `pytest`, `fastapi`, `langchain` | 15 |

Tier answers "can I run this with stock Python?", so `packages` wins whenever a task is both — an
`asyncio` task that stands up a FastAPI app to have something to await is `packages`, not
`advanced`. The test is what **the solution** needs: a library the learner's own code imports, or
that the task is plainly about. Imports below the machinery marker are the grader's and do not
count — 14 tasks `import pytest` down there for `pytest.approx` alone and are `core`, while
`084_fixtures` is `packages` because its `@pytest.fixture` is in the learner's region.

**difficulty** — how hard the task is to get **right the first time**: `easy`, `medium` or `hard`.
It is not how long the task takes. Thirty minutes of unsurprising typing is `easy`; six lines you
can only write once you have seen the trick is `hard`. Anchor the call on the task's `## Rules` —
rules are where the traps live — and grade a new task against the rubric all 171 were graded
against: [`docs/difficulty-rubric.md`](docs/difficulty-rubric.md).
Today: 36 easy · 108 medium · 27 hard.

**track** — optional, at most one per task: a themed run through the catalogue that cuts across
tiers. `rsample` (18 tasks) is a RAG take-home broken into steps. Leave the key out unless the task
belongs to such a run.

**tags** — what Python you practise. Lowercase, kebab-case, 1–3 per task, and one rule decides
every one of them:

> A tag names a **Python concept you can practise** — never the task's identity, never its story.

`recursion`, `dict-get`, `context-managers` and `bitwise` are tags: each names something you could
sit down and get better at, and something a *future* task could also be tagged with.
`flatten-array`, `phone-screens` and `take-home-task-2` are not. They name one task and could never
name another, so they are the task's identity wearing a tag's clothes.

A tag on a single task is fine — 37 of the 76 are, because 171 tasks cannot cover every concept
twice. The test is not "does more than one task have it?" but "**could** another task have it?".
That is what makes a tag an answer to *what do I want to practise today*, which is the job it does
in the catalogue filter and in the per-tag coverage table on the progress screen. So reach for an
existing tag before minting a synonym — `sets` not `set`, `strings` not `str-stuff` — and when
nothing fits, name the concept, not the task. `GET /api/catalogue` returns the whole vocabulary
under `tags`.

**grade** — what a pass was worth, computed by `grade_of()` and never self-reported:
`quick` (+2 boxes) · `pass` (+1) · `struggled` (stays put) · `abandoned`.
`easy` is a **difficulty** and never a grade; that word moved when the vocabulary landed.

Six tags were retired to get here. If an old branch or an old note still uses one:

| retired tag | where it went |
|---|---|
| `exercism` | `source:` — provenance is a field, not a concept you can practise (84 tasks carry one) |
| `core`, `data-structures` | `tier:` — the coarse grouping is its own key now |
| `whole-task` | `difficulty:` — it marked size, and size is not difficulty |
| `rsample` | `track:` |
| `basics` | `functions` — the concept the tasks actually taught |

**`focus`** in `progress.json` is a single string, and the scheduler matches it against a task's
**tier, track and tags alike** (`scheduler.py:_facets`): `advanced`, `rsample` and `recursion` are
all valid. It restricts which *new* tasks are offered — reviews and the open catalogue ignore it —
and `POST /api/focus` sets it.

## The tasks

One folder per task, `tasks/<NNN>_<name>/`; copy the shape of an existing one.

`<NNN>` is a contiguous incremental id, `001`–`171`, so the next task you add is `172`. It is an
identity and nothing else: it encodes no difficulty, no section and no provenance — `tier`,
`difficulty` and `source:` carry those. Append, never insert: `prereqs:` and `practices:` point at
these numbers, so renumbering means rewriting other people's frontmatter.

**`README.md`** — YAML frontmatter, then GitHub-flavoured Markdown:

```markdown
---
title: Counter — top N by frequency   # the concept first, then what you build with it
difficulty: medium                    # easy | medium | hard
tier: core                            # core | advanced | packages
track: rsample                         # optional, omit it unless the task is part of a run
minutes: 12                           # par time — the grader's input, never shown to the learner
prereqs: [18]                         # task numbers that gate it; [] when nothing does
tags: [counter, sorted]               # Python concepts, lowercase kebab-case
practices: [19, 22]                   # optional — task numbers this one rehearses
source: exercism/python practice/two-fer (MIT, adapted)   # optional
---
# Counter — top N by frequency
## Why / ## You get / ## You return / ## Rules / ## Read first
## Hints
### Hint 1 … ### Hint 2 … ### Hint 3
```

Write the keys in that order. `title`, `difficulty`, `tier`, `minutes` and `tags` are required.

A folder the catalogue cannot read is **skipped**, not reported: a half-written task must never
break the menu for the other 170. That makes a mistake look like a task that simply is not there,
so check this list first when your new task does not appear —

- a required key missing, empty, or misspelt (`tags: []` counts as missing);
- frontmatter that is not a closed `---` block, or is not valid YAML;
- `task.py` with no machinery marker line, or with no `solve()` as the last statement of the
  learner's region, or that does not parse;
- a hint count that is not **exactly 3** — `### Hint 1`, `### Hint 2`, `### Hint 3` under `## Hints`.

`uv run drillion selfcheck` counts what it found: if it says `170/170` after you added a task, the
task is one of the above. `prereqs:` and `practices:` are lists of task
**numbers**, not slugs. No real task carries all nine keys — the block above shows the order, not a
typical task.

The title leads with the concept, never with a puzzle name: Exercism's `bob` is
`conditionals — classify a message into one of five replies`, and the puzzle name survives in the
slug and in `source:`.

The number is **not** in the frontmatter — it is the folder's leading digits, and the API exposes
it as `topic`. The **spec** is everything from `# title` up to `## Hints`; extra sections
(`## Introduction`, `## Instructions`) may go anywhere before it. Exactly 3 hints, escalating, the last one worked on different data — the server
never sends one the learner has not unlocked. Headings, lists, tables, fenced code, GitHub alerts
(`> [!NOTE]`), Mermaid diagrams, images and muted looping clips from `assets/` all render. For a
task adapted from Exercism the README carries **Exercism's Markdown verbatim** — never trimmed to
make room for ours — plus frontmatter `source:` and a closing attribution line.

**`task.py`** — code only, no docstring spec, no META, no HINTS:

```python
from collections import Counter        # the learner's imports, given code and solve()

def solve(lines, n):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══
from _lib import rng

def _gen(r): ...                        # builds inputs from a seeded random.Random
def _reference(lines, n): ...           # the correct implementation; tests compare yours to it
def test_solve(): ...                   # generated cases, plus canonical ones where they exist
```

**The region contract.** Everything above the marker line is the learner's: it is the text the
editor shows and the only text a save may replace. `solve` is the last statement in it; given code
(constants, exception classes, a toy app) goes above `solve`, never below. The machinery
(`_gen`, `_reference`, `test_*`) is never sent to the editor, and an edit that pastes the marker,
defines `_reference`/`_gen`/`test_*` or names `_reference` is refused.

Sanity check for a new task: `uv run drillion selfcheck` splices `_reference` into every file and
runs the tests — it must be green before the task is trusted.

## Status

Backend, API, the folder-per-task Markdown format, the vocabulary above and all 171 tasks are done
and tested, and the three screens — catalogue, task, progress — are built in light and dark. Not
yet: a container smoke test in CI.
