def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import asyncio
import inspect

from _lib import rng


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
