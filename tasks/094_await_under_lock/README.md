---
title: take-home Task 1 — embed before you borrow
minutes: 20
prereqs: [56]
tags: [concurrency, asyncio, rsample]
---
# take-home Task 1 — embed before you borrow

*Take-home Task 1 — do the slow wait BEFORE you borrow the connection.*

## Why
This is the bug you fixed in the take-home, rebuilt small. The `/search` endpoint borrowed a database connection from a pool of 5, and THEN waited 80 ms for the embedding API while still holding it. Under 200 concurrent requests only 5 could be "inside" at a time, so the 80 ms waits ran five at a time instead of all at once: 40 rounds x 80 ms is over 3 seconds of pure queueing. The connection did nothing during that wait. Moving the embedding call before the borrow lets all 200 waits overlap, and the connection is held only for the few ms the query needs.

## You get
nothing to start — you return an async function. The test then calls it as `await search(q, pool, embed)` many times at once, where:

- `q` — the query string, e.g. `"storage best practices"`
- `pool` — a stand-in pool: `async with pool.acquire() as conn:` gives you a `conn`, and only 2 callers can hold one at a time
- `embed` — an async function: `await embed(q)` returns the vector (a list). The stand-in pretends to be the slow network call.
- `conn.fetch(vector)` — async; returns the rows for that vector.

## You return
`search` must return whatever `conn.fetch(vector)` returned.

## Rules
- `search` is `async def search(q, pool, embed)`.
- It awaits `embed(q)` BEFORE entering `async with pool.acquire()`.
- Inside the `async with`, it awaits `conn.fetch(vector)` and returns the rows (returning after the block ends is fine too).

> [!WARNING]
> The test checks the ORDER of events, not a stopwatch: when 20 searches start together, all 20 embeds must have started before any connection is taken.

## Read first
- [Async IO Explained](https://realpython.com/async-io-python/) — an `await` is a place where this request pauses and lets OTHER requests run. Nothing else matters as much as that sentence.
- [asyncpg connection pools](https://magicstack.github.io/asyncpg/current/usage.html#connection-pools) — the real pool you used: a fixed number of database connections, handed out one per `async with pool.acquire()`
- [asyncio.Semaphore](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore) — the test's fake pool is just this: a counter of free slots
- [The async with statement](https://docs.python.org/3/reference/compound_stmts.html#the-async-with-statement)

> [!NOTE]
> **Take-home:** `embed_query` outside `pool.acquire()`

## Hints
### Hint 1
Write the three lines in the order the README told you: get the vector, then `async with pool.acquire() as conn:`, then fetch. The bug was only ever the order of the first two. If your embed line is indented under the `async with`, it is inside the borrow — move it up one level.
### Hint 2
Why order matters: `await embed(q)` pauses this request and lets the next request run. If the pause happens while you hold a slot, the next request blocks on `acquire()` instead of starting its own embed. If the pause happens first, every request reaches its embed immediately.
### Hint 3
**Say it in the interview:**

> The connection was acquired and then held across an await that had nothing to do with the database. With a pool of 5 that serialised the 80 ms embedding wait five at a time. I moved the embed call before pool.acquire(), so the waits overlap and each connection is held only for the query itself. Raising max_size would hide the symptom; the DB would still be starved of connections by callers who are not using them.
