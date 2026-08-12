"""Whole-task drill: wait for the deploy to come up, or fail the pipeline.

Combines topics 46 (deadlines), 45 (backoff), 39 (exit codes).
"""

from _lib import rng

META = {"topic": 76, "title": "DRILL: poll until healthy, back off, exit code",
        "tier": 4, "minutes": 30, "prereqs": [46],
        "practices": [46, 45, 39]}


def solve(check, now, sleep, timeout, interval, max_interval):
    """A deploy just went out. Wait for it to report healthy, or give up.

    `check()` returns something truthy when the service is up. `now()` and
    `sleep()` are the clock, handed in so the test can replay hours in no
    time. Never import time here.

    Rules, exactly:
      - Read the clock once at the top: start = now(), and the deadline is
        start + timeout.
      - While now() is before the deadline: call check(). Truthy means done.
        Otherwise sleep(wait), then double wait, capped at max_interval.
        The first wait is `interval`.
      - Return a dict either way:

            {"exit_code": 0, "attempts": 3, "elapsed": 3.0}   # healthy
            {"exit_code": 1, "attempts": 4, "elapsed": 11.0}  # gave up

        exit_code is 0 for healthy and 1 for the timeout. attempts counts
        check() calls. elapsed is now() - start at the moment you return.

    Worked example, timeout=10, interval=1, max_interval=4, check false
    then false then true:

        t=start+0   attempt 1, false, sleep 1  (wait becomes 2)
        t=start+1   attempt 2, false, sleep 2  (wait becomes 4)
        t=start+3   attempt 3, true
        ->  {"exit_code": 0, "attempts": 3, "elapsed": 3}

    Returning the code instead of calling sys.exit is what makes this
    testable; the real script does sys.exit(result["exit_code"]) at the
    very bottom, and a non-zero code is what stops the pipeline. Say that
    part out loud, it is half of what the question is asking.
    """
    raise NotImplementedError


HINTS = [
    "Three separate ideas, and mixing them is what makes this hard: a "
    "deadline read once at the top, a wait that grows between polls, and an "
    "exit code carried out in the return value instead of thrown at the "
    "process. Sketch where each of the three lives before you write a line.",
    "start = now(); deadline = start + timeout; wait = interval; attempts = 0. "
    "Loop `while now() < deadline`, bump attempts, call check(), return the "
    "success dict on truthy. Otherwise sleep(wait) and then "
    "wait = min(wait * 2, max_interval). The code after the loop only runs "
    "when the clock ran out, so build the exit_code 1 dict there. Both "
    "branches compute elapsed as now() - start.",
    "Different data — a wait that doubles into a ceiling:\n"
    "    wait, waits = 2, []\n"
    "    for _ in range(5):\n"
    "        waits.append(wait)\n"
    "        wait = min(wait * 2, 10)\n"
    "    print(waits)     # [2, 4, 8, 10, 10]\n"
    "The cap matters: without it a long timeout ends with one enormous sleep "
    "and you notice the service came up four minutes ago.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

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

            def run(fn):
                now, sleep = _clock(start)
                check, n = _healthy_on(k)
                out = fn(check, now, sleep, timeout, interval, max_interval)
                return (out["exit_code"], out["attempts"],
                        round(out["elapsed"], 6), n["c"], round(now(), 6))

            assert run(solve) == run(_reference)
