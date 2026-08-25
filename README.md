# study — spaced-repetition Python drills with a local web UI

A single-user practice tool: a catalogue of small, tagged Python exercises, each graded by its own
pytest test against a reference solution on **fresh random data every sitting**, scheduled by a
5-box Leitner ladder, with gated hints and a gated solution. You open it in a browser, write
`solve()` in the editor, press Run, and the app grades, schedules and archives the attempt.

The exercise files on disk are the source of truth; the app edits only the learner's region of
each file and never writes a file without its spec docstring.

## Quick start

```bash
uv run study                 # start the server on http://127.0.0.1:8765 and open the browser
uv run study selfcheck       # prove every drill passes with its own reference solution
docker compose up            # the same app in a container (drills and progress mounted from ./)
```

Requirements: Python 3.13 and [uv](https://docs.astral.sh/uv/). Docker is optional. The web
frontend (React + Vite) is being built; until `web/dist` exists the server exposes the JSON API only.

## How a session works

1. **Today** shows due reviews first (most overdue first), then up to 2 new topics whose
   prerequisites you have passed. The whole catalogue is open too — the queue is a suggestion.
2. Opening an exercise starts an **attempt** (fresh seed, active-seconds timer that pauses when the
   tab is hidden). The left pane is the spec: `WHY` / `YOU GET` / `YOU RETURN` / exact rules, plus
   READ FIRST links. The right pane is the editor with the stub.
3. **Run** saves your region into the file and runs that file's pytest test with the attempt's
   seed. Failures come back with the assertion lines mapped to editor line numbers.
4. **Hints** unlock one level per 60 active seconds; the **solution** unlocks after 3 attempts and
   10 minutes, and taking it means the pass cannot promote the card.
5. **Pass** → computed grade → card moves on the ladder → your code is archived into
   `progress.json` → the file is reset to the stub, so the next review starts blank.

State lives in `progress.json` (cards, open attempts, log, archived solutions) and is committed
with the repo on purpose: it is your work.

## Why it's built this way

**Fresh data every sitting.** Each exercise ships a generator, so when a topic comes back in 8 days
the IPs, names and numbers are different. You can't recall the answer because that exact answer
never existed. This is the one feature that stops spaced repetition from degrading into memorising
files.

**A 5-box ladder, not a fancy algorithm.** Pass an exercise and it returns in 2 → 4 → 8 → 16 → 28
days. Fail and it drops two boxes instead of resetting, because a lapse here costs 30 minutes, not
5 seconds. Nothing is ever scheduled past a week before the target date.

The obvious choice was FSRS (what Anki uses). Tested it: with default settings a topic you get right
three times comes back in 46 days, then 90 — i.e. after the interview. It's tuned for people
memorising vocabulary over years. Fixed intervals are also the *more* correct choice here: with a
known deadline, the research (Cepeda 2008) puts the optimal gap at 10–20% of the time remaining,
which is a number you can just write down.

**Grades are computed, not self-reported.** First try under par = EASY (+2 boxes). Two tries = PASS
(+1). Slow, or three-plus tries = STRUGGLED (stays put). Looked at the solution = never promotes,
regardless of the tests going green. That last rule is the important one: hint-assisted passes are
how people finish a curriculum and still can't code.

**Hints are gated.** Three levels — a nudge, then a strategy, then the same idea worked through on
*different* data. Levels are 60 s apart because clicking through hints is the best-documented way
to feel productive while learning nothing.

**Reviews come before new material,** capped at 2 new topics a day. Reviews arrive interleaved
rather than blocked — mixing confusable topics is the largest effect in the whole literature
(d ≈ 0.83), and it will feel worse than drilling one thing at a time. That feeling is documented
and wrong.

## Layout

```
src/study/            the application package (`study` console script)
  cli.py              serve (default) | selfcheck; logging
  settings.py         STUDY_ROOT / STUDY_HOST / STUDY_PORT / STUDY_OPEN_BROWSER
  state.py            progress.json load/save (atomic)
  catalogue.py        exercises(): META, HINTS, READ FIRST — parsed with ast, never executed
  region.py           the learner's region: cut/splice/stub/validate/etag, atomic file writes
  scheduler.py        ladder, due/new queue, grading, rescheduling
  attempts.py         open/run/pass/abandon/hint/solution lifecycle, active-seconds timer
  runner.py           pytest subprocess, failure summariser, selfcheck
  api.py              FastAPI JSON API + static frontend, serve()
tests/                unit + ASGI tests (plain pytest, no fixtures)
exercises/            the drills (ex_<topic>_<name>.py) and _lib.py (seeded Random)
web/                  the frontend (React + Vite), served from web/dist
progress.json         your cards, attempts, log and archived solutions
Dockerfile, compose.yaml, .github/workflows/ci.yml
```

## Configuration

| variable | default | meaning |
|---|---|---|
| `STUDY_ROOT` | cwd if it has `exercises/`, else the repo | where `exercises/` and `progress.json` live |
| `STUDY_HOST` | `127.0.0.1` | bind address (`0.0.0.0` inside Docker) |
| `STUDY_PORT` | `8765` | port |
| `STUDY_OPEN_BROWSER` | `1` | open the browser on start (`0` in Docker) |
| `STUDY_SEED` | — | pin the data seed when running a drill by hand |

The server binds to loopback, accepts only `127.0.0.1`/`localhost` host headers, rejects bodies
over 256 KB, and runs exercise code only inside a pytest subprocess with a timeout.

## Development

```bash
uv sync                                      # dependencies (runtime + dev)
uv run pytest tests -q                       # the app's tests
uv run ruff check .                          # lint
uv run study selfcheck                       # every drill green with its reference
uv run pytest exercises/ex_019_counter.py    # one drill by hand (fails with NotImplementedError on a stub)
STUDY_SEED=42 uv run pytest exercises/ex_019_counter.py   # same drill, fixed data
```

CI runs the same three checks on every push. The frontend dev loop (`pnpm --dir web dev` with a
proxy to the API) is documented in `web/` once it lands.

## The exercises

One file per drill, `exercises/ex_<topic>_<name>.py`; copy the shape of an existing one:

- `META` — `topic` (== the number in the filename), `title`, `minutes` (par time), `prereqs`
  (topic numbers that gate it), `tags`; whole-task drills add `practices`
- `solve()` — the stub; its docstring **is** the spec (`WHY` / `YOU GET` / `YOU RETURN` / rules)
- `HINTS` — exactly 3, escalating, the last one worked on different data
- `_gen(r)` — builds inputs from `r` (a seeded `random.Random`)
- `_reference(...)` — the correct implementation; tests compare yours against it
- `test_solve()` — a handful of generated cases, plus fixed canonical cases where they exist

**The region contract.** Everything between `META` and `HINTS` is the learner's: it is the text the
editor shows and the only text a save may replace. `solve` must be the last statement in it; given
code (constants, exception classes, a toy app) goes above `solve`, never below. The machinery
(`_gen`, `_reference`, `test_*`) is never sent to the editor.

**Tags** — one catalogue, no folders:

- *Section*, exactly one, by topic number: `core` (1–17) · `data-structures` (18–25) ·
  `files-text` (26–34) · `stdlib-ops` (35–42) · `errors` (43–47, 81) · `http` (48–53) ·
  `concurrency` (54–56, 94–97) · `testing` (57–61, 98–99) · `packaging` (62–67) · `cloud` (68–72) ·
  `whole-task` (73–80, 82–86, 100–101) · `llm` (88–93)
- *Library*, from the file's imports: `boto3` · `requests` · `langchain` · `fastapi` · `asyncio`
- *Track*: `rsample` (drills built around a RAG take-home, with a `TAKE-HOME:` line in READ FIRST);
  `exercism` (drills adapted from [exercism/python](https://github.com/exercism/python), MIT —
  each carries a `# SOURCE:` line and the Exercism concept slugs as tags; topics 200+)

`focus` in `progress.json` is a single tag that restricts which *new* exercises are offered;
reviews and the open catalogue ignore it.

Sanity check for a new drill: `uv run study selfcheck` splices `_reference` into every file and
runs the tests — it must be green before the drill is trusted.

## Status

Backend, API, catalogue migration and 87 drills are done and tested. In progress: the React
frontend (light + dark), the Exercism-derived drills (batches of concept and practice exercises),
container smoke test.
