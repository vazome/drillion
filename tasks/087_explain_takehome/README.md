---
title: explain the take-home — ten interview questions
difficulty: easy
tier: core
track: rsample
minutes: 15
prereqs: [80, 86]
tags: [concurrency]
---
# explain the take-home — ten interview questions

*The interview itself — ten questions a reviewer will ask about your take-home.*

## Why
You submitted this code. The reviewer's job is to find out whether you understand it, and the README said submissions that look AI-written are disqualified. Every question below is one they can ask while pointing at a line of your diff. Pick the answer you would say out loud. No code to write — the test is whether your mental model is right.

## You get
nothing.

## You return
a dict `{question_number: letter}`, e.g.

```python
solve()
# -> {1: "b", 2: "a", 3: "b", 4: "b", 5: "c",
#     6: "b", 7: "c", 8: "b", 9: "b", 10: "b"}
```

with all ten answered.

## Rules
Ten questions, each with one correct answer. Pick the letter you would say out loud.

### Q1
200 concurrent requests, pool of 5, each request awaited an 80 ms embedding call. Why did it take seconds?

- a) Postgres was slow under load
- b) each request held a connection during the 80 ms wait, so only 5 waits ran at once: 40 rounds x 80 ms
- c) httpx limited the load test to 5 connections
- d) Python's GIL serialised the requests

### Q2
Why is raising max_size to 200 not the fix?

- a) asyncpg caps pools at 100
- b) it would still pass the test but the README forbids it
- c) it hides the cause: connections are still wasted on a wait that does not need them, and the database's connection limit is hit sooner
- d) creating 200 connections takes longer than 4 s

### Q3
Why not `asyncio.gather(embed_query(q), conn.fetch(...))` to run both at once?

- a) gather only accepts tasks, not coroutines
- b) fetch needs the vector that embed produces — they depend on each other, so they cannot overlap
- c) gather inside a pool context is not allowed
- d) it would work, but the README asked for sequential code

### Q4
`app/db.py` checks `_pool is None`, takes an `asyncio.Lock`, and checks again. What does the lock prevent?

- a) two queries running on the same connection
- b) many first-arriving requests each creating their own pool, because `await create_pool()` yields between the check and the assignment
- c) a deadlock between the pool and the event loop
- d) nothing in asyncio — it is only needed with threads

### Q5
Why did your concurrency test use a FakePool built on `Semaphore(2)`?

- a) semaphores are faster than real connections
- b) pytest requires fakes to be context managers
- c) it models a limited pool, so holding a slot during a slow await visibly serialises callers and the test fails against the bug
- d) to avoid importing asyncpg

### Q6
In FakePool, why is the slot released even when the body raises?

- a) the garbage collector releases it
- b) `__aexit__` runs on normal exit AND on exception, like `finally`
- c) asyncio cancels the context on error
- d) it is not — that is a known leak in the test

### Q7
The README asked for fixtures. Why is a fixture better than repeating the monkeypatch lines in every test?

- a) fixtures run faster because pytest caches them
- b) ruff flags repeated code
- c) one place for setup, automatic teardown (monkeypatch restores the originals), and tests that state only the behaviour they check
- d) fixtures are required for async tests

### Q8
Why add a reranking stage instead of returning vector order?

- a) vector search is unreliable and should be replaced
- b) stage one is cheap and wide (recall); stage two is costlier and narrow (precision); the latency cost is 20 cheap score calls
- c) Postgres cannot sort by distance correctly
- d) reranking is needed to deduplicate chunks

### Q9
Your score was a raw count of overlapping words. What does a fraction of the query's words improve?

- a) nothing — they sort identically within one request
- b) it is bounded 0..1 and comparable across queries of different length, so thresholds and logging mean the same thing everywhere
- c) it handles synonyms
- d) it is faster to compute

### Q10
Why `httpx.ASGITransport` in the tests?

- a) it is faster than TestClient
- b) it calls the FastAPI app in-process — real routing and validation, no server, port or network — so `pytest` alone runs the suite
- c) TestClient does not support query parameters
- d) it mocks the database automatically

## Read first
These are the ones the questions come from — re-read, then answer from memory.

- [Async IO Explained](https://realpython.com/async-io-python/)
- [asyncpg connection pools](https://magicstack.github.io/asyncpg/current/usage.html#connection-pools)
- [asyncio synchronization primitives](https://docs.python.org/3/library/asyncio-sync.html) — Lock and Semaphore
- [Asynchronous context managers](https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers)
- [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [FastAPI async tests](https://fastapi.tiangolo.com/advanced/async-tests/)
- [Rerankers](https://www.pinecone.io/learn/series/rag/rerankers/)
- [Precision and recall](https://en.wikipedia.org/wiki/Precision_and_recall)

> [!NOTE]
> **Take-home:** the interview

## Hints
### Hint 1
Answer 1, 2 and 3 first: they are all the same fact seen from three sides — an await pauses THIS request and lets others run, so a resource held across an await that does not need it is a resource stolen from everyone else.
### Hint 2
For 4-7: every 'why' about the tests is about what happens BETWEEN awaits or AFTER the body — the lock guards the gap inside create_pool(); __aexit__ and fixture teardown both run whatever happened in the body.
### Hint 3
**Say it in the interview** (the whole story in 6 sentences):

> The endpoint held a pooled connection across the embedding await, so a pool of 5 serialised 200 requests into 40 rounds; I moved the embed before acquire. A bigger pool only hides it. The test reproduces it with a Semaphore-based fake pool and concurrent callers. The lazy pool init needs a lock because await create_pool yields mid-check. Reranking trades 20 cheap score calls for precision over a recall-oriented vector stage. I would move the test setup into a fixture and score by fraction rather than count.
