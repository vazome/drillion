# Task 4 report — `web.py` JSON API + ASGI smoke tests

Commit: `89f4d57 web.py: JSON API over the drill core` on branch `study-ui`.
Parent is `3e85082` ("read_first: skip the # SOURCE: attribution line"), which landed on
`study-ui` from outside this task while I was working — my commit sits on top of it, the tree
is clean, and everything below was re-verified after it appeared.

Files: `web.py` (new, 355 lines), `web/index.html` (new, one line — Task 6 replaces it),
`test_study.py` (+133 lines: 2 API tests, 2 helpers, imports/docstring).
`study.py`, `progress.json` and `exercises/` are untouched.

## What I implemented

**Shape.** One FastAPI app, `docs_url=redoc_url=openapi_url=None` (no surface we don't use),
`TrustedHostMiddleware(allowed_hosts=["127.0.0.1", "localhost"])` added last so it is the
outermost middleware, a `content-length` guard returning 413 above `MAX_BODY = 256 * 1024`, and
`StaticFiles(directory=study.ROOT/"web", html=True)` mounted at `/` after every route.

**Every route is a plain `def`, not `async def`.** They all block on one module-level
`threading.Lock`; an `async def` waiting on it would freeze the event loop for the whole of a
60 s pytest run. FastAPI runs sync handlers in its threadpool, so blocking there is correct.
The brief only required this of `run`; making it uniform is what makes the lock safe.

**Routes** (all as the plan's API table): `GET /api/catalogue`, `GET /api/progress`,
`GET /api/ex/{slug}`, `POST …/open`, `PUT /api/ex/{slug}`, `POST …/run`, `…/touch`, `…/hint`,
`…/solution`, `…/abandon`, `POST /api/focus`. Bodies are `Edit{code, etag}`, `Etag{etag}`,
`Focus{tag: str | None}`.

**Error shapes.** Two exception handlers give the page one vocabulary:
`study.Invalid` → 400 `{error, line, col}`; `HTTPException` → its `detail` verbatim when it is a
dict, else `{"error": detail}`. So:
- 404 `{error: "no exercise 'x'"}` — a slug only ever indexes `study.exercises()`.
- 409 `{error, etag, code}` on an etag mismatch, `code` being the current disk editor text.
- 409 `{error: "no open attempt — open the exercise first"}` for `run/touch/hint/solution` when
  `st["open"]` has no entry — this is the documented answer to the ruling's "409 or 400, pick one".
  The two 409s are told apart by the presence of `etag`.
- 423 `{error, wait_secs, exhausted}` for hints: `Gated(n>0)` → `exhausted: false`;
  `Gated(0)` → `wait_secs: 0, exhausted: true` and "no hints left — the solution is the next step".
- 423 `{error, need_attempts, need_secs}` for a locked solution.
- 413 `{error}` for an oversized body; 400 (plain text, from Starlette) for a bad `Host`.

**Rulings honoured.** `open_attempt(st, slug)` 2-arg; `abandon(st, slug, disk_src)` returns the
stubbed source and `web.py` does the etag check + `write_region`; `record_pass(st, slug, meta,
code)` returns `(grade, gap, box)` and deletes the attempt itself (checked the source — `del
st["open"][slug]` is in there, so `run` does not repeat it), and `web.py` writes `stub(body)`;
`summarise(out, region_start, doc_offset, hints_line)`; etag compared against `study.etag(disk_src)`
before validating; GET handlers never `save()`.

**One bug this avoided:** `summarise`'s coordinates are recomputed from the *just-written* source
(`_coords(new_src)`), not from the catalogue entry parsed before the write. The learner's edit
changes the line count of the region, so using the pre-write `region_start`/`hints_line` would
have mis-mapped every traceback line by the size of their edit.

**`serve()`** prints the URL first (`flush=True`, so it shows when stdout is piped),
`threading.Timer(0.7, …)` opens the browser — `explorer.exe <url>` on WSL (`/proc/version`
contains "microsoft"; existence-checked so this still works on macOS), else `webbrowser.open` —
then `uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")`.

## Deliberate readings where the plan is self-contradictory

1. **PUT does not touch the timer or write `progress.json`.** The API table says PUT mutates
   "file"; the State section lists "save" among the touch points. I followed the table: autosave
   fires on an 800 ms debounce and would otherwise rewrite the whole `progress.json` (archive of
   every solution included) once a second while typing. Nothing is lost — `touch()` caps a gap at
   120 s and the page heartbeats every 60 s while visible, so `active` stays accurate.
2. **`abandon` tolerates a missing attempt** (`study.abandon` pops with a default), so it doubles
   as "reset this file to the stub". Every other mutating route requires an open attempt.
3. **`status` is included in the exercise payload** as well as in the catalogue rows — the
   exercise page is reachable directly by hash URL and would otherwise have to guess.
4. `meta` in the payload is the catalogue entry minus `path, hints, read_first, hints_line,
   region_start` (`CATALOGUE_ONLY`): `hints` are spoilers and are served one at a time by the
   gated route, `path` is not the browser's business, and the rest are top-level fields already.
5. `touch` does not call `exercises()` (no 404 for an unknown slug, it answers 409). It runs every
   60 s and only a slug that already passed the 404 check can be in `st["open"]`.

`# ponytail:` markers: one, on the body limit — a chunked request carries no `content-length` and
slips past it; the only client is our own page and uvicorn caps headers.

## Tests

Two functions, plain pytest, no fixtures. `_api(flow)` copies `ex_001_fstrings.py` + `_lib.py`
into `tempfile.mkdtemp()`, repoints `study.EXDIR`/`study.STATE` at it, runs the async flow with
`asyncio.run` (no pytest-asyncio in the project, and none added) over
`httpx.AsyncClient(transport=httpx.ASGITransport(app=web.app), base_url="http://127.0.0.1")`,
then restores the globals and `rmtree`s the directory in `finally`. Daniel's real
`exercises/`, `progress.json` and open ex_016 attempt are never touched.

`test_the_api_carries_a_drill_from_stub_to_pass` — catalogue lists the one drill as `new` and
queues it → `open` (fresh attempt, spec stripped out of `code`, no `_reference`) → `run` the stub
(`passed False`, `attempts 1`, headline mentions `NotImplementedError`) → `PUT` a 2-space-indented
body (200; the file on disk gets `\n  """WHY` — the spec goes back at the learner's indent) →
the same etag again → 409 carrying the fresh etag and the disk code → `run` the reference body
(`passed True`, grade in `GRADES`, `due_in == LADDER[box]`, and `stub(body) == body` on disk) →
state has one log entry, no open attempt, the archive holds the passing code → `open` again
(attempt is fresh: `{attempts: 0, hints: 0, active: 0, …}`, `code` is the stub, the archive entry
has **no** `code` key, solution locked) → `hint` 200 level 1 of 3 → `hint` again 423 with
`0 < wait_secs <= 120` → `Host: evil.com` → 400.

`test_the_api_guards_its_edges` — a GET leaves no `progress.json` behind (the "GETs never save"
ruling) → `_lib` (a real file, not a catalogue entry) 404 → `..%2f..%2fetc%2fpasswd` 404 →
unknown slug 404 → `run` with no attempt 409 → a 256 KB+ body 413 → a syntax error 400 with
`(line, col) == (2, 14)` and the file on disk unchanged → `return _reference(rows)` 400 →
locked solution 423 → focus round-trip through the catalogue → `per_tag` → abandon an untouched
stub (200, attempt gone, nothing archived).

## Verification

```
$ uv run pytest test_study.py -q
..........................................                               [100%]
42 passed in 2.77s

$ uv run ruff check .
All checks passed!

$ uv run study.py selfcheck
87/87 ok

$ uv run pytest -q | tail -1
86 failed, 43 passed, 1 error in 6.33s
```
The full-suite line is the pre-existing baseline, not a regression: `testpaths` includes
`exercises/`, whose 87 stubs are *meant* to raise `NotImplementedError` (Task 3's report records
"86 failed, 41 passed, 1 error"; the two extra passes are the new API tests). `uv run pytest -q`
can never be green while the drills are stubs — the brief's "`uv run pytest -q` green" can only
mean `test_study.py`, which is green.

Real boot smoke (server started in the background, PID recorded, killed by PID):

```
$ uv run study.py > /tmp/serve.log 2>&1 &   # pid 332980
$ cat /tmp/serve.log
study → http://127.0.0.1:8765/   (ctrl-c to stop)

$ curl http://127.0.0.1:8765/api/catalogue | head -c 300
{"focus":null,"tags":["asyncio","boto3","cloud","concurrency","core","data-structures","rsample",
"errors","fastapi","files-text","http","langchain","llm","requests","stdlib-ops","testing",
"whole-task"],"today":{"review":["ex_009_sortkey","ex_022_sets"],"new":["ex_001_fstrings",
"ex_002_slicing"],"done

$ curl -s -o /dev/null -w '%{http_code}' -H 'Host: evil.com' http://127.0.0.1:8765/api/catalogue
400
$ curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8765/            # the placeholder page
200
$ curl -s -o /dev/null -w '%{http_code}' -X PUT -H 'Content-Type: application/json' \
       --data-binary @/tmp/big.txt http://127.0.0.1:8765/api/ex/ex_001_fstrings   # 300 KB
413
$ curl -s http://127.0.0.1:8765/api/progress | head -c 120
{"boxes":[2,0,0,0,0],"due":2,"seen":2,"total":87,"log":[{"date":"2026-08-21","slug":"ex_009_sortkey",
$ curl -s http://127.0.0.1:8765/api/ex/ex_016_typehints        # Daniel's live attempt, read only
… "status":"open","attempt":{"attempts":0,"hints":0,"active":0,"seed":4357,"solution_shown":false},
  "hints":{"total":3,"shown":[],"next_in":0},"solution":{"unlocked":false,"need_attempts":3,
  "need_secs":600},"archive":[]  (code = the get_type_hints draft, spec stripped)
$ curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
       -d '{"code":"x","etag":"y"}' http://127.0.0.1:8765/api/ex/ex_001_fstrings/run
409
$ kill 332980   # → stopped; git status clean, progress.json unmodified
```
The GETs against the live state left `progress.json` byte-identical (`git status` clean) —
the zero-cards `card()` materialises are never persisted by a GET.

## Self-review findings (fixed before committing)

- The first `_coords` used the catalogue's `region_start`/`hints_line`, i.e. the file *before* the
  write. Recomputed from `new_src` (see above).
- `date.today()` in the catalogue tripped DTZ011 (ruff's rules here are wider than the default and
  the `DTZ` per-file-ignore only covers `study.py`). Replaced with
  `date.fromisoformat(study.today())`, which also gives the whole app one definition of "today"
  instead of two.
- Two `# noqa: SLF001 / S603, S607` directives were dead (those rules are off here) and RUF100
  flagged them; they are ordinary comments now.
- `run` called `study.cut(new_src)` three times; hoisted to one `body`.
- A first draft of the guards test used `"def solve(rows):\n    return"` as "broken code" — a bare
  `return` parses fine, so it returned 200 and the assertion was checking nothing. Replaced with
  `return 1 1`, and the test now pins `(line, col)` and asserts the file on disk is unchanged.
- The traversal probe `/api/ex/../../etc/passwd` is normalised to `/etc/passwd` by httpx, so it
  was testing the static mount, not the slug guard. Replaced with `/api/ex/_lib` (a file that
  really exists next to the drill but is not in the catalogue) plus a percent-encoded traversal.
- `print` in `serve()` got `flush=True` after the boot smoke showed an empty log file when stdout
  is a pipe rather than a terminal.

## Concerns

1. **`run` holds the global lock for the whole pytest subprocess** (up to 60 s), so a second tab's
   catalogue GET waits behind it. That is the plan's "one lock serialises read→validate→write→save"
   taken literally, and this is a single-user app on loopback; a per-slug lock is the upgrade if it
   ever bites.
2. **`exercises()` runs on nearly every request** (~60 ms, 87 files). Fine at one user, and the
   plan explicitly says "no cache", but `touch`/`hint` on a slow disk will feel it. `touch` already
   skips it.
3. **`_solution` is a private name in `study.py`** and the plan says to call it; it stays private
   with the gate immediately above the call.
4. The 409 for "no open attempt" and the 409 for an etag mismatch share a status code. The page
   must branch on `"etag" in body`. I chose 409 over 400 because 400 is already the validate shape.
5. `web/index.html` is a one-line placeholder that links to `/api/catalogue`; Task 6 replaces it.
   `StaticFiles` needs the directory to exist at import time, so `import web` fails if `web/`
   is ever deleted.
6. The passing `code` returned by `run` and stored in the archive is derived from what landed on
   disk (`strip_spec(cut(new_src).body).editor`), not the raw submitted string — identical unless
   the learner pasted the docstring back, in which case the archived copy is the normalised one.
