def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import asyncio
import inspect

from _lib import rng
from langchain_core.runnables import RunnableLambda

FAST, SLOW, LIMIT = 0.005, 0.05, 0.03


def _gen(r):
    verbs = ["restart", "drain", "rotate", "scale", "patch", "evict", "resize", "reload"]
    prompts = [f"explain {v}" for v in r.sample(verbs, r.randint(3, 6))]
    # prompts[0] stays fast, so a sequential solution always finishes one call
    # before starting the next and the start/end ordering check catches it
    slow = set(r.sample(prompts[1:], r.randint(1, len(prompts) - 2)))
    return prompts, slow


def _model(slow, log):
    async def call(prompt):
        log.append(("start", prompt))
        await asyncio.sleep(SLOW if prompt in slow else FAST)
        log.append(("end", prompt))
        return prompt.upper()
    return RunnableLambda(call)


def _reference():
    async def ask_all(model, prompts, timeout):
        async def one(prompt):
            try:
                return await asyncio.wait_for(model.ainvoke(prompt), timeout)
            except TimeoutError:
                return "TIMEOUT"
        return await asyncio.gather(*(one(p) for p in prompts))
    return ask_all


def test_solve():
    r = rng()
    ask_all = solve()
    assert inspect.iscoroutinefunction(ask_all), "ask_all must be an async def"

    for _ in range(3):
        prompts, slow = _gen(r)
        want = ["TIMEOUT" if p in slow else p.upper() for p in prompts]

        log = []
        got = asyncio.run(ask_all(_model(slow, log), list(prompts), LIMIT))
        assert got == want, f"got {got}, expected {want}"

        starts = [i for i, (kind, _) in enumerate(log) if kind == "start"]
        ends = [i for i, (kind, _) in enumerate(log) if kind == "end"]
        assert len(starts) == len(prompts), "every prompt must be sent"
        assert ends and max(starts) < min(ends), (
            "the calls ran one after another: every call must START before any "
            "call comes back. Launch them all, then wait."
        )
