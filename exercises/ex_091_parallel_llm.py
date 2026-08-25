"""Fan out N model calls at once, keep the order, cap what each one may cost you."""

import asyncio
import inspect

from _lib import rng
from langchain_core.runnables import RunnableLambda

META = {"topic": 91, "title": "parallel LLM calls — gather with a per-call timeout",
        "tier": 4, "minutes": 22, "prereqs": [56]}


def solve():
    """WHY: LangChain is a library for wiring steps together around an AI
    model. A support team wants ten customer tickets summarised by an AI
    model. Sent one after another, each waits for the previous one to
    finish; sent all at once they take about as long as the slowest single
    one. But any single call can hang, so each needs its own time limit, and
    a call that runs out of time must just be marked as such without
    spoiling the other answers.

    YOU GET: nothing — you build the thing from scratch. The function you
    write will later be handed three things: `model` (a stand-in AI model
    whose ainvoke method gives back an answer string), `prompts` (a list of
    strings) and `timeout` (seconds allowed per call). The test's fake model
    only pauses briefly and writes down when each call started and ended; no
    real AI is called.

    YOU RETURN: an async function named ask_all. Return the function itself;
    do not call it. When the test runs it, it must give back a list of
    answers in the same order as the prompts, with the text "TIMEOUT" in the
    slot of any call that took too long.

    ─── exact rules ───
    Ten prompts answered one after another is ten round trips of sitting
    still. Every Runnable has an async side — `await model.ainvoke(prompt)` —
    so all ten can be in flight at once. And since one prompt can hang, each
    call needs its own time limit rather than one limit for the batch.

    Return an ASYNC function `ask_all(model, prompts, timeout)` where:

      - `model` is a Runnable; `await model.ainvoke(prompt)` returns a string
      - `prompts` is a list of prompt strings
      - `timeout` is the seconds allowed for ONE call

    ask_all must:

      - start every call concurrently, not one after another
      - return a list of answers in the same order as `prompts`
      - put the string "TIMEOUT" in the slot of any call that ran longer than
        `timeout`, and leave the other answers untouched

        answers = await ask_all(model, ["a", "b", "c"], 0.03)
        # ["A", "TIMEOUT", "C"]

    One slow prompt must not delay the others and must not sink the whole
    batch. Return the function itself, not a coroutine: `return ask_all`.

    The test records when each call starts and finishes, and fails a version
    that waits for one call to come back before starting the next.
    """
    raise NotImplementedError


HINTS = [
    ("Two separate problems, and mixing them up is the usual mistake. First: "
    "everything must be launched before anything is awaited, or you have a "
    "slow for-loop wearing async syntax. Second: the time limit belongs to one "
    "call, not to the group — a group-wide limit would kill the answers that "
    "already came back, and letting a timeout escape would sink the whole "
    "batch. So the per-call handling has to happen inside each call."),
    ("Write a small inner `async def one(prompt)` that wraps a single call: "
    "asyncio.wait_for(model.ainvoke(prompt), timeout) gives up after `timeout` "
    "seconds by raising TimeoutError, so catch that and return 'TIMEOUT'. Then "
    "hand one(p) for every p to asyncio.gather, which runs them all at once "
    "and returns results in argument order."),
    ("Different data — three lookups at once, each capped at 20ms:\n"
    "    import asyncio\n"
    "    async def lookup(host):\n"
    "        await asyncio.sleep(0.05 if host == 'slow' else 0.001)\n"
    "        return host + '.internal'\n"
    "\n"
    "    async def one(host):\n"
    "        try:\n"
    "            return await asyncio.wait_for(lookup(host), 0.02)\n"
    "        except TimeoutError:\n"
    "            return 'TIMEOUT'\n"
    "\n"
    "    async def all_of(hosts):\n"
    "        return await asyncio.gather(*(one(h) for h in hosts))\n"
    "\n"
    "    print(asyncio.run(all_of(['a', 'slow', 'b'])))\n"
    "    # ['a.internal', 'TIMEOUT', 'b.internal']\n"
    "Yours awaits model.ainvoke(prompt) where this awaits lookup(host)."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
