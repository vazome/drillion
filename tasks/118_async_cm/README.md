---
title: async context manager — build a FakePool
difficulty: hard
tier: advanced
minutes: 25
prereqs: [57, 73, 89]
tags: [concurrency, asyncio]
---
# async context manager — build a FakePool

*Build a FakePool yourself — an async context manager around a semaphore.*

## Read first
- [Using the async with Statement / Creating Custom Context Managers](https://realpython.com/python-with-statement/) — `__enter__`/`__exit__` first, then the async twins
- [Asynchronous context managers](https://devdocs.io/python~3.14/reference/datamodel#asynchronous-context-managers) — the two methods Python calls: `__aenter__` on the way in, `__aexit__` on the way out (ALWAYS, even on error)
- [contextlib.asynccontextmanager](https://devdocs.io/python~3.14/library/contextlib#contextlib.asynccontextmanager) — the shorter way: one async generator with a single `yield`

## Why
A test suite that must run without a real Postgres still has to let `async with pool.acquire() as conn:` in the endpoint work unchanged. The usual answer is a FakePool: a Semaphore for the slots and a canned list of rows behind the same two methods asyncpg's pool exposes. That means knowing what `__aenter__` and `__aexit__` are, and why the slot is given back even when the body raises. This task builds one from nothing.

## You get
nothing to start — you return a CLASS. The test builds it as `FakePool(rows, max_size)` where:

- `rows` — the list the fake database will always answer with, e.g. `[{"id": 1, "content": "storage best practices"}]`
- `max_size` — how many callers may hold a connection at the same time

## You return
the class. The test uses it exactly like asyncpg's pool:

```python
async with pool.acquire() as conn:
    got = await conn.fetch("SELECT ...", 1, 2)   # -> rows
```

## Rules
- `pool.acquire()` is a plain method returning something usable in `async with`. Returning `self` is the lazy, fine answer.
- Entering waits for a free slot (`Semaphore(max_size)`); leaving gives the slot back — also when the body raised an exception.
- The object bound by `as conn` has `async def fetch(self, sql, *params)` that ignores its arguments and returns `rows`.

> [!WARNING]
> With `max_size=1`, entering twice in a row must work (second entry follows the first exit); entering while another caller holds the slot must wait, not raise.

## Hints
### Hint 1
Skeleton: `__init__` stores `rows` and `self.slots = asyncio.Semaphore(max_size)`. `def acquire(self): return self`. `async def __aenter__(self)`: `await self.slots.acquire(); return self`. `async def __aexit__(self, *exc)`: `self.slots.release()`. `async def fetch(self, sql, *params)`: `return self.rows`.
### Hint 2
Why `*exc` in `__aexit__`: Python passes three values (exception type, value, traceback) when the body raised, or three `None`s when it did not. You do not care which — release either way. Returning `None` (not `True`) lets the exception keep propagating, which is what you want in a test.
### Hint 3
**Say it in the interview:**

> async with calls __aenter__ to take the resource and __aexit__ to give it back, and __aexit__ runs whether the body returned or raised — it is the async version of try/finally. A FakePool built on a Semaphore lets max_size callers hold a slot at once, which is enough to reproduce pool starvation in a test with no database.
