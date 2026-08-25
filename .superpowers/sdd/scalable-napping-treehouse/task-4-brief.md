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

