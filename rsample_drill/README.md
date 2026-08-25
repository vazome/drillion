# rsample take-home track — go top to bottom

Goal: explain every line and every decision of your RAG take-home in an interview.
Each file starts with `# READ FIRST:` links — read them BEFORE opening the task.
The last hint of every new drill is "SAY IT IN THE INTERVIEW" — the sentences to say out loud.

```bash
STUDY_DIR=rsample_drill uv run study.py          # what to do now
STUDY_DIR=rsample_drill uv run study.py check    # grade it
STUDY_DIR=rsample_drill uv run study.py hint     # stuck
uv run pytest rsample_drill/ex_09_await_under_lock.py   # or just run one file
```

| # | file | what you learn | in the take-home |
|---|---|---|---|
| 01 | sortkey | `sorted(key=..., reverse=True)`, ties keep order | `sorted(rows, key=score)` in main.py |
| 02 | sets | intersection `&` | `query_words & content_words` in reranker.py |
| 03 | regex | `re.sub` to strip punctuation | `_tokenize` in reranker.py |
| 04 | typehints | `-> list[dict[str, Any]]` etc. | required on every signature |
| 05 | decorators | what `@something` does to a function | `@app.get("/search")`, `@pytest.fixture` |
| 06 | contextmanager | `with` = setup / body / guaranteed cleanup | the sync half of `async with pool.acquire()` |
| 07 | concurrency | threads vs processes vs asyncio | "why async here?" |
| 08 | asyncio | `gather`: start all, collect in order | `loadtest.py`, your concurrency test |
| 09 | **await_under_lock** | the Task 1 bug, rebuilt small | `embed_query` outside `pool.acquire()` |
| 10 | **semaphore** | at most N in flight | why `FakePool` is a `Semaphore(max_size)` |
| 11 | **async_cm** | build `FakePool`: `__aenter__` / `__aexit__` | your `tests/test_search.py` |
| 12 | **lazy_init_lock** | `asyncio.Lock` + double check | `app/db.py` (given — you must explain it) |
| 13 | mock | swap a real function for a fake in a test | `monkeypatch.setattr(...)` |
| 14 | **fixtures** | one setup, automatic restore | what the README asked and you skipped |
| 15 | **asgi_test** | call FastAPI in-process, no server | `httpx.ASGITransport(app=app)` |
| 16 | **rerank** | wide retrieve → fraction score → stable top-k | Task 2 + the "fraction, not count" upgrade |
| 17 | whattotest | what deserves a test | Task 3 judgement |
| 18 | **explain_takehome** | ten interview questions, pick the answer | the interview |

Bold = new, written around the take-home. Plain = copies of the general drills you need first.
