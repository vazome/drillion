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
9. `STUDY.md` command block only (`uv run study`, `uv run study selfcheck`, `uv run pytest
   exercises/ex_019_counter.py`, `docker compose up`); the full doc pass stays in Task 8.

Verification (paste outputs): `uv run pytest tests -q` → 42 passed (43 with the health assert),
no warnings; `uv run ruff check .` clean; `uv run study selfcheck` → 87/87; `uv run study` boots
(record PID, `curl -s http://127.0.0.1:8765/api/health`, `curl -s -o /dev/null -w '%{http_code}'
-H 'Host: evil.com' …/api/catalogue` → 400, kill by PID); `python -m study --help` works;
`git status` clean; `STUDY_ROOT=/tmp/x uv run study selfcheck` fails loudly with a clear message
(no exercises dir). Commits: `Restructure into the study package`, `Docker image, compose and CI`.

