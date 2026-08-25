"""Take-home Task 1 — do the slow wait BEFORE you borrow the connection."""
# READ FIRST:
#   https://realpython.com/async-io-python/  — 'Async IO Explained': an `await` is a place where
#       this request pauses and lets OTHER requests run. Nothing else matters as much as that sentence.
#   https://magicstack.github.io/asyncpg/current/usage.html#connection-pools  — the real pool you used:
#       a fixed number of database connections, handed out one per `async with pool.acquire()`
#   https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore  — the test's fake pool is
#       just this: a counter of free slots
#   https://docs.python.org/3/reference/compound_stmts.html#the-async-with-statement
#   TAKE-HOME: `embed_query` outside `pool.acquire()`

import asyncio
import inspect

from _lib import rng

META = {"topic": 94, "title": "take-home Task 1 — embed before you borrow", "tier": 4,
        "minutes": 20, "prereqs": [56], "tags": ["concurrency", "asyncio", "rsample"]}


def solve():
    """WHY: This is the bug you fixed in the take-home, rebuilt small. The
    `/search` endpoint borrowed a database connection from a pool of 5, and
    THEN waited 80 ms for the embedding API while still holding it. Under
    200 concurrent requests only 5 could be "inside" at a time, so the 80 ms
    waits ran five at a time instead of all at once: 40 rounds x 80 ms is
    over 3 seconds of pure queueing. The connection did nothing during that
    wait. Moving the embedding call before the borrow lets all 200 waits
    overlap, and the connection is held only for the few ms the query needs.

    YOU GET: nothing to start — you return an async function. The test then
    calls it as `await search(q, pool, embed)` many times at once, where:
      `q`     — the query string, e.g. "storage best practices"
      `pool`  — a stand-in pool: `async with pool.acquire() as conn:` gives
                you a `conn`, and only 2 callers can hold one at a time
      `embed` — an async function: `await embed(q)` returns the vector (a
                list). The stand-in pretends to be the slow network call.
      `conn.fetch(vector)` — async; returns the rows for that vector.

    YOU RETURN: `search` must return whatever `conn.fetch(vector)` returned.

    ─── exact rules ───
      - `search` is `async def search(q, pool, embed)`.
      - It awaits `embed(q)` BEFORE entering `async with pool.acquire()`.
      - Inside the `async with`, it awaits `conn.fetch(vector)` and returns
        the rows (returning after the block ends is fine too).
      - The test checks the ORDER of events, not a stopwatch: when 20
        searches start together, all 20 embeds must have started before any
        connection is taken.
    """
    raise NotImplementedError


HINTS = [
    ("Write the three lines in the order the README told you: get the vector, "
    "then `async with pool.acquire() as conn:`, then fetch. The bug was only "
    "ever the order of the first two. If your embed line is indented under "
    "the `async with`, it is inside the borrow — move it up one level."),
    ("Why order matters: `await embed(q)` pauses this request and lets the "
    "next request run. If the pause happens while you hold a slot, the next "
    "request blocks on `acquire()` instead of starting its own embed. If the "
    "pause happens first, every request reaches its embed immediately."),
    ("SAY IT IN THE INTERVIEW: 'The connection was acquired and then held "
    "across an await that had nothing to do with the database. With a pool "
    "of 5 that serialised the 80 ms embedding wait five at a time. I moved "
    "the embed call before pool.acquire(), so the waits overlap and each "
    "connection is held only for the query itself. Raising max_size would "
    "hide the symptom; the DB would still be starved of connections by "
    "callers who are not using them.'"),
]


# ─────────────────────────────  below here is the machinery  ──────────────

class _Conn:
    def __init__(self, log):
        self.log = log

    async def fetch(self, vector):
        self.log.append(("fetch", vector[0]))
        return [{"id": vector[0], "content": f"chunk-{vector[0]}"}]


class _Pool:
    """Stand-in for asyncpg's pool: `max_size` slots, counted by a Semaphore."""

    def __init__(self, log, max_size=2):
        self.log = log
        self.slots = asyncio.Semaphore(max_size)

    def acquire(self):
        return self

    async def __aenter__(self):
        await self.slots.acquire()
        self.log.append(("acquire",))
        return _Conn(self.log)

    async def __aexit__(self, *exc):
        self.log.append(("release",))
        self.slots.release()


def _gen(r):
    return [r.randint(100, 999) for _ in range(r.randint(12, 20))]


def _reference():
    async def search(q, pool, embed):
        vector = await embed(q)
        async with pool.acquire() as conn:
            rows = await conn.fetch(vector)
        return rows

    return search


def test_solve():
    r = rng()
    search = solve()
    assert inspect.iscoroutinefunction(search), "solve() must return an async def"
    for _ in range(3):
        qs = _gen(r)
        log = []

        async def embed(q, _log=log):
            _log.append(("embed_start", q))
            await asyncio.sleep(0.002)
            _log.append(("embed_done", q))
            return [q]

        async def main():
            pool = _Pool(log, max_size=2)  # noqa: B023
            return await asyncio.gather(*(search(q, pool, embed) for q in qs))  # noqa: B023

        rows = asyncio.run(main())
        assert rows == [[{"id": q, "content": f"chunk-{q}"}] for q in qs], "wrong rows returned"
        kinds = [e[0] for e in log]
        first_acquire = kinds.index("acquire")
        started_before = kinds[:first_acquire].count("embed_start")
        assert started_before == len(qs), (
            f"only {started_before}/{len(qs)} embeds had started when the first "
            "connection was taken — you are awaiting embed() while holding the slot"
        )
        assert kinds.count("release") == len(qs), "every acquire must be released"
