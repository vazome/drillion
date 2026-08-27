from langchain_core.runnables import Runnable


class RateLimited(Exception):
    """The provider said 429. The identical call will work later."""


class BadRequest(Exception):
    """The provider said 400. The identical call will never work."""


def solve(model: Runnable[str, str], prompt: str, sleep, max_attempts: int, base: float):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng
from langchain_core.runnables import RunnableLambda


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
