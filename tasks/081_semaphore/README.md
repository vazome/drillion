---
title: semaphore — at most N in flight
difficulty: hard
tier: advanced
track: rsample
minutes: 20
prereqs: [53]
tags: [concurrency, asyncio]
---
# semaphore — at most N in flight

*asyncio.Semaphore — run many jobs at once, but never more than N at a time.*

## Read first
- [Example of Using an Asyncio Semaphore](https://superfastpython.com/asyncio-semaphore/) — what a semaphore is, with runnable examples; read up to 'Example of Using an Asyncio Semaphore'
- [asyncio.Semaphore](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore) — the 6-line reference
- [asyncio.gather](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) — start everything, collect in order

> [!NOTE]
> **Take-home:** why `FakePool` is a `Semaphore(max_size)`

## Why
A connection pool is exactly this idea: N slots, and the (N+1)th caller waits until someone gives one back. Your take-home test built a FakePool with `asyncio.Semaphore(max_size)` for that reason — to imitate a pool of 2 without a database. The same tool is what you reach for when a vendor API says "no more than 5 requests at a time" or when 500 hosts must be pinged without opening 500 sockets.

## You get
nothing to start — you return an async function. The test calls it as `await run_all(fn, items, limit)`, where:

- `fn` — an async function; `await fn(item)` does the work for one item
- `items` — a list, e.g. `["host-1", "host-2", ...]`
- `limit` — a whole number: the most `fn` calls allowed to be running at the same moment

## You return
a list of results, one per item, in the SAME order as items.

## Rules
- All items are launched together (one coroutine each), not one after another — a plain `for` loop with `await fn(item)` inside fails.
- At any moment no more than `limit` calls of `fn` are in progress. With limit=3 and 10 items, exactly 3 are running as soon as it starts, never 4.
- Results keep item order even if later items finish first.

## Hints
### Hint 1
Make one `asyncio.Semaphore(limit)`. Write a small inner `async def one(item)` that does `async with sem:` and inside it `return await fn(item)`. Then `gather` one `one(item)` per item — gather returns results in call order.
### Hint 2
Why the semaphore must wrap the await and not just the call: `async with sem` takes a slot on entry and gives it back on exit, so the slot is held for the whole `await fn(item)`. If you release before the await, everything runs at once and the limit is a lie.
### Hint 3
**Say it in the interview:**

> A semaphore is a counter of free slots. acquire takes one or waits; release gives it back. Wrapping each job in async with sem bounds how many are in flight while gather still launches them all and returns results in order. That is the same mechanism as a connection pool, which is why my FakePool in the tests was a Semaphore(max_size).
