---
title: lazy init under a lock — why db.py has asyncio.Lock
minutes: 20
prereqs: [56, 95]
tags: [concurrency, asyncio, rsample]
---
# lazy init under a lock — why db.py has asyncio.Lock

*app/db.py explained — create the pool once, even when 50 requests arrive together.*

## Why
The take-home's `app/db.py` created the connection pool lazily — on the first request, not at import — and guarded that creation with an `asyncio.Lock`. You did not write that file, but you shipped it, and an interviewer will ask "why is the lock there, and why is `_pool is None` checked twice?" The answer: `await create_pool()` pauses. In that pause the other 49 first-arrivers each see `_pool is None` too and each create their own pool — 50 pools, 250 connections, on a server allowed 100.

## You get
nothing to start — you return an async function. The test calls it as `await get_pool(create)` from many coroutines at once, where:

- `create` — an async function with no arguments; `await create()` is the slow "open the real pool" step. It returns a new object every time it is called, and the test counts how often it runs.

## You return
`get_pool` returns the pool object — the SAME object to every caller, forever after the first call.

## Rules
- `create()` is awaited exactly once, no matter how many callers arrive together or later.
- Every caller gets the identical object (`is`, not just `==`).
- Keep the state inside `solve()` (variables the inner function closes over, with `nonlocal`), so each `solve()` call starts fresh.
- Use `asyncio.Lock()`; check `pool is None` before taking the lock AND again inside it. The first check skips the lock on the fast path; the second stops the callers who were queued behind the winner from creating a second pool.

## Read first
- [asyncio.Lock](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Lock) — one holder at a time; `async with lock:` is the whole API you need
- [Double-checked locking](https://en.wikipedia.org/wiki/Double-checked_locking) — read only 'Motivation and original pattern': check, lock, check again. (Ignore the Java memory-model parts.)
- [Async IO Explained](https://realpython.com/async-io-python/) — why an `await` is a gap where another request can sneak in between your `if` and your assignment

> [!NOTE]
> **Take-home:** `app/db.py` (given — you must explain it)

## Hints
### Hint 1
Skeleton inside `solve()`: `pool = None`, `lock = asyncio.Lock()`, then `async def get_pool(create): nonlocal pool; if pool is None: async with lock: if pool is None: pool = await create(); return pool`. Return `get_pool`.
### Hint 2
Why the second `if`: 49 callers queue on the lock while the first awaits `create()`. When the first releases, the next enters the lock — without the inner check it would create again. Without the lock at all, nobody queues: all 50 pass the first check during the winner's await and all 50 create.
### Hint 3
**Say it in the interview:**

> The pool is created lazily, and await create_pool() yields to the event loop, so concurrent first requests would each see None and each open a pool. The lock makes creation exclusive; the outer check keeps the steady state lock-free; the inner check stops the callers queued behind the winner from creating a second pool. It is double-checked locking, and in asyncio it is safe because there is one thread and the only switch points are the awaits.
