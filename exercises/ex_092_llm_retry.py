"""Retry the failures that clear on their own — and only those."""

from _lib import rng
from langchain_core.runnables import RunnableLambda

META = {"topic": 92, "title": "LLM retry — back off on rate limits, fail fast on bad requests",
        "tier": 4, "minutes": 20, "prereqs": [45]}


class RateLimited(Exception):
    """The provider said 429. The identical call will work later."""


class BadRequest(Exception):
    """The provider said 400. The identical call will never work."""


def solve(model, prompt, sleep, max_attempts, base):
    """WHY: LangChain is a library for wiring steps together around an AI
    model. Calls to a paid AI service fail in two ways. "Too many requests,
    slow down" clears by itself if you wait a bit and try again. "Your
    request is malformed" will never clear, and retrying it only wastes
    money, adds load and delays the error message someone needs to read. A
    script that treats both the same way is a common and expensive bug.

    YOU GET: `model` — a stand-in AI model. model.invoke(prompt) returns an
    answer string, or raises one of two errors defined at the top of this
    file: RateLimited (wait and try again) or BadRequest (give up). The
    test's fake follows a script of outcomes; no real AI is called.

    `prompt` — the question, as a string.

    `sleep` — a function you call with a number of seconds to wait. The test
    hands you a fake that only writes the number down, so nothing really
    waits.

    `max_attempts` — a whole number, like 3: the most calls you may make.

    `base` — a number, like 0.5: the first wait in seconds; each later wait
    is double the one before.

    YOU RETURN: the answer string from the model. If the tries run out, or
    the request is bad, or the model raises something you were not told
    about, let that error escape instead of returning anything.

    ─── exact rules ───
    Model APIs fail in two very different ways, and telling them apart is
    the whole job. A rate limit clears on its own, so waiting helps. A
    malformed request does not, so retrying it burns your budget, multiplies
    the load, and delays the error message someone actually needs to read.

    Call `model.invoke(prompt)` and return what it returns. Rules:

      - at most `max_attempts` calls, ever
      - RateLimited, attempts remaining: wait, then try again. For failure
        number i (0-based, so the first failure is i=0) wait exactly

            base * (2 ** i)

        by calling sleep(that number). Never time.sleep
      - RateLimited on the last allowed attempt: re-raise it
      - BadRequest: give up immediately. Re-raise it, do not sleep, do not
        call the model again
      - anything else the model raises is not yours to handle — let it out
        untouched, on the first sight of it

        base=0.5, model raises RateLimited twice then returns "ok"
        ->  sleeps 0.5, then 1.0, calls the model 3 times, returns "ok"

    RateLimited and BadRequest are defined at the top of this file, so you can
    name them directly in an except clause. `sleep` is a parameter rather than
    an import so the test can pass a fake that only records the delay — that
    is why this test finishes instantly instead of waiting minutes, and
    "inject the clock so tests control time" is worth saying out loud in an
    interview.
    """
    raise NotImplementedError


HINTS = [
    ("Backoff is the easy half. The half that matters is that not every "
    "exception deserves a retry, so a bare `except Exception` is already the "
    "wrong answer — it turns one bad prompt into max_attempts identical bad "
    "prompts, and hides the real error behind the last one. Decide per "
    "exception type: wait and retry, or get out of the way."),
    ("Loop `for attempt in range(max_attempts)` and try to return "
    "model.invoke(prompt) inside it. You need two except clauses on that try. "
    "`except BadRequest: raise` re-raises straight away. `except RateLimited:` "
    "checks whether attempt is the last one (bare `raise` if so) and otherwise "
    "calls sleep(base * 2 ** attempt) before going round again. Any other "
    "exception is caught by neither clause, which is exactly what you want."),
    ("Different data — two kinds of failure from a file read, 3 tries:\n"
    "    for attempt in range(3):\n"
    "        try:\n"
    "            data = open('/tmp/report').read()\n"
    "            break\n"
    "        except IsADirectoryError:\n"
    "            raise                      # never going to become a file\n"
    "        except BlockingIOError:\n"
    "            if attempt == 2:\n"
    "                raise                  # out of tries, give up honestly\n"
    "            time.sleep(0.1 * 2 ** attempt)   # 0.1, then 0.2\n"
    "Note the two clauses do opposite things, and that the last retry re-raises "
    "rather than returning None. Yours returns instead of breaking, and calls "
    "the injected sleep."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _model(script, value):
    """A Runnable that follows `script`: one of "429", "400", "boom", "ok" per call."""
    calls = []

    def call(prompt):
        calls.append(prompt)
        assert len(calls) <= len(script), (
            f"the model was called {len(calls)} times; only {len(script)} were allowed"
        )
        outcome = script[len(calls) - 1]
        if outcome == "429":
            raise RateLimited("429 rate limit exceeded")
        if outcome == "400":
            raise BadRequest("400 invalid prompt")
        if outcome == "boom":
            raise ValueError("something else entirely")
        return value

    return RunnableLambda(call), calls


def _reference(model, prompt, sleep, max_attempts, base):
    for attempt in range(max_attempts):
        try:
            return model.invoke(prompt)
        except BadRequest:
            raise
        except RateLimited:
            if attempt == max_attempts - 1:
                raise
            sleep(base * (2 ** attempt))


def _delays(base, count):
    return [round(base * (2 ** i), 9) for i in range(count)]


def test_solve():
    r = rng()
    for _ in range(4):
        base = r.choice([0.25, 0.5, 1.0, 2.0])
        limits = r.randint(1, 3)
        max_attempts = limits + r.randint(1, 3)
        value = r.choice(["ok", "done", "answer: 42", "restarted"])
        prompt = r.choice(["summarise the alert", "explain the outage", "name the pod"])

        # 1. rate limited a few times, then it works
        model, calls = _model(["429"] * limits + ["ok"], value)
        waits = []
        assert solve(model, prompt, waits.append, max_attempts, base) == value
        assert len(calls) == limits + 1, f"expected {limits + 1} calls, got {len(calls)}"
        assert [round(w, 9) for w in waits] == _delays(base, limits), (
            f"delays were {waits}, expected {_delays(base, limits)}"
        )

        # 2. rate limited forever: give up after max_attempts and re-raise
        model, calls = _model(["429"] * max_attempts, value)
        waits = []
        try:
            solve(model, prompt, waits.append, max_attempts, base)
            raise AssertionError("expected RateLimited once the attempts ran out")
        except RateLimited:
            pass
        assert len(calls) == max_attempts
        assert [round(w, 9) for w in waits] == _delays(base, max_attempts - 1)

        # 3. a bad request stops everything on the spot
        before = r.randrange(0, max_attempts - 1)
        model, calls = _model(["429"] * before + ["400"], value)
        waits = []
        try:
            solve(model, prompt, waits.append, max_attempts, base)
            raise AssertionError("expected BadRequest to be re-raised, not retried")
        except BadRequest:
            pass
        assert len(calls) == before + 1, "a BadRequest must not be retried"
        assert [round(w, 9) for w in waits] == _delays(base, before)

        # 4. an error you were not asked to handle passes straight through
        model, calls = _model(["boom"], value)
        waits = []
        try:
            solve(model, prompt, waits.append, max_attempts, base)
            raise AssertionError("expected the ValueError to propagate")
        except ValueError:
            pass
        assert len(calls) == 1, "only RateLimited is worth retrying"
        assert waits == []
