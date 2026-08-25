"""asyncio.Semaphore — run many jobs at once, but never more than N at a time."""
# READ FIRST:
#   https://superfastpython.com/asyncio-semaphore/  — what a semaphore is, with runnable examples;
#       read up to 'Example of Using an Asyncio Semaphore'
#   https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore  — the 6-line reference
#   https://docs.python.org/3/library/asyncio-task.html#asyncio.gather  — start everything, collect in order

import asyncio
import inspect

from _lib import rng

META = {"topic": 10, "title": "semaphore — at most N in flight", "tier": 4,
        "minutes": 20, "prereqs": []}


def solve():
    """WHY: A connection pool is exactly this idea: N slots, and the (N+1)th
    caller waits until someone gives one back. Your take-home test built a
    FakePool with `asyncio.Semaphore(max_size)` for that reason — to imitate
    a pool of 2 without a database. The same tool is what you reach for when
    a vendor API says "no more than 5 requests at a time" or when 500 hosts
    must be pinged without opening 500 sockets.

    YOU GET: nothing to start — you return an async function. The test calls
    it as `await run_all(fn, items, limit)`, where:
      `fn`    — an async function; `await fn(item)` does the work for one item
      `items` — a list, e.g. ["host-1", "host-2", ...]
      `limit` — a whole number: the most `fn` calls allowed to be running at
                the same moment

    YOU RETURN: a list of results, one per item, in the SAME order as items.

    ─── exact rules ───
      - All items are launched together (one coroutine each), not one after
        another — a plain `for` loop with `await fn(item)` inside fails.
      - At any moment no more than `limit` calls of `fn` are in progress.
        With limit=3 and 10 items, exactly 3 are running as soon as it
        starts, never 4.
      - Results keep item order even if later items finish first.
    """
    raise NotImplementedError


HINTS = [
    ("Make one `asyncio.Semaphore(limit)`. Write a small inner `async def one(item)` "
    "that does `async with sem:` and inside it `return await fn(item)`. Then "
    "`gather` one `one(item)` per item — gather returns results in call order."),
    ("Why the semaphore must wrap the await and not just the call: `async with sem` "
    "takes a slot on entry and gives it back on exit, so the slot is held for the "
    "whole `await fn(item)`. If you release before the await, everything runs at "
    "once and the limit is a lie."),
    ("SAY IT IN THE INTERVIEW: 'A semaphore is a counter of free slots. acquire "
    "takes one or waits; release gives it back. Wrapping each job in async with "
    "sem bounds how many are in flight while gather still launches them all and "
    "returns results in order. That is the same mechanism as a connection pool, "
    "which is why my FakePool in the tests was a Semaphore(max_size).'"),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    items = [f"host-{i}" for i in range(r.randint(6, 12))]
    return items, r.randint(2, 4)


def _reference():
    async def run_all(fn, items, limit):
        sem = asyncio.Semaphore(limit)

        async def one(item):
            async with sem:
                return await fn(item)

        return await asyncio.gather(*(one(i) for i in items))

    return run_all


def test_solve():
    r = rng()
    run_all = solve()
    assert inspect.iscoroutinefunction(run_all), "solve() must return an async def"
    for _ in range(3):
        items, limit = _gen(r)
        state = {"now": 0, "peak": 0, "started": []}

        async def fn(item, _s=state):
            _s["started"].append(item)
            _s["now"] += 1
            _s["peak"] = max(_s["peak"], _s["now"])
            await asyncio.sleep(0.003 if item.endswith("1") else 0.001)  # some finish early
            _s["now"] -= 1
            return item.upper()

        results = asyncio.run(run_all(fn, list(items), limit))
        assert results == [i.upper() for i in items], "results must keep item order"
        assert state["peak"] <= limit, f"{state['peak']} ran at once, limit was {limit}"
        assert state["peak"] == limit, (
            f"only {state['peak']} ran at once with limit={limit}: you are running "
            "jobs one after another instead of launching them all"
        )
