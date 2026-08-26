def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import asyncio
import inspect

from _lib import rng


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
