# Task 9 report — production-grade layout of `study`

Branch `study-ui`, from `3c06497`. Two commits, tree clean, nothing pushed.

- `dfebde2 Restructure into the study package`
- `67a89a0 Docker image, compose and CI`

## What was done, per step

### 1. Package `src/study/`

`study.py` and `web.py` were split by slicing their exact line ranges into the modules from the
plan's Architecture tree — no function was retyped:

| module | contents |
|---|---|
| `region.py` | `Invalid`, `Region`, `Spec`, `_assign/_solve/_str_expr/_docstring`, `bounds/cut/splice/strip_spec/merge_spec/stub/etag/validate/write_region` |
| `state.py` | `load/save/today/card` |
| `catalogue.py` | `has_given`, `read_first`, `exercises` |
| `scheduler.py` | `LADDER/INTERVIEW/NEW_PER_DAY/GRADES`, `due_today/unseen/queue/pick/grade_of/reschedule` |
| `attempts.py` | `HINT_GAP/SOLUTION_GATE`, `Gated`, `touch/open_attempt/record_pass/abandon/next_hint/unlock_solution/_solution` |
| `runner.py` | `_FILE_LINE`, `run_tests`, `summarise`, `_reference_call`, `selfcheck` |
| `api.py` | the FastAPI app, all handlers, `serve()` (git recorded it as a rename of `web.py`) |
| `cli.py`, `settings.py`, `__main__.py`, `__init__.py` | new |

`study.py`, `web.py`, `test_study.py`, `main.py` deleted. `pyproject.toml`: hatchling build backend,
`[tool.hatch.build.targets.wheel] packages = ["src/study"]`, `[project.scripts] study =
"study.cli:main"`, real description. Runtime deps (`boto3, fastapi, httpx, langchain-core, moto,
pytest, pytest-timeout, requests, responses, uvicorn`) moved into `[project.dependencies]` — the
exercise imports were verified by grepping `exercises/` (`botocore` arrives with boto3; everything
else the drills import is stdlib). Dev group is `ipykernel, pytest-watcher, ruff`. `uv lock` +
`uv sync` re-run; `uv.lock` committed.

**Move-not-rewrite check.** I diffed every top-level def/class of `3c06497:study.py` and
`3c06497:web.py` against the package (normalising the `study.` prefix). Nothing is missing, nothing
new except `Settings`, `_default_root` and `health`, and the only changed bodies are:
`load`/`save` (settings path), `exercises` (settings path), `run_tests`/`selfcheck` (`cwd`), `main`
(argparse + logging + root check), the api handlers that gained a log line, and `serve()`. Every
other function is byte-identical.

### 2. Settings

`settings.py`: one stdlib `@dataclass Settings`, one module-level `settings`. `root` from
`STUDY_ROOT`, else the cwd when it holds `exercises/`, else the repo (parent of `src/`);
`host`/`port`/`open_browser` from `STUDY_HOST`/`STUDY_PORT`/`STUDY_OPEN_BROWSER`.
`exercises_dir`, `state_path`, `web_dist` are properties, so every read happens at call time and a
test can assign `settings.root` and restore it in `finally`. No module keeps a path constant
(`ROOT`/`EXDIR`/`STATE` are gone). `TrustedHostMiddleware` still allows exactly
`["127.0.0.1", "localhost"]`; only `STUDY_HOST` can widen the bind address.

### 3. Runner

`run_tests` and `selfcheck` run pytest with `cwd=settings.root`, so `exercises/_lib.py` still
imports and the API tests' temp root works the same way.

### 4. API

Added `GET /api/health` → `{"status": "ok", "exercises": N, "root": str}`, outside the lock, no
`save()`. Everything else is the old `web.py`. `serve()` reads host/port from settings and skips the
browser when `open_browser` is off or the host is not `127.0.0.1`. The static mount is now
`settings.web_dist` and is skipped while that directory does not exist (Task 6 creates it) —
otherwise `StaticFiles` raises at import and the server cannot boot at all.

### 5. Logging

`logging.basicConfig(INFO, "%(asctime)s %(levelname)s %(name)s: %(message)s")` once in `cli.main()`.
`study.api` logs one line per run (`slug passed=… attempts=…`), one per pass
(`slug grade box=… due in …d`), one per abandon. uvicorn runs at `log_level="info"` with its access
log on. No log framework, no JSON.

### 6. Tests

Split into `tests/test_region.py` (22), `test_catalogue.py` (3), `test_scheduler.py` (6),
`test_attempts.py` (8, including the `load()` state test — the tree has no `test_state.py`),
`test_runner.py` (2), `test_api.py` (3). Shared helpers (`FILES/SRC/SPEC/_parts/_solved/_exs/_st`)
are duplicated where needed rather than hoisted into a conftest — plain functions, no fixtures, as
the plan requires. All 42 original test functions moved with their assertions unchanged (verified by
AST diff: only `study.EXDIR/STATE` → `settings.*` lines differ); `test_the_api_reports_its_health`
is new, so 43 tests / 136 asserts. The API driver now copies the drill into `<tmp>/exercises/` and
sets `settings.root = tmp`. `testpaths = ["tests", "exercises"]`, `python_files` unchanged, ruff
per-file-ignores `"src/study/*" = ["DTZ"]`.

### 7. Docker

`Dockerfile` (`python:3.13-slim`, uv copied from `ghcr.io/astral-sh/uv:latest`, `uv sync --frozen
--no-dev`, non-root uid 1000, `STUDY_ROOT=/data STUDY_HOST=0.0.0.0 STUDY_OPEN_BROWSER=0`,
`EXPOSE 8765`, `HEALTHCHECK` via `urllib.request.urlopen(.../api/health)`, `CMD ["study"]`), with the
node build stage commented out for Task 6. `compose.yaml` (service `study`, `build: .`,
`ports: ["127.0.0.1:8765:8765"]`, the two bind mounts). `.dockerignore` as specified.

### 8. CI

`.github/workflows/ci.yml`: push/PR → `actions/checkout@v4`, `astral-sh/setup-uv@v5` (cache on),
`uv sync`, `uv run ruff check .`, `uv run pytest tests -q`, `uv run study selfcheck`. Parses as valid
YAML.

### 9. STUDY.md

Only the top command block was replaced (`uv run study`, `uv run study selfcheck`,
`uv run pytest exercises/ex_019_counter.py`, `docker compose up`). The prose pass stays in Task 8.

## Decisions taken (brief was open to reading)

1. **`web_dist`.** The brief says `<package parent>/web/dist`, which read literally is
   `src/web/dist`. The plan everywhere else puts the Vite project at the repo-root `web/` with
   `build.outDir = dist`, and the Dockerfile copies `web/`. I resolved it to
   `PKG.parent.parent / "web" / "dist"` = `<repo>/web/dist` (and `/app/web/dist` in the image):
   package-relative, never under `STUDY_ROOT`, and it is where Task 6 will actually build. Neither
   reading changes behaviour today (the directory does not exist yet, so nothing is mounted and `/`
   returns a JSON 404 — the `web/index.html` placeholder is no longer served, as the brief's mount
   target is `web/dist`).
2. **Health test count.** The brief's verification says "42 passed (43 with the health assert)", so
   the health check is its own test function through the same temp-root driver → 43 passed.
3. **`test_load_fills_in_the_keys_an_older_file_lacks`** went to `tests/test_attempts.py`; the
   Architecture tree lists no `test_state.py` and attempts are the state file's main writer.
4. **Bad-root failure message** lives in `cli.main()` (one check, before either subcommand), so both
   `serve` and `selfcheck` fail the same way.
5. **`Dockerfile` copies `web/`, not `web/dist`.** "Copy `web/dist` if present" has no safe
   single-source form (`COPY web/dis[t]` fails the build outright when nothing matches, and Docker is
   not installed here to test the glob). `COPY web/ ./web/` always succeeds, carries `dist` when the
   host has built it, and only `web/dist` is ever served. Task 6 replaces the line with
   `COPY --from=web /build/dist ./web/dist`.
6. **Boot smoke test ran with `STUDY_OPEN_BROWSER=0`** so it would not throw a browser window at
   Daniel's desktop. The browser path itself is unchanged code.

## Verification (all run on the committed tree)

```
$ uv run pytest tests -q
...........................................                              [100%]
43 passed in 3.00s

$ uv run ruff check .
All checks passed!

$ uv run study selfcheck
87/87 ok

$ uv run python -m study --help
usage: study [-h] [{serve,selfcheck}]

Spaced-repetition Python drills.

positional arguments:
  {serve,selfcheck}  serve the web UI (default), or solve every drill with its
                     reference

options:
  -h, --help         show this help message and exit

$ STUDY_ROOT=/tmp/x uv run study selfcheck
no exercises/ under /tmp/x — run study from the repo, or point STUDY_ROOT at the directory that holds it
exit=1

$ git status --short
(clean)
```

Boot smoke test (PID 358051, killed by PID afterwards; port confirmed closed):

```
$ STUDY_OPEN_BROWSER=0 nohup uv run study > /tmp/study_boot2.log 2>&1 &
PID=358051
$ curl -s http://127.0.0.1:8765/api/health
{"status":"ok","exercises":87,"root":"/home/daniel/study"}
$ curl -s -o /dev/null -w '%{http_code}' -H 'Host: evil.com' http://127.0.0.1:8765/api/catalogue
400
$ curl -s -o /dev/null -w '%{http_code}' -H 'Host: localhost:8765' http://127.0.0.1:8765/api/catalogue
200

study → http://127.0.0.1:8765/   (ctrl-c to stop)
INFO:     Started server process [358057]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8765 (Press CTRL+C to quit)
INFO:     127.0.0.1:37298 - "GET /api/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:37308 - "GET /api/catalogue HTTP/1.1" 400 Bad Request
INFO:     127.0.0.1:37312 - "GET /api/catalogue HTTP/1.1" 200 OK
INFO:     Shutting down
```

`progress.json` and `exercises/` are byte-unchanged (`git status` clean after every run, including
selfcheck, which creates and removes its `_selfcheck_*.py` files).

## Files changed

Added: `src/study/{__init__,__main__,api,attempts,catalogue,cli,region,runner,scheduler,settings,state}.py`,
`tests/test_{region,catalogue,scheduler,attempts,runner,api}.py`, `Dockerfile`, `compose.yaml`,
`.dockerignore`, `.github/workflows/ci.yml`.
Modified: `pyproject.toml`, `uv.lock`, `STUDY.md` (command block only).
Deleted: `study.py`, `web.py`, `test_study.py`, `main.py`.
Untouched: `exercises/**`, `progress.json`, `web/index.html`.

## Self-review findings

- Steps 1–9 are all implemented; the AST diff above is the evidence that nothing was rewritten that
  only needed moving.
- Behaviour parity: same routes, same status codes, same payload keys, same grading and splice code.
  The three deliberate behaviour additions are `/api/health`, the log lines, and `serve()` honouring
  the new env vars.
- Test output is pristine — 43 passed, no warnings, no skips.
- Inline comment columns shifted by a few characters in `api.py` where the `study.` prefix went away;
  I re-aligned the worst offenders and left the rest.
- `region.py`'s docstring was reworded (it is not "no disk" — `write_region` writes), and `api.py`'s
  now names `region`/`scheduler`/`attempts` instead of `study.py`.

## Concerns / not verifiable here

1. **`progress.json` as a single-file bind mount (compose).** `save()` writes `progress.tmp` and
   renames it over the target; renaming onto a single-file bind mount can fail with `EBUSY`, which
   would break every state write inside the container. I kept the mounts the brief specifies and
   marked the ceiling with a `# ponytail:` comment in `compose.yaml` naming the fix (`- ./:/data`).
   Untestable here — Docker is not installed.
2. **Docker build unverified** (no Docker on this box): the uv-copy line, `uv sync --frozen --no-dev`,
   the healthcheck and `COPY web/`. One assumption worth naming: `uv sync` installs the project in
   editable mode, so in the image `study/__init__.py` lives at `/app/src/study` and `web_dist`
   resolves to `/app/web/dist`. If a future uv installs non-editably, `web_dist` would point into
   `site-packages/../web/dist` and the page would not be served (the API would still work).
3. **CI unrun** — no GitHub runner here; the YAML parses and every command in it passes locally.
4. `/` returns a JSON 404 until Task 6 builds `web/dist`; the old `web/index.html` placeholder is no
   longer reachable. Deliberate: the brief points the mount at `web/dist`.
