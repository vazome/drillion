"""app/db.py explained — create the pool once, even when 50 requests arrive together."""
# READ FIRST:
#   https://docs.python.org/3/library/asyncio-sync.html#asyncio.Lock  — one holder at a time;
#       `async with lock:` is the whole API you need
#   https://en.wikipedia.org/wiki/Double-checked_locking  — read only 'Motivation and original
#       pattern': check, lock, check again. (Ignore the Java memory-model parts.)
#   https://realpython.com/async-io-python/  — 'Async IO Explained': why an `await` is a gap where
#       another request can sneak in between your `if` and your assignment
#   TAKE-HOME: `app/db.py` (given — you must explain it)

import asyncio
import inspect

from _lib import rng

META = {"topic": 97, "title": "lazy init under a lock — why db.py has asyncio.Lock", "tier": 4,
        "minutes": 20, "prereqs": [56, 95], "tags": ["concurrency", "asyncio", "rsample"]}


def solve():
    """WHY: The take-home's `app/db.py` created the connection pool lazily —
    on the first request, not at import — and guarded that creation with an
    `asyncio.Lock`. You did not write that file, but you shipped it, and an
    interviewer will ask "why is the lock there, and why is `_pool is None`
    checked twice?" The answer: `await create_pool()` pauses. In that pause
    the other 49 first-arrivers each see `_pool is None` too and each create
    their own pool — 50 pools, 250 connections, on a server allowed 100.

    YOU GET: nothing to start — you return an async function. The test calls
    it as `await get_pool(create)` from many coroutines at once, where:
      `create` — an async function with no arguments; `await create()` is the
                 slow "open the real pool" step. It returns a new object every
                 time it is called, and the test counts how often it runs.

    YOU RETURN: `get_pool` returns the pool object — the SAME object to every
    caller, forever after the first call.

    ─── exact rules ───
      - `create()` is awaited exactly once, no matter how many callers arrive
        together or later.
      - Every caller gets the identical object (`is`, not just `==`).
      - Keep the state inside solve() (variables the inner function closes
        over, with `nonlocal`), so each `solve()` call starts fresh.
      - Use `asyncio.Lock()`; check `pool is None` before taking the lock AND
        again inside it. The first check skips the lock on the fast path; the
        second stops the callers who were queued behind the winner from
        creating a second pool.
    """
    raise NotImplementedError


HINTS = [
    ("Skeleton inside solve(): `pool = None`, `lock = asyncio.Lock()`, then "
    "`async def get_pool(create): nonlocal pool; if pool is None: async with lock: "
    "if pool is None: pool = await create(); return pool`. Return get_pool."),
    ("Why the second `if`: 49 callers queue on the lock while the first awaits "
    "create(). When the first releases, the next enters the lock — without the "
    "inner check it would create again. Without the lock at all, nobody queues: "
    "all 50 pass the first check during the winner's await and all 50 create."),
    ("SAY IT IN THE INTERVIEW: 'The pool is created lazily, and await "
    "create_pool() yields to the event loop, so concurrent first requests would "
    "each see None and each open a pool. The lock makes creation exclusive; the "
    "outer check keeps the steady state lock-free; the inner check stops the "
    "callers queued behind the winner from creating a second pool. It is "
    "double-checked locking, and in asyncio it is safe because there is one "
    "thread and the only switch points are the awaits.'"),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    return r.randint(10, 50)


def _reference():
    pool = None
    lock = asyncio.Lock()

    async def get_pool(create):
        nonlocal pool
        if pool is None:
            async with lock:
                if pool is None:
                    pool = await create()
        return pool

    return get_pool


def test_solve():
    r = rng()
    for _ in range(3):
        get_pool = solve()
        assert inspect.iscoroutinefunction(get_pool), "solve() must return an async def"
        n = _gen(r)
        calls = {"n": 0}

        async def create(_c=calls):
            _c["n"] += 1
            await asyncio.sleep(0.002)           # the gap where the race happens
            return object()

        async def main():
            first = await asyncio.gather(*(get_pool(create) for _ in range(n)))  # noqa: B023
            later = await get_pool(create)  # noqa: B023
            return first, later

        first, later = asyncio.run(main())
        assert calls["n"] == 1, f"create() ran {calls['n']} times for {n} concurrent callers"
        assert all(p is first[0] for p in first), "every caller must get the same object"
        assert later is first[0], "a later call must reuse the pool, not rebuild it"
