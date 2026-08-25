"""asyncio — run many waits at once instead of one after another."""
# READ FIRST:
#   https://realpython.com/async-io-python/  — THE asyncio walkthrough; read 'Async IO Explained' and 'The asyncio Package' before anything below
#   https://docs.python.org/3/library/asyncio-task.html#asyncio.gather
#   TAKE-HOME: `loadtest.py`, your concurrency test

import asyncio
import inspect

from _lib import rng

META = {"topic": 56, "title": "asyncio — gather, don't queue", "tier": 4,
        "minutes": 20, "prereqs": [55], "tags": ["concurrency", "asyncio", "rsample"]}


def solve():
    """WHY: A status page must fetch the state of a dozen services before it
    can render. Each fetch is mostly waiting on the network. If the code
    waits for service 1 to answer before it even asks service 2, the page
    takes the sum of all the waits; asking everyone at once and then
    collecting the answers takes only the slowest single wait. The team's
    code is written in Python's async style, and you are asked to write the
    "ask everyone at once, collect the answers in order" helper.

    YOU GET: nothing — you build the thing from scratch. Your solve()
    returns a helper; the test then calls that helper with its own `worker`
    (an async stand-in that pauses and returns a value) and a list of job
    ids. No real service is contacted.

    YOU RETURN: the helper function itself (an async function that takes a
    worker and a list of jobs), not the result of running it. When the test
    runs your helper, every job must start before any job finishes, and the
    results must come back in the same order as the jobs.

    ─── exact rules ───
    Return an ASYNC function `fetch_all(worker, jobs)` where:

      - `worker` is an async function: `await worker(job)` returns a result
      - `jobs` is a list of job ids

    fetch_all must start ALL jobs concurrently and return their results
    in the same order as `jobs`.

        async def worker(j): ...
        results = await fetch_all(worker, [3, 1, 2])   # [r3, r1, r2]

    The test fails a version that awaits jobs one at a time in a loop —
    that is just a slow for-loop wearing async syntax. One asyncio function
    does "launch all, wait for all, keep order" in a single call.

    Return the function itself (not a coroutine): `return fetch_all`.
    """
    raise NotImplementedError


HINTS = [
    ("`await worker(j)` inside a plain for-loop finishes job 1 completely "
    "before job 2 even starts — sequential, exactly what async exists to "
    "avoid. You need to hand ALL the coroutines to the event loop at once."),
    ("Build the list of coroutine objects first — calling worker(j) WITHOUT "
    "await creates one without running it. Then look up asyncio.gather: it "
    "takes many awaitables, runs them concurrently, and returns results in "
    "argument order."),
    ("Different data, same shape:\n"
    "    import asyncio\n"
    "    async def shout(word):\n"
    "        await asyncio.sleep(0.01)\n"
    "        return word.upper()\n"
    "    async def all_shouts(words):\n"
    "        return await asyncio.gather(*(shout(w) for w in words))\n"
    "    print(asyncio.run(all_shouts(['hi', 'yo'])))   # ['HI', 'YO']\n"
    "The * unpacks the coroutines into gather's arguments."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
