def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import asyncio
import inspect

from _lib import rng


def _gen(r):
    n = r.randint(1, 4)
    rows = [{"id": i, "content": f"chunk {r.randint(1, 99)}"} for i in range(n)]
    return rows, r.randint(1, 3)


def _reference():
    class FakePool:
        def __init__(self, rows, max_size):
            self.rows = rows
            self.slots = asyncio.Semaphore(max_size)

        def acquire(self):
            return self

        async def __aenter__(self):
            await self.slots.acquire()
            return self

        async def __aexit__(self, *exc):
            self.slots.release()

        async def fetch(self, sql, *params):
            return self.rows

    return FakePool


def test_solve():
    r = rng()
    FakePool = solve()
    assert inspect.isclass(FakePool), "solve() must return a class"
    for _ in range(3):
        rows, max_size = _gen(r)

        async def main(_rows=rows, _max=max_size):
            pool = FakePool(_rows, _max)
            async with pool.acquire() as conn:
                assert await conn.fetch("SELECT 1", 7) == _rows, "fetch must return rows"

            # max_size callers may be inside at once, never more
            state = {"now": 0, "peak": 0}

            async def hold():
                async with pool.acquire():
                    state["now"] += 1
                    state["peak"] = max(state["peak"], state["now"])
                    await asyncio.sleep(0.002)
                    state["now"] -= 1

            await asyncio.gather(*(hold() for _ in range(_max + 3)))
            assert state["peak"] == _max, f"{state['peak']} holders at once, max_size={_max}"

            # a slot taken by a body that raised must still come back
            one = FakePool(_rows, 1)
            try:
                async with one.acquire():
                    raise ValueError("boom")
            except ValueError:
                pass

            async def reenter():
                async with one.acquire() as conn:
                    return await conn.fetch("x")

            got = await asyncio.wait_for(reenter(), timeout=0.5)  # hangs => slot leaked
            assert got == _rows

        asyncio.run(main())
