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
8. `STUDY.md`: delete the "Take-home track" section; add a "Tags" section (vocabulary above, the
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

