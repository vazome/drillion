---
title: async context manager — your own FakePool
minutes: 25
prereqs: [13, 56]
tags: [concurrency, asyncio, rsample]
---
# async context manager — your own FakePool

*Build the FakePool yourself — an async context manager around a semaphore.*

## Why
In the take-home tests you could not use a real Postgres. You
wrote a FakePool class so that `async with pool.acquire() as conn:` in
the endpoint kept working unchanged, but behind it was a Semaphore and
a canned list of rows. An interviewer will point at `__aenter__` and
`__aexit__` and ask what they are and why the slot is given back even
when the body raises. This drill makes you build it from nothing.

## You get
nothing to start — you return a CLASS. The test builds it as
`FakePool(rows, max_size)` where:
  `rows`     — the list the fake database will always answer with,

```
e.g. [{"id": 1, "content": "storage best practices"}]
```

  `max_size` — how many callers may hold a connection at the same time

## You return
the class. The test uses it exactly like asyncpg's pool:

```python
async with pool.acquire() as conn:
    got = await conn.fetch("SELECT ...", 1, 2)   # -> rows
```

## Rules
  - `pool.acquire()` is a plain method returning something usable in
    `async with`. Returning `self` is the lazy, fine answer.
  - Entering waits for a free slot (Semaphore(max_size)); leaving gives
    the slot back — also when the body raised an exception.
  - The object bound by `as conn` has `async def fetch(self, sql, *params)`
    that ignores its arguments and returns `rows`.
  - With max_size=1, entering twice in a row must work (second entry
    follows the first exit); entering while another caller holds the slot
    must wait, not raise.

## Read first
- https://realpython.com/python-with-statement/  — section 'Using the async with Statement' and 'Creating Custom Context Managers' (__enter__/__exit__ first, then the async twins)
- https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers  — the two methods Python calls: __aenter__ on the way in, __aexit__ on the way out (ALWAYS, even on error)
- https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager  — the shorter way: one async generator with a single `yield`

> [!NOTE]
> **Take-home:** your `tests/test_search.py`

## Hints
### Hint 1
Skeleton: __init__ stores rows and `self.slots = asyncio.Semaphore(max_size)`. `def acquire(self): return self`. `async def __aenter__(self)`: await self.slots.acquire(); return self. `async def __aexit__(self, *exc)`: self.slots.release(). `async def fetch(self, sql, *params)`: return self.rows.
### Hint 2
Why `*exc` in __aexit__: Python passes three values (exception type, value, traceback) when the body raised, or three Nones when it did not. You do not care which — release either way. Returning None (not True) lets the exception keep propagating, which is what you want in a test.
### Hint 3
SAY IT IN THE INTERVIEW: 'async with calls __aenter__ to take the resource and __aexit__ to give it back, and __aexit__ runs whether the body returned or raised — it is the async version of try/finally. My FakePool used a Semaphore so max_size callers can hold a slot at once; that is enough to reproduce the pool-starvation bug in a test without a database.'
