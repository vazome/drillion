def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import asyncio
import inspect

from _lib import rng


def _gen(r):
    jobs = r.sample(range(100, 999), r.randint(3, 6))
    return jobs


def _reference():
    async def fetch_all(worker, jobs):
        return await asyncio.gather(*(worker(j) for j in jobs))
    return fetch_all


def test_solve():
    r = rng()
    fetch_all = solve()
    assert inspect.iscoroutinefunction(fetch_all), "fetch_all must be async def"
    for _ in range(3):
        jobs = _gen(r)
        log = []

        async def worker(j, _jobs=jobs, _log=log):
            _log.append(("start", j))
            # first-listed job sleeps longest: a sequential loop is forced
            # to finish it before later jobs start, and the assert catches that
            await asyncio.sleep(0.01 * (len(_jobs) - _jobs.index(j)))
            _log.append(("end", j))
            return j * 2

        results = asyncio.run(fetch_all(worker, list(jobs)))
        assert results == [j * 2 for j in jobs], "results must keep job order"
        starts = [i for i, (kind, _) in enumerate(log) if kind == "start"]
        ends = [i for i, (kind, _) in enumerate(log) if kind == "end"]
        assert max(starts) < min(ends), (
            "jobs ran one-after-another: every job must START before any "
            "job finishes. Launch them all, then wait."
        )
