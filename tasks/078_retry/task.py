from collections.abc import Callable


def solve(call: Callable[[], int], sleep: Callable[[float], None],
          rand: Callable[[], float], max_attempts: int, base: float):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import itertools

from _lib import rng


def _flaky(fails, value):
    """A callable that raises ConnectionError `fails` times, then succeeds."""
    calls = {"n": 0}

    def call():
        calls["n"] += 1
        if calls["n"] <= fails:
            raise ConnectionError("transient")
        return value

    return call, calls


def _reference(call, sleep, rand, max_attempts, base):
    for attempt in range(max_attempts):
        try:
            return call()
        except Exception:
            if attempt == max_attempts - 1:
                raise
            sleep(base * (2 ** attempt) * (1 + rand()))


def test_solve():
    r = rng()
    for _ in range(4):
        fails = r.randint(1, 3)
        max_attempts = fails + r.randint(1, 3)
        base = r.choice([0.5, 1.0, 2.0])
        jitters = [r.random() for _ in range(max_attempts)]
        value = r.randint(100, 999)

        # succeeds after `fails` failures
        call, calls = _flaky(fails, value)
        delays = []
        it = iter(jitters)
        assert solve(call, delays.append, lambda: next(it), max_attempts, base) == value  # noqa: B023
        assert calls["n"] == fails + 1
        expected = [base * (2 ** i) * (1 + jitters[i]) for i in range(fails)]
        assert [round(d, 9) for d in delays] == [round(e, 9) for e in expected]
        assert all(a < b for a, b in itertools.pairwise(delays))  # backoff grows

        # never succeeds: must re-raise after exactly max_attempts calls
        call, calls = _flaky(10 ** 9, value)
        delays = []
        it = iter(jitters)
        try:
            solve(call, delays.append, lambda: next(it), max_attempts, base)  # noqa: B023
            raise AssertionError("expected ConnectionError after max_attempts")
        except ConnectionError:
            pass
        assert calls["n"] == max_attempts
        assert len(delays) == max_attempts - 1
