# Study UI: one tagged catalogue + HackerRank-style web app

## Context

`study.py` is a CLI spaced-repetition runner over `exercises/ex_*.py` (79 drills) and a second,
duplicated folder `rsample_drill/` (18 drills, 10 of them copies) selected with `STUDY_DIR=...`.
Daniel wants:

- **No folder-per-track.** One catalogue; tracks/topics are tags in `META`.
- **Zero launch friction.** One command opens a browser; write `solve()` there, press Run, see
  results, hints, timer, progress. No pytest flags, no env vars, no VS Code required.
- **HackerRank feel.** Catalogue with tag filters + status, exercise page with spec + editor +
  results, Today queue, progress dashboard. "Beautiful" — and **no hacker aesthetic**.
- **Modern rich frontend framework** (Daniel, 2026-08-25: "we must use modern rich framework of
  course"), engaging, with **light and dark modes**. Vanilla-JS decision below is superseded.

Decisions taken with Daniel (2026-08-25):
1. Code is written **in the browser** (CodeMirror 6). The exercise file on disk stays the source of
   truth — the server splices the editor's region back into it.
2. **Open catalogue + Today queue.** Any exercise runnable any time; the Leitner pick is a suggestion.
   Grading/rescheduling rules unchanged.
3. **Reviews start from a blank stub.** Implemented as: **the file returns to the stub the moment
   you pass** (solution archived first), so the file is a stub whenever no attempt is open and a
   review can never show you last time's code.
4. Design choices go through the `frontend-design:frontend-design` skill; no black-and-green /
   neon / terminal look. **Daniel runs `/design` (Claude Design) himself before Task 6**; its
   tokens/components replace or extend `design-brief.md` and must cover light **and** dark.
5. (2026-08-25) Frontend = **React 19 + TypeScript + Vite + Tailwind v4 + shadcn/ui**, editor =
   **CodeMirror 6 via `@uiw/react-codemirror`** (bundled, no esm.sh). See "Research" below.

Standing instruction: subagents run as Opus 5 / high effort; Fable is the final reviewer gate.
Reviewed by a Fable 5 subagent on 2026-08-25; its findings are folded in below.
Phase B (after this plan): convert a curated set of Exercism Python exercises into this format.

## Global constraints (binding for every task; reviewers copy this block)

- Python 3.13 via `uv`. The only new Python dependency is `uvicorn` (dev group). Frontend is a
  Vite project in `web/` (Node 24 + pnpm present on the box; `web/pnpm-lock.yaml` committed,
  `web/dist` and `web/node_modules` git-ignored). `uv run study.py` builds `web/dist` when it is
  missing or older than `web/src`/`package.json` (`pnpm install --frozen-lockfile && pnpm build`),
  then serves it. No templating library.
- An exercise file is **never** written without `solve`'s docstring (assert on the output before
  `os.replace`). `_reference`, `_gen`, `test_*` are never sent to the editor; the solution is
  returned only by the gated `solution` endpoint.
- The server process never `exec`s or imports exercise code; tests run only in a pytest subprocess.
- File writes are atomic (`.tmp` + `os.replace`); every write carries an etag check (409 on
  mismatch); one `threading.Lock` serialises read→validate→write→`save()` on the server.
- Server binds `127.0.0.1` only, `TrustedHostMiddleware(allowed_hosts=["127.0.0.1","localhost"])`,
  request bodies > 256 KB rejected, slugs only ever index the catalogue dict (404 otherwise).
- `progress.json` lives at the repo root, is tracked in git, and has exactly the shape in "State".
- Grading rules are unchanged: `grade_of`, `reschedule`, `LADDER`, `NEW_PER_DAY`, hint spacing
  (60 s × level), solution gate (3 attempts and 600 active seconds), `INTERVIEW` cutoff.
- Style: minimal code, stdlib first, fewest files; no speculative abstractions. Every non-trivial
  function has a pytest test in `test_study.py` (plain functions, no fixtures/frameworks).
  `uv run ruff check .` clean. Deliberate shortcuts carry a `# ponytail:` comment naming the ceiling.
- Git: work on branch `study-ui`; one commit per task (more if natural); commit messages end with
  `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. Never push.
- UI: no hacker/terminal aesthetic (no black-and-green, no neon); follow the design brief.

## Inventory facts the plan relies on (verified twice, by AST, on all 97 files)

- `exercises/`: 79 files; `rsample_drill/`: 17 `ex_*.py` + `skipped_ex_03_regex.py` (hidden copy of
  ex_029 with its own READ FIRST links). All 97 parse; pytest collects 97 tests (`ex_14_fixtures`
  has 2 and puts `@pytest.fixture` on `solve`). No `async def solve`, no multi-line signatures.
- META keys: `topic, title, tier, minutes, prereqs` (+ `practices` on 16). `tier` is read by nothing.
  Every file has 3 `HINTS`, a `_reference(`, a solve docstring, and `solve` is the **last statement**
  between `META` and `HINTS` (97/97). 7 files have *given* code above `solve` in that region
  (ex_036 `TRUTHY`, ex_039, ex_044 exception classes, ex_081, ex_092, rsample ex_14, ex_15).
- Copies differ from originals only by a `# READ FIRST:` block, local topic numbers 1–18, emptied
  prereqs — and Daniel's work in 3: `ex_01_sortkey` solved, `ex_02_sets` solved, `ex_04_typehints`
  partial (+ hoisted `Callable`/`get_type_hints` imports, which are a spoiler for that exercise).
  Mapping: 01→ex_009, 02→ex_022, 03→ex_029, 04→ex_016, 05→ex_012, 06→ex_013, 07→ex_055,
  08→ex_056, 13→ex_059, 17→ex_061. Originals: 09, 10, 11, 12, 14, 15, 16, 18.
- `rsample_drill/progress.json`: 2 seen cards (both overdue), 2 log entries, `current`=ex_04.
  No root `progress.json`. Checkpoint commit `67d64f5` tracks everything (branch `study-ui`).
- `ex_070_ebscleanup.py` has `topic: 72` **on purpose** (its docstring says why) → rename the file,
  not the topic. `ex_048`/`ex_050` legitimately contain a second `NotImplementedError` (in an `except`).
- Current `exercises()` execs every file (0.88 s, imports moto/langchain into the runner). `ast`
  parse + `literal_eval` of META/HINTS: 0.06 s, works 97/97.
- Installed: fastapi 0.141, starlette, httpx, pytest, pytest-timeout. Missing: **uvicorn**.
  FastAPI JSON endpoints reject non-JSON content types (422). WSL2: `explorer.exe` exists,
  `$BROWSER` unset. Ports 8000/8765 free.

## Research (2026-08-25, so we don't reinvent the wheel)

Existing platforms checked: **Exercism** (CLI + exercism.org; the website is open source but a full
Rails/PostgreSQL/Sidekiq stack, no local single-user mode; we already reuse its *exercises*),
**INGInious** (self-hosted autograder: Python + Docker + MongoDB, course/LTI oriented — far heavier
than a laptop tool, no spaced repetition), **pytest-web / pytest-commander** (local web runners for
pytest suites — a runner UI, no exercise/spec/hint/scheduling model), **Trane / InterviewTraner**
(deliberate-practice engine with prerequisite graph + spaced repetition — Rust, its own content
format, no code grading), **Anki/FSRS** (scheduling only; `py-fsrs` is the algorithm we could swap
for the Leitner ladder later), **nbgrader/JupyterLab** (notebook autograding, classroom model).
Conclusion: nothing combines *local files as source of truth + pytest grading + Leitner review +
gated hints* in a small footprint; build the thin app, but reuse every component:
- Framework: **React 19 + Vite + TypeScript** (largest ecosystem, shadcn/ui and every editor
  wrapper target it first; Svelte 5 would be lighter but has thinner kit/editor wrappers).
- UI kit: **Tailwind v4 + shadcn/ui** (accessible Radix primitives, first-class light/dark via
  `ThemeProvider` + `.dark` class, tokens as CSS variables — `/design` output maps 1:1).
- Editor: **CodeMirror 6** via `@uiw/react-codemirror` (+ `@uiw/codemirror-themes` for a custom
  light/dark theme from the tokens, `@codemirror/lang-python`). Monaco rejected: 2–5 MB, worker
  setup, IntelliSense we don't need; CM6 is what react.dev/Observable/Prisma Studio embed.
- Data: **TanStack Query** (cache, invalidation after run/pass, mutation ordering). Router:
  **react-router** hash routes (no server fallback needed). Theme: `next-themes`-style provider
  from the shadcn Vite recipe (system/light/dark, persisted).
- Scheduler stays our Leitner ladder; `py-fsrs` noted as the upgrade path.

## Architecture

```
uv run study               → serve: uvicorn on STUDY_HOST:STUDY_PORT (127.0.0.1:8765), opens browser
uv run study selfcheck     → every exercise passes with its reference solution ("test it all works")
docker compose up          → same app in a container; exercises/ + progress.json mounted from the host

pyproject.toml   [project.scripts] study = "study.cli:main"; runtime deps in [project.dependencies]
src/study/       the application package (Task 9 — production layout)
  cli.py         argparse: serve (default) | selfcheck; logging setup
  settings.py    Settings from env: root, host, port, open_browser (stdlib dataclass)
  state.py       load/save progress.json (atomic), today(), card()
  catalogue.py   exercises() (ast), read_first(), has_given()
  region.py      bounds/cut/splice/strip_spec/merge_spec/stub/validate/etag/write_region, Invalid
  scheduler.py   LADDER/INTERVIEW/NEW_PER_DAY, due_today/unseen/queue/grade_of/reschedule
  attempts.py    touch/open_attempt/record_pass/abandon/next_hint/unlock_solution, Gated, _solution
  runner.py      run_tests(), summarise(), selfcheck()
  api.py         FastAPI app (routes, lock, middleware) + StaticFiles(web/dist); serve()
tests/           test_region.py, test_catalogue.py, test_scheduler.py, test_attempts.py,
                 test_runner.py, test_api.py  (plain pytest functions, no fixtures)
web/             Vite + React 19 + TS + Tailwind v4 + shadcn/ui (Task 6)
Dockerfile, compose.yaml, .dockerignore, .github/workflows/ci.yml
```
`study.cli` is the only place that imports `study.api` (lazily, for `serve`). The old CLI
`next/check/hint/status` and `STUDY_DIR` switching stay deleted. Content (`exercises/`, `_lib.py`,
`progress.json`) lives under `settings.root`, never inside the package.

### Catalogue (ast, no exec, no cache) — `study.exercises()`
For each `exercises/ex_*.py`: `ast.parse`; META/HINTS via `literal_eval` of the top-level assigns;
`read_first` = the consecutive `#` comment block after the module docstring (skip blank lines
first; first line must start with `# READ FIRST`, prefix match; return the lines with the leading
`#` and one space stripped); `region_start` (= META end line + 1) and `hints_line` from the AST.
A file that fails to parse **or** lacks META/HINTS/`solve` is skipped (one `try` per file; never
crash the menu). `tags = META.get("tags", [])`. Re-parse per request (0.06 s) — no cache.

### Region + splice (pure functions in `study.py`)
```
bounds(src)  → meta_end (end_lineno of top-level META assign), hints_start (lineno of HINTS)
cut(src)     → head=lines[:meta_end], mid=lines[meta_end:hints_start-1], tail=lines[hints_start-1:]
               lead/trail = blank lines at the ends of mid (preserved verbatim), body = mid.strip("\n")
splice(src, body)  = head + lead + body.strip("\n") + trail + tail        # splice(src, cut(src).body) == src  (97/97)
strip_spec(body)   → editor text without solve's docstring, spec_src (verbatim lines), spec_text
                     (inspect.cleandoc), doc_offset. solve = last top-level (Async)FunctionDef named
                     solve; decorators ride along untouched.
merge_spec(edited, spec_src) → parse edited; b0 = solve.body[0]; pre = line[b0.lineno][:b0.col_offset];
                     reject if pre.strip() ("put solve()'s body on its own line" — catches one-liners
                     AND `def solve(\n x,\n): return x`); drop b0 if it is a string (docstring pasted
                     back); insert spec lines re-indented as pre + line[4:]  (2-space / tab bodies work).
stub(body)   → keep everything before solve (imports, given code, decorators) + signature +
               docstring, replace the rest with `<pre>raise NotImplementedError`.
               Positional rule; identity on every pristine file.
```
**Write gate** (`validate(edited, spec_src, disk_src)`, any failure raises `Invalid(msg, line, col)`):
parse ok → exactly one top-level `def solve` → no top-level `_reference/_gen/META/HINTS/test_*`
and no `Name` `_reference` anywhere in the region → non-empty → `merge_spec` →
`ast.get_docstring(solve)` on the **output** is not None → `new_src = splice(...)` parses,
`bounds(new_src)` ok, `"def _reference(" in new_src` → return `new_src`. Writer does the atomic
write. Etag = `sha256(disk_body)[:12]` where disk_body is `cut(disk_src).body`.

### State — `progress.json` (root, **tracked in git** — it now holds your solutions)
```jsonc
{ "focus": null,                                   // tag restricting NEW picks (replaces STUDY_DIR)
  "cards":   {slug: {box, due, seen}},                              // solution_shown moves to the attempt
  "open":    {slug: {seed, attempts, hints, new, started, last, active, solution_shown}},
  "log":     [{date, slug, grade, attempts, secs, new}],
  "archive": {slug: [{date, grade, code}]} }                        // uncapped; editor text only
```
`save()` stays (atomic). **Timer = active seconds**: every server touch (open/save/run/hint/
heartbeat) does `o.active += min(now - o.last, 120); o.last = now` (`touch(o)`). The page sends a
heartbeat every 60 s while visible. `grade_of`, hint spacing and the solution gate (3 attempts +
600 active s) all use `active`. Seed is generated on first open and **kept until pass**.
`started`/`last` are ISO timestamps (`datetime.now().isoformat()`).

### Scheduler (kept, small edits)
`due_today/unseen/pick/grade_of/reschedule` stay. `unseen` hoists `by_topic` out of the loop;
when `focus` is set it only offers exercises with that tag **and ignores prereqs whose exercise
lacks the tag** (otherwise the rsample track stalls at ex_012 whose prereq 8 isn't rsample).
`queue(st, exs)` → `{review: [...due, most overdue first], new: [next NEW_PER_DAY - done_today by
lowest topic, excluding slugs with an open attempt], done_today}`.

### Attempt lifecycle (functions in `study.py`, called by `web.py`)
- **open(st, slug)**: if no attempt → create `{seed: randint(1000,9999), started=last=now,
  active=0, attempts=0, hints=0, solution_shown=False, new: card.seen==0}`. The file is already a
  stub (invariant), nothing is written. If an attempt exists → `touch` it.
- **save/run**: `validate`; `run` saves first, then `run_tests`. A syntax/gate error is a 400 from
  the save step and **does not count as an attempt**. Attempts increment only when pytest ran.
- **pass**: `grade_of(attempts, active, minutes, solution_shown)` → `reschedule` → `seen+=1` → log →
  `archive[slug].append({date, grade, code: editor text})` → **write `stub(body)` to disk** →
  delete `open[slug]` → respond with grade, next due, the passing code and the new etag.
- **abandon(st, slug, etag)**: archive the disk body as `{grade:"abandoned"}` (only if it differs
  from the stub), write the stub, delete the attempt.
- **archive visibility**: `code` is included in GET only when `seen>0` and either (no attempt is
  open and the card is not due) or (an attempt is open and the solution gate is unlocked). A due
  review therefore never shows last time's answer.
- **hint(st, slug)**: level = o.hints; if level >= 3 → 423 (hints exhausted; use solution);
  if level > 0 and o.active < 60*(level+1) → 423 `{wait_secs}`; else o.hints += 1, return text.
- **solution(st, slug)**: unlocked iff attempts >= 3 and active >= 600; then set
  `o.solution_shown = True` and return `_solution(path)` (existing function).

### API (`web.py`)
| method/path | body | returns | mutates |
|---|---|---|---|
| GET `/api/catalogue` | — | `{focus, tags:[all tags sorted], today:{review:[slug], new:[slug], done_today}, stats:{boxes:[5], due, seen, total, days_left}, exercises:[{slug,topic,title,minutes,tags,prereqs,practices,status:new\|due\|scheduled\|open\|done,box,due,seen}]}` | no |
| POST `/api/ex/{slug}/open` | — | exercise payload | creates attempt |
| GET `/api/ex/{slug}` | — | `{slug, meta, spec, read_first, code, etag, has_given, doc_offset, region_start, hints_line, attempt:{attempts,hints,active,seed,solution_shown} or null, hints:{total,shown:[texts so far],next_in}, solution:{unlocked,need_attempts,need_secs}, archive:[{date,grade,code?}]}` | no |
| PUT `/api/ex/{slug}` | `{code, etag}` | `{etag}` / 400 `{error,line,col}` / 409 `{etag,code}` | file |
| POST `/api/ex/{slug}/run` | `{code, etag}` | `{passed, attempts, headline:[..], output, etag}` + on pass `{grade, box, due_in, code}` | yes + file |
| POST `/api/ex/{slug}/touch` | — | `{active}` | yes (heartbeat) |
| POST `/api/ex/{slug}/hint` | — | `{level,total,text}` / 423 `{wait_secs}` | yes |
| POST `/api/ex/{slug}/solution` | — | `{code}` / 423 `{need_attempts,need_secs}` | yes |
| POST `/api/ex/{slug}/abandon` | `{etag}` | exercise payload | yes + file |
| POST `/api/focus` | `{tag\|null}` | `{focus}` | yes |
| GET `/api/progress` | — | `{boxes, due, seen, total, log:[last 30], per_tag:{tag:{seen,total}}}` | no |

`status` per exercise: `open` if an attempt exists; else `due` if seen>0 and due<=today; else
`done` if seen>0 (scheduled — expose `due`); else `new`. `has_given` = any non-import statement
before `solve` in the region. `run` is a sync `def` (threadpooled). `run_tests(path, seed)` gains
`cwd=ROOT`, `timeout=60`, `-p no:cacheprovider`. `summarise(out, region_start, doc_offset,
hints_line)` (pure): headline = `E   ` lines (max 6) else `FAILED/ERROR` lines; `file.py:NN`
remapped to editor lines **only for NN inside `[region_start, hints_line)`**; output tail 8 KB.
Static mount `/` **after** all API routes.

### Frontend (`web/` — Vite + React 19 + TypeScript + Tailwind v4 + shadcn/ui)
- Project: `web/package.json` (pnpm), `vite.config.ts` (`server.proxy['/api'] → http://127.0.0.1:8765`,
  `build.outDir = dist`), `src/main.tsx`, `src/api.ts` (typed fetch helpers + TanStack Query
  hooks, one `ApiError` carrying status + body), `src/routes/{Catalogue,Exercise,Progress}.tsx`,
  `src/components/` (shadcn/ui generated components + `Editor.tsx`, `Ladder.tsx`, `ResultsPanel.tsx`,
  `TagChips.tsx`, `ThemeToggle.tsx`), `src/theme.ts` (CodeMirror light/dark themes from the tokens).
- Routes (react-router, hash): `#/` catalogue + Today, `#/ex/:slug`, `#/progress`.
- **Light and dark modes** (system default, toggle in the header, persisted) — every component and
  the editor theme switch together; tokens from `/design` / `design-brief.md` as CSS variables on
  `:root` and `.dark`.
- Catalogue: search box, tag chips (multi-select AND), status filter, rows: topic · title · tags ·
  minutes · status pill · mini ladder. Today panel on top: due reviews, then new picks, focus
  select ("Focus: all / rsample / exercism / …" → POST /api/focus; when focus has nothing new left,
  say so + clear).
- Exercise page (HackerRank layout, resizable split): left = title, tags, READ FIRST links
  (+ TAKE-HOME line), spec as `<pre>` (hand-formatted text, `spec-key` highlight for WHY/YOU GET/
  YOU RETURN), given-code note when `has_given`; right = CodeMirror (python, `indentUnit` 4 spaces,
  `Mod-Enter` runs, `indentWithTab`), toolbar: Run · timer (server `active` + local elapsed since
  last response, paused while hidden; amber at `minutes`, red at 2×) · attempts · seed · hint
  button with countdown · solution button (locked text until unlocked) · abandon · archive.
  Results panel: headline lines + collapsible full output; pass state shows the grade line
  (`EASY · 4m12s · 1 attempt · box 3/5 · back in 8 days`), the ladder stepping up, and the passing
  code read-only.
- **One in-order request chain per exercise**: Run cancels the pending debounce, awaits any
  in-flight PUT and uses its returned etag — no spurious 409s. Autosave = 800 ms debounce → PUT;
  a 400 from autosave is **silent** (amber "unsaved" dot; the error surfaces on Run). Raw editor
  text is mirrored to `localStorage[slug]` on every change and offered on open when newer than
  disk. `beforeunload` guard when dirty. 409 with `etag` → banner "reload from disk / overwrite";
  409 without `etag` (no open attempt) → re-open the attempt and retry once. Error bodies are
  `{error,...}` or FastAPI `{detail}` — one helper normalises both.
- Heartbeat: `POST touch` every 60 s while visible.
- `serve()`: build `web/dist` if stale (print what it runs; fail loudly if node/pnpm missing —
  say `pnpm --dir web install && pnpm --dir web build`), start uvicorn on 127.0.0.1:8765; open the
  browser from `threading.Timer(0.7, …)`: on WSL (`microsoft` in `/proc/version`) run
  `explorer.exe <url>` only (ignore its exit code), else `webbrowser.open`; always print the URL.
- Dev loop: `pnpm --dir web dev` (Vite on :5173, proxy to the API) while `uv run study.py` runs.
- Visual direction: `design-brief.md` (frontend-design skill) **plus Daniel's `/design` output**;
  no hacker/terminal aesthetic — no black-and-green, no neon. Dark mode is a calm dark, not black.
- Superseded (2026-08-25): the vanilla-JS/esm.sh design and the Task 1 import lines; the
  `<textarea>` fallback (the editor is bundled, no runtime CDN).

### `selfcheck` (defined)
For each exercise: `body' = solve` with its body replaced by `return _reference(<same parameter
names>)` (decorators kept — works for `ex_098`'s `@pytest.fixture`), write
`exercises/_selfcheck_<slug>.py` = `splice(src, body')`, run pytest on those files with
`cwd=ROOT`, delete them in `finally`. Print `N/N ok` or the failing slugs; exit 1 on failure.

## Tasks

### Task 1: CodeMirror spike (controller runs this; no dispatch)

Static page in the SDD workspace loading from esm.sh: `codemirror@6` (basicSetup, EditorView),
`@codemirror/lang-python@6`, `@codemirror/language@6` (indentUnit), `@codemirror/view@6` (keymap),
`@codemirror/commands@6` (indentWithTab). Success = an EditorView renders with `indentUnit` 4 and
a `Mod-Enter` binding, no "Unrecognized extension value" error. Record the exact import lines that
worked in the ledger; if duplicate `@codemirror/state` instances appear, pin with an import map.
Nothing is committed.

### Task 2: `study.py` core + `test_study.py` (TDD)

Rewrite `study.py` per the design sections above ("Catalogue", "Region + splice", "State",
"Scheduler", "Attempt lifecycle", "selfcheck", and the `summarise`/`run_tests` notes under "API").
Read those sections in the plan file `/home/daniel/.claude/plans/scalable-napping-treehouse.md`
(everything above "## Tasks") — they are the spec. Deliverables:

- Keep: `ROOT`, `LADDER`, `INTERVIEW`, `NEW_PER_DAY`, `GRADES`, `load/save/today/card/due_today/
  pick/grade_of/reschedule/_solution`. Change `EXDIR = ROOT/"exercises"`, `STATE = ROOT/
  "progress.json"`; `load()` returns `{"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}}`
  when missing and fills missing keys on old files. Delete `cmd_next/cmd_check/cmd_hint/cmd_status`.
- New pure functions with these exact names: `bounds`, `cut` (returns a small dataclass or tuple
  `head, lead, body, trail, tail`), `splice`, `strip_spec` (returns `editor, spec_src, spec_text,
  doc_offset`), `merge_spec`, `stub`, `validate` (raises `Invalid(msg, line, col)`), `etag`,
  `read_first(src)`, `has_given(body)`, `summarise`, `touch`, `queue`, `exercises` (ast-based, no exec).
- Attempt lifecycle functions: `open_attempt(st, slug, meta)`, `record_pass(st, slug, meta, code)`
  (does reschedule/log/archive and returns `(grade, gap, box)` — the **caller** writes the stub;
  provide `write_region(path, new_src)` for the atomic write), `abandon(...)`, `next_hint(st, slug,
  hints)` → `(level, text)` or raises `Gated(wait_secs)`, `unlock_solution(st, slug)` → bool.
  `grade_of(attempts, secs, par, solution_shown)` unchanged; callers pass `active`.
- `run_tests(path, seed)` with `cwd=ROOT`, `timeout=60`, `-p no:cacheprovider`; returns `(ok, out)`.
- `selfcheck()` exactly as defined; CLI: `uv run study.py` → `serve` (lazy `from web import serve`),
  `uv run study.py selfcheck`. Module docstring updated.
- `test_study.py` (plain pytest functions, no fixtures), each test globbing `exercises/ex_*.py`
  where it says "all files": splice round-trip on all files; stub identity on all files (they are
  all pristine now); spec round-trip (`merge_spec(strip_spec(body).editor, spec_src)` equals body
  after normalising blank lines); merge edge cases (one-liner `def solve(x): return x` rejected;
  `def solve(\n    x,\n): return x` rejected; 2-space body ok; tab body ok; pasted docstring
  dropped; comment-first body ok; decorated solve keeps decorator); validate rejects: syntax error
  (with line), no solve, two solves, top-level `_reference`, `test_x`, `Name` `_reference` inside
  solve, empty; stub keeps given code (ex_036 `TRUTHY`, ex_044 `ConfigError`); summarise: headline
  = `E   ` lines, a `file.py:NN` inside the region maps to the editor line, a test-frame line
  does not; `grade_of`/`reschedule` pinned with 3 cases each; `queue`/`unseen` with focus ignores
  out-of-focus prereqs (build a tiny fake `exs` dict); `touch` caps a gap at 120 s.
- TDD: write the tests first (RED), then implement (GREEN). Run `uv run pytest test_study.py -q`
  and `uv run ruff check .`; both clean. `uv run study.py selfcheck` → `79/79 ok`.
- Commit: `study.py core: ast catalogue, region splice, attempt lifecycle, selfcheck`.

### Task 3: Migration to one tagged catalogue

Precondition: Task 2 merged (use its functions: `cut`, `strip_spec`, `stub`, `splice`, `bounds`).
Write a one-off script `migrate.py` at the repo root, run it once, verify, commit, then delete the
script in the same commit series (final state has no `migrate.py`). The script asserts a clean
`git status` before touching anything.

1. **Root `progress.json`** from `rsample_drill/progress.json`:
   cards with `seen>0` remapped (ex_01_sortkey→ex_009_sortkey, ex_02_sets→ex_022_sets) with keys
   `{box, due, seen}` only; the 2 log entries with slugs remapped; `focus: null`;
   `archive`: for ex_009 and ex_022 the editor text (`strip_spec(cut(src).body).editor`) of the
   rsample copy's region, `{date: <log date>, grade: <log grade>, code}`;
   `open["ex_016_typehints"]` = `{seed: 4357, attempts: 0, hints: 0, new: true, started: now,
   last: now, active: 0, solution_shown: false}` and ex_016's file gets ex_04's partial solve
   **body** as its draft with `from typing import get_type_hints` as the first line **inside** the
   body (no module-level import; `Callable` annotation dropped; keep the general signature and
   docstring). ex_009/ex_022 stay stubs on disk.
2. **The 10 copies** (rsample file → general file): ex_01→ex_009_sortkey, ex_02→ex_022_sets,
   skipped_ex_03→ex_029_regex, ex_04→ex_016_typehints, ex_05→ex_012_decorators,
   ex_06→ex_013_contextmanager, ex_07→ex_055_concurrency, ex_08→ex_056_asyncio, ex_13→ex_059_mock,
   ex_17→ex_061_whattotest. For each: take the copy's `# READ FIRST` comment block (the consecutive
   `#` lines after the module docstring, skipping blank lines; drop any line containing "copy of"),
   append a line `#   TAKE-HOME: <text>` and insert the block immediately after the general file's
   module docstring, followed by one blank line. Add `rsample` to the general file's tags.
   TAKE-HOME texts (from `rsample_drill/README.md`): 01 `` `sorted(rows, key=score)` in main.py ``;
   02 `` `query_words & content_words` in reranker.py ``; 03 `` `_tokenize` in reranker.py ``;
   04 `required on every signature`; 05 `` `@app.get("/search")`, `@pytest.fixture` ``;
   06 `` the sync half of `async with pool.acquire()` ``; 07 `"why async here?"`;
   08 `` `loadtest.py`, your concurrency test ``; 13 `` `monkeypatch.setattr(...)` ``;
   17 `Task 3 judgement`.
3. **The 8 originals** → `git mv` to `exercises/`: ex_09→`ex_094_await_under_lock.py`,
   ex_10→`ex_095_semaphore.py`, ex_11→`ex_096_async_cm.py`, ex_12→`ex_097_lazy_init_lock.py`,
   ex_14→`ex_098_fixtures.py`, ex_15→`ex_099_asgi_test.py`, ex_16→`ex_100_rerank.py`,
   ex_18→`ex_101_explain_takehome.py`. Set `META["topic"]` to 94…101 and `prereqs`:
   094 `[56]`, 095 `[56]`, 096 `[13, 56]`, 097 `[56, 95]`, 098 `[59]`, 099 `[98]`, 100 `[9, 22, 29]`,
   101 `[94, 100]`. Append the TAKE-HOME line to their existing READ FIRST block:
   09 `` `embed_query` outside `pool.acquire()` ``; 10 `` why `FakePool` is a `Semaphore(max_size)` ``;
   11 `` your `tests/test_search.py` ``; 12 `` `app/db.py` (given — you must explain it) ``;
   14 `what the README asked and you skipped`; 15 `` `httpx.ASGITransport(app=app)` ``;
   16 `Task 2 + the "fraction, not count" upgrade`; 18 `the interview`.
4. `git mv exercises/ex_070_ebscleanup.py exercises/ex_072_ebscleanup.py` (topic stays 72).
5. **Tags** for all 87 files, written into META as a `"tags": [...]` entry (last key; keep the
   file parseable and ruff-clean): section by topic — 1–17 `core` · 18–25 `data-structures` ·
   26–34 `files-text` · 35–42 `stdlib-ops` · 43–47 and 81 `errors` · 48–53 `http` · 54–56
   `concurrency` · 57–61 `testing` · 62–67 `packaging` · 68–72 `cloud` · 73–80 and 82–86
   `whole-task` · 88–93 `llm` · 94–97 `concurrency` · 98–99 `testing` · 100–101 `whole-task`;
   library tags from the file's own imports — `boto3`/`moto`→`boto3`, `requests`/`responses`→
   `requests`, `langchain_core`→`langchain`, `fastapi`/`httpx`→`fastapi`, `asyncio`→`asyncio`;
   track tag `rsample` on the 18 (10 merged + 8 originals). Leave `tier` untouched.
6. `git rm -r rsample_drill/`.
7. `pyproject.toml`: `testpaths = ["exercises", "test_study.py"]`; ruff per-file-ignore
   `"exercises/*" = ["E402"]`; `uv add --dev uvicorn`. `.gitignore`: add `*.tmp` and
   `.pytest_cache/`; do not ignore `progress.json`.
8. `README.md`: delete the "Take-home track" section; add a "Tags" section (vocabulary above, the
   `rsample` track tag, focus); in "Adding exercises" add `tags` to the META list and the region
   contract ("everything between META and HINTS is the learner's; `solve` must be the last
   statement in it; given code goes above `solve`").

Verification (all must hold; put the commands and output in the report): `uv run study.py
selfcheck` → `87/87 ok`; `uv run pytest --collect-only -q exercises | tail -1` → 88 tests;
`ls exercises/ex_*.py | wc -l` → 87; no `rsample_drill/`; every META has a non-empty `tags` list;
filename number == `topic` for 87/87; for every file except ex_016 `stub(cut(src).body) ==
cut(src).body`; ex_016's body contains `get_type_hints` and no module-level typing import;
`uv run pytest test_study.py -q` green; `uv run ruff check .` clean; `git status` clean after the
final commit and `migrate.py` gone. Commit(s): `Merge rsample drills into one tagged catalogue`.

### Task 4: `web.py` API + ASGI smoke tests

Implement `web.py` per the "API" and "Attempt lifecycle" sections of the plan file
`/home/daniel/.claude/plans/scalable-napping-treehouse.md` (read everything above "## Tasks";
it is the spec). Use `study.py`'s functions — do not re-implement logic in `web.py`. Details:

- FastAPI app; `TrustedHostMiddleware(allowed_hosts=["127.0.0.1", "localhost"])`; a request-body
  limit of 256 KB (reject larger with 413); one module-level `threading.Lock` held for every
  handler that reads/writes an exercise file or `progress.json`; static mount
  `StaticFiles(directory=ROOT/"web", html=True)` at `/` registered **last**. Create `web/` with a
  placeholder `index.html` (one line) so the mount works; Task 6 replaces it.
- Pydantic bodies: `{code: str, etag: str}` for PUT/run, `{etag: str}` for abandon,
  `{tag: str|None}` for focus. Unknown slug → 404. Etag mismatch → 409 `{etag, code}` with the
  current disk editor text. `validate` failure → 400 `{error, line, col}`.
- `run`: sync `def`; save (validate + atomic write) first; increment attempts only when pytest
  ran; on pass call `record_pass`, write the stub, delete the attempt, respond per the table.
- `serve()`: `uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")`; browser open
  via `threading.Timer(0.7, ...)`: on WSL (`"microsoft" in Path("/proc/version").read_text().lower()`)
  `subprocess.Popen(["explorer.exe", url])` (ignore exit code), else `webbrowser.open(url)`;
  print the URL first.
- Tests appended to `test_study.py` using `httpx.AsyncClient(transport=httpx.ASGITransport(app=app))`
  against a **temporary copy** of one real exercise (copy `exercises/ex_001_fstrings.py` and
  `_lib.py` into a `tmp_path`-free temp dir you create/remove yourself; point `study.EXDIR`/`STATE`
  there via monkeypatching module globals inside the test, restore after): catalogue lists it →
  open → run stub → 400? no: the stub parses, so run → `passed False`, headline contains
  `NotImplementedError`, attempts 1 → PUT a body with 2-space indentation → 200, file on disk still
  has the docstring → run with the reference body (`return "\n".join(f"{name:<14}{value:>12,.2f}"
  for name, value in rows)`) → `passed True`, grade present, file on disk is the stub, `progress.json`
  has 1 log entry, `open` empty, `archive` has the code → open again → attempt exists, `code` is the
  stub, archive `code` absent (card not due? it is scheduled → present; so instead assert the
  attempt is fresh) → hint → 200 level 1; hint again immediately → 423 → `Host: evil.com` header →
  400 → PUT with a stale etag → 409. Keep it to one or two test functions.
- `uv run pytest -q` green, `uv run ruff check .` clean, `uv run study.py selfcheck` still 87/87.
- Commit: `web.py: JSON API over the drill core`.

### Task 5: Design direction (controller runs this with the frontend-design skill; no dispatch)

Invoke `frontend-design:frontend-design`; choose palette (no black/green, no neon; calm and
professional), typography, spacing, the three layouts (catalogue+Today, exercise, progress) and
the CodeMirror theme colours. Write `.superpowers/sdd/scalable-napping-treehouse/design-brief.md`
with concrete CSS variables (colours as hex, font stacks, sizes), component list and a one-screen
ASCII/markdown mock of the exercise page. The brief is the input to Task 6.

### Task 9: Production-grade layout (runs NOW, before Task 6 — Daniel, 2026-08-25)

Same behaviour, proper application shape: launchable as-is (`uv run study`) or as a Docker image.
No new features; every existing test keeps passing (split across files, same assertions).

1. **Package** `src/study/` with the modules in the Architecture tree. Move code, don't rewrite:
   function names, signatures and behaviour are unchanged (`bounds/cut/splice/strip_spec/
   merge_spec/stub/validate/etag/write_region`, `exercises/read_first/has_given`, `queue/grade_of/
   reschedule/…`, `touch/open_attempt/record_pass/abandon/next_hint/unlock_solution`, `run_tests/
   summarise/selfcheck`, the FastAPI handlers). Delete `study.py`, `web.py`, `test_study.py`,
   `main.py` (placeholder). `src/study/__main__.py` → `cli.main()`.
   `pyproject.toml`: `[build-system]` hatchling, `[tool.hatch.build.targets.wheel] packages =
   ["src/study"]`, `[project.scripts] study = "study.cli:main"`, real `description`.
   **Dependencies**: move the runtime set into `[project.dependencies]` — fastapi, uvicorn, pytest,
   pytest-timeout, httpx, and the libraries the exercises import at runtime (verify by grepping
   `exercises/`: boto3, moto, requests, responses, langchain-core, …). Dev group keeps ruff,
   ipykernel, pytest-watcher. `uv lock` regenerates; commit `uv.lock`.
2. **Settings** (`settings.py`, stdlib dataclass, one module-level `settings` instance): `root`
   (`STUDY_ROOT`; default: the current directory if it contains `exercises/`, else the repo root
   = parent of `src/`), `host` (`STUDY_HOST`, default `127.0.0.1`), `port` (`STUDY_PORT`, 8765),
   `open_browser` (`STUDY_OPEN_BROWSER`, `1`). `exercises_dir = root/"exercises"`, `state_path =
   root/"progress.json"`, `web_dist = <package parent>/web/dist`. Every module reads paths from
   `settings` at call time (no import-time path constants) so tests can point `settings.root` at
   a temp dir and restore it in `finally`. Binding to a non-loopback host is allowed only via
   `STUDY_HOST` (Docker); `TrustedHostMiddleware` keeps `["127.0.0.1", "localhost"]` (the browser
   reaches the container through a published localhost port; Starlette ignores the port).
3. **Runner**: `run_tests` uses `cwd=settings.root` so `exercises/_lib.py` keeps importing.
4. **API**: add `GET /api/health` → `{"status": "ok", "exercises": N, "root": str}` (no lock,
   no save). Everything else identical to today's `web.py`. `serve()` skips the browser when
   `open_browser` is off or `host != 127.0.0.1`.
5. **Logging**: stdlib `logging` configured once in `cli.main()` (INFO, `%(asctime)s %(levelname)s
   %(name)s: %(message)s`); one INFO line per run (`slug passed=… attempts=…`), per pass (grade,
   box, due), per abandon; uvicorn `log_level="info"` and its access log left on. No log
   framework, no JSON logging.
6. **Tests** → `tests/` split by module as in the tree; `pytest.ini_options.testpaths = ["tests",
   "exercises"]`; `python_files` unchanged. The API tests point `settings.root` at their temp
   copy (replacing today's `study.EXDIR/STATE` monkeypatch) and add one `GET /api/health` assert.
   ruff per-file-ignores: `"src/study/*" = ["DTZ"]` replaces the `study.py` entry.
7. **Docker**: `Dockerfile` (multi-stage-ready): `python:3.13-slim`, install `uv` (copy from
   `ghcr.io/astral-sh/uv:latest`), copy `pyproject.toml`+`uv.lock`+`src/`, `uv sync --frozen
   --no-dev`, non-root user, `ENV STUDY_ROOT=/data STUDY_HOST=0.0.0.0 STUDY_OPEN_BROWSER=0`,
   `EXPOSE 8765`, `HEALTHCHECK` via `python -c "urllib.request.urlopen('http://127.0.0.1:8765/
   api/health')"`, `CMD ["study"]`. Copy `web/dist` into the image **if present** (Task 6 adds the
   node build stage; leave a commented stage stub). `compose.yaml`: service `study`, `build: .`,
   `ports: ["127.0.0.1:8765:8765"]`, volumes `./exercises:/data/exercises` and
   `./progress.json:/data/progress.json`. `.dockerignore` (.venv, .git, web/node_modules, drafts,
   *.html, __pycache__, .pytest_cache). Docker is **not installed on this box** — write the files
   carefully, `docker build` cannot be run here; say so in the report (the controller notes it as
   unverified).
8. **CI**: `.github/workflows/ci.yml` — on push/PR: `astral-sh/setup-uv`, `uv sync`, `uv run ruff
   check .`, `uv run pytest tests -q`, `uv run study selfcheck`. Cannot be run here either; keep it
   minimal and valid YAML.
9. `README.md` command block only (`uv run study`, `uv run study selfcheck`, `uv run pytest
   exercises/ex_019_counter.py`, `docker compose up`); the full doc pass stays in Task 8.

Verification (paste outputs): `uv run pytest tests -q` → 42 passed (43 with the health assert),
no warnings; `uv run ruff check .` clean; `uv run study selfcheck` → 87/87; `uv run study` boots
(record PID, `curl -s http://127.0.0.1:8765/api/health`, `curl -s -o /dev/null -w '%{http_code}'
-H 'Host: evil.com' …/api/catalogue` → 400, kill by PID); `python -m study --help` works;
`git status` clean; `STUDY_ROOT=/tmp/x uv run study selfcheck` fails loudly with a clear message
(no exercises dir). Commits: `Restructure into the study package`, `Docker image, compose and CI`.

### Task 10: Content format — one folder per drill, guidance in Markdown (runs NOW, before Task 6)

Spec: `.superpowers/sdd/scalable-napping-treehouse/content-format-spec.md` — binding, read it
fully first. Implement the core change and the migration in one task, in this order:

1. **Core** (`src/study/`): `region.py` → marker-based region (`bounds/cut/splice/stub/has_given/
   validate/etag/write_region`; delete `strip_spec`, `merge_spec`, `Spec`, `doc_offset`, the
   docstring gate). `catalogue.py` → folders `exercises/<NNN>_<name>/` with `README.md` (PyYAML
   frontmatter; `topic` from the folder name; spec Markdown = body up to `## Hints`; hints = the
   `### Hint N` sections) + `drill.py` (marker present). `runner.py` → `_selfcheck.py` inside the
   folder; `summarise` keeps mapping `drill.py:NN` to editor lines (region starts at line 1, so
   the map is identity up to the marker). `api.py` → payload per the spec's "API changes"
   (`spec_md`, no `read_first`/`doc_offset`, `meta.source`, assets endpoint). `settings.py`
   unchanged. `pyproject.toml`: `pyyaml` runtime dep; pytest `pythonpath = ["exercises"]`,
   `python_files = ["drill.py", "test_*.py"]`; ruff ignores for `exercises/*/drill.py`.
2. **Tests** (`tests/`): rewrite `test_region.py` for the marker region (round-trip on all drills,
   stub identity on all drills except open attempts, validate rejections incl. "marker in edited
   text"), `test_catalogue.py` (frontmatter, headings, exactly 3 hints, topic from folder name,
   broken folder skipped), `test_api.py` (temp copy of one drill folder; spec_md present; hint
   texts are Markdown; assets endpoint 200/404 incl. traversal), scheduler/attempts/runner tests
   adjusted to the new slugs. TDD: red first for the new region and catalogue behaviour.
3. **Migration** — `migrate.py` at the root per the spec's "Migration" section; run once; verify
   the list in the spec; delete the script in the final commit. Do not hand-edit drills except
   where the converter cannot classify a docstring line (report those).
4. `README.md` (repo): update "The exercises" (layout, README.md contract, drill.py marker,
   Exercism verbatim rule) and the Layout tree. `DESIGN.md`: the spec pane renders Markdown
   (headings, lists, tables, fenced code, GitHub alerts, Mermaid, images, muted looping video),
   hints are Markdown; `read_first` is part of the Markdown.
5. Verification (paste): `uv run pytest tests -q` green, no warnings; `uv run ruff check .`;
   `uv run study selfcheck` → 104/104; `ls -d exercises/*/ | wc -l` → 104; a script that loads
   every README and asserts required frontmatter keys + headings + 3 hints; boot smoke:
   `GET /api/ex/019_counter` shows `spec_md` starting with `# ` and `GET /api/ex/019_counter/
   assets/..%2Fdrill.py` → 404; `git status` clean; `progress.json` keys renamed, values intact
   (diff shows only key renames); `exercises/016_typehints/drill.py` region == the old file's
   region minus the docstring.
Commits: `Core: marker region, Markdown guidance, folder per drill` · `Migrate drills to folders` ·
`Remove the migration script`.

### Task 11: Content pass — Exercism verbatim + native polish (after Task 10)

Per the spec's "Exercism drills — keep their content, add ours": rebuild `README.md` for the 17
Exercism drills (200,203,206,207,209,212,213,300–309) from `/tmp/exercism-python` sources
(introduction.md, instructions.md, instructions.append.md, hints.md, concepts/<slug>/links.json,
introduction.md) — Exercism text verbatim, our Why / You get / You return / Rules / Hint 3 kept
from the migrated README, attribution line. Native drills (87): fence every example, turn
`TAKE-HOME:` into callouts, tables where a rule list is really a table; no wording changes to the
WHY blocks. Batches of ~20 per implementer; one reviewer per batch checks: nothing from Exercism
dropped, headings contract, 3 hints, frontmatter, selfcheck still green.
Update `phase-b-exercism.md` so batches B–I author the folder format directly.

### Task 6: Frontend (React + Vite + shadcn/ui)

Implement the `web/` Vite project per the "Frontend" and "API" sections of the plan file
`/home/daniel/.claude/plans/scalable-napping-treehouse.md` (read everything above "## Tasks") and
the design inputs: `.superpowers/sdd/scalable-napping-treehouse/design-brief.md` **and the
`/design` output Daniel provides** (path recorded in the ledger under "Task 6 design input";
if the two disagree, `/design` wins). Stack is fixed: React 19, TypeScript, Vite, Tailwind v4,
shadcn/ui (CLI-generated components into `web/src/components/ui`), TanStack Query, react-router
(hash), `@uiw/react-codemirror` + `@codemirror/lang-python` + `@uiw/codemirror-themes`. Setup details
verified via Context7 are in `.superpowers/sdd/scalable-napping-treehouse/stack-notes.md` (binding). pnpm;
commit `web/pnpm-lock.yaml`; git-ignore `web/dist`, `web/node_modules`. Keep `web/src` under
~1,200 lines total; if it grows past that, report it rather than adding abstractions.

Also: `study/api.py` mounts `settings.web_dist` (keep `html=True`, still registered last) and
`serve()` gains the build-if-stale step described in "Frontend"; the Dockerfile gets its node build
stage (`node:24-slim`, `pnpm install --frozen-lockfile && pnpm build`, copy `dist` into the python
stage). Delete the placeholder `web/index.html`.

Must-haves checklist (the reviewer checks each): 3 routes; catalogue search + tag chips (AND) +
status filter + Today panel + focus select; exercise page layout with spec `<pre>`, READ FIRST
links, given-code note, editor with `indentUnit` 4 + `Mod-Enter` + `indentWithTab`, toolbar (Run,
timer with amber/red thresholds, attempts, seed, hints with countdown, solution button states,
abandon, archive), results panel (headline + collapsible output; pass state with grade line,
ladder step and read-only passing code); in-order request chain (Run cancels debounce, awaits
in-flight PUT, reuses its etag); autosave 800 ms with silent 400 + amber dot; localStorage draft
mirror offered on open when newer; `beforeunload` when dirty; 409 banner (etag) / re-open (no
attempt); heartbeat every 60 s while visible; **light + dark mode** incl. the editor, toggle in the
header, system default; progress view with boxes/ladder, due count, per-tag table, last 30 log
lines. Accessibility basics: shadcn primitives, visible focus, contrast per tokens in both modes.

Verify: `pnpm --dir web build` clean (tsc + vite), `uv run study` serves the built app at
`http://127.0.0.1:8765/` (curl `/` → 200 with the Vite `index.html`, `/assets/*.js` → 200), the
ASGI tests in `tests/test_api.py` still green, `uv run ruff check .` clean. Exercise the UI in a real
browser if one is available (explorer.exe opens the Windows browser on this WSL box); otherwise
state clearly that browser verification is left to the controller (Task 7).
Commit: `web UI: React + Vite catalogue, exercise page, progress`.

### Task 7: End-to-end verification in a real browser (controller runs this; fixes are dispatched)

Run the 13-step sequence in "Verification (end-to-end)" below with the t3 preview browser against
`uv run study.py`. Every failure becomes a finding for a single fix dispatch (Opus), then a
scoped re-review.

### Task 8: Docs and final review

Update `README.md` (`uv run study`, `uv run study selfcheck`, `docker compose up`, `uv run pytest
exercises/ex_019_counter.py`), the package layout, that passing resets the file and solutions live
in `progress.json`, Exercism attribution (Phase B). Remove anything that still mentions
`STUDY_DIR`, `check`, `hint`, `next`, `status`. Commit: `README.md for the web UI`. Then the controller
dispatches the final whole-branch review.

## Verification (end-to-end)

1. `uv run study.py` → browser opens `#/`; 87 rows; tag chips include `rsample`; Today shows due + new.
2. Open a fresh exercise → spec shows WHY/YOU GET/YOU RETURN; editor shows the 2-line stub.
3. Run → headline `NotImplementedError`, attempts 1. Type and press Run within 1 s → no 409.
4. Type a wrong answer with **2-space indentation**, wait 1 s → `git diff`: only the region changed,
   docstring intact; Run → assertion line(s), editor line numbers correct.
5. Paste the reference body → pass state with grade; file on disk is the stub; `progress.json` has
   the log entry, `open` gone, `archive` has the code; `git diff` shows only `progress.json`.
6. Set that card's `due` to yesterday → reload → "due"; open → stub, **archive code not shown**;
   pass again → promotes (solution_shown cleared per attempt).
7. Peek the solution on another exercise → pass → grade struggled; next attempt on it passes → promotes.
8. `focus = rsample` → Today offers ex_012 despite prereq 8 not being rsample.
9. ex_098 (decorated, 2 tests) runs green and, after pass, the stub keeps the decorator; ex_036's
   stub keeps `TRUTHY`.
10. Edit the file in VS Code and save; type in the browser → 409 banner, no silent clobber.
11. Toggle dark mode → every panel and the editor switch, contrast holds; reload keeps the choice.
    Type an unparseable draft, reload → draft offered from localStorage.
12. `curl -H 'Host: evil.com' http://127.0.0.1:8765/api/catalogue` → 400.
13. `uv run study selfcheck` → all ok; `uv run pytest tests -q` green; `docker compose up` serves
    the same app on 127.0.0.1:8765 (on a box with Docker).

## Skipped on purpose (add when needed)
- Quiz-style exercises (ex_061, ex_101) get over-credited on review (recall of letters) — accepted;
  add a `quiz` tag + box cap if it bothers you.
- Partial read-only ranges for the 7 "given code" files — a note instead; the risk is self-sabotage.
- File watcher / `window.focus` re-fetch — etag + 409 covers it.
- A "show the test" panel (HackerRank shows tests) — later add if wanted.
- FSRS scheduling (`py-fsrs`) instead of the Leitner ladder — later, if the ladder feels wrong.
- Multi-user, auth, CORS, remote access — localhost only.
