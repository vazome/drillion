def solve(check, now, sleep, timeout, interval):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _clock():
    """A fake clock: now() reads it, sleep(s) advances it. No real time."""
    t = [0.0]

    def now():
        return t[0]

    def sleep(s):
        t[0] += s

    return now, sleep


def _ready_after(k):
    """A check() that returns False until call number k."""
    n = {"c": 0}

    def check():
        n["c"] += 1
        return n["c"] >= k

    return check, n


def _reference(check, now, sleep, timeout, interval):
    deadline = now() + timeout
    polls = 0
    while now() < deadline:
        polls += 1
        if check():
            return polls
        sleep(interval)
    raise TimeoutError(f"not ready after {polls} checks")


def test_solve():
    r = rng()
    for _ in range(4):
        timeout = r.randint(5, 30)
        interval = r.choice([1, 2, 3, 5])
        for k in (r.randint(1, 6), 10 ** 9):  # one likely success, one sure timeout

            def run(fn):  # closes over loop vars; called within this iteration
                now, sleep = _clock()
                check, n = _ready_after(k)  # noqa: B023
                try:
                    out = ("ok", fn(check, now, sleep, timeout, interval))  # noqa: B023
                except TimeoutError:
                    out = ("timeout", None)
                return out, n["c"], now()

            assert run(solve) == run(_reference)
