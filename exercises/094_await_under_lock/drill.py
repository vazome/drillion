def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import asyncio
import inspect

from _lib import rng


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
