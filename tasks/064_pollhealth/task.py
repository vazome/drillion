def solve(check, now, sleep, timeout: int, interval: float, max_interval: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _clock(start):
    """Fake clock: now() reads it, sleep(s) advances it. No real waiting."""
    t = [float(start)]

    def now():
        return t[0]

    def sleep(s):
        t[0] += s

    return now, sleep


def _healthy_on(k):
    """A check() that stays false until call number k."""
    n = {"c": 0}

    def check():
        n["c"] += 1
        return n["c"] >= k

    return check, n


def _reference(check, now, sleep, timeout, interval, max_interval):
    start = now()
    deadline = start + timeout
    wait = interval
    attempts = 0
    while now() < deadline:
        attempts += 1
        if check():
            return {"exit_code": 0, "attempts": attempts,
                    "elapsed": now() - start}
        sleep(wait)
        wait = min(wait * 2, max_interval)
    return {"exit_code": 1, "attempts": attempts, "elapsed": now() - start}


def test_solve():
    r = rng()
    for _ in range(4):
        start = r.randint(1000, 9999)
        timeout = r.randint(8, 40)
        interval = r.choice([0.5, 1, 2])
        max_interval = r.choice([4, 8, 16])
        for k in (r.randint(1, 6), 10 ** 9):   # one likely success, one sure timeout

            def run(fn):  # closes over loop vars; called within this iteration
                now, sleep = _clock(start)  # noqa: B023
                check, n = _healthy_on(k)  # noqa: B023
                out = fn(check, now, sleep, timeout, interval, max_interval)  # noqa: B023
                return (out["exit_code"], out["attempts"],
                        round(out["elapsed"], 6), n["c"], round(now(), 6))

            assert run(solve) == run(_reference)
