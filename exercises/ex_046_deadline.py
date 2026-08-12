"""Any call that can block needs a deadline — waiting forever is an outage."""

from _lib import rng

META = {"topic": 46, "title": "deadlines — poll until ready or time out", "tier": 3,
        "minutes": 15, "prereqs": [43]}


def solve(check, now, sleep, timeout, interval):
    """Wait for a resource to become ready, but never wait forever.

    Rules, exactly:
      - Compute the deadline once, up front: deadline = now() + timeout.
      - While now() < deadline: call check(). If it returns something truthy,
        return the number of times check was called. Otherwise sleep(interval)
        and loop.
      - If the loop ends without success, raise TimeoutError (the built-in).

        timeout=10, interval=4, check ready on the 2nd call
        ->  check at t=0 (no), sleep to t=4, check at t=4 (yes) -> return 2

        timeout=10, interval=4, never ready
        ->  checks at t=0, 4, 8, clock reaches 12 -> raise TimeoutError

    Real code would use time.monotonic() and time.sleep(). Here they arrive
    as parameters, so the test hands in a fake clock where sleep(4) just adds
    4 to a number. No real waiting, and the test can assert exactly when you
    gave up. Injecting the clock is what makes timeout code testable — say
    that in an interview and you sound like you have been paged before.
    """
    raise NotImplementedError


HINTS = [
    "Two mistakes to avoid: recomputing the deadline inside the loop (it drifts "
    "forever) and checking the clock before the first check() (you always get "
    "at least one look). Pin down when the clock is read and when you poll.",
    "One variable for the deadline before the loop, one counter for polls. "
    "`while now() < deadline:` then check(), return the counter on truthy, "
    "else sleep(interval). After the while, raise TimeoutError — code below a "
    "while only runs when its condition went false.",
    "Different data — waiting for a fake queue to drain, budget 6, step 2:\n"
    "    t = [0]\n"
    "    queue = [3, 1, 0]          # lengths we will see\n"
    "    stop_at = t[0] + 6\n"
    "    looks = 0\n"
    "    while t[0] < stop_at:\n"
    "        looks += 1\n"
    "        if queue[looks - 1] == 0:\n"
    "            print('drained after', looks, 'looks')\n"
    "            break\n"
    "        t[0] += 2\n"
    "    else:\n"
    "        print('gave up')\n"
    "    # drained after 3 looks\n"
    "Yours returns instead of printing, and raises TimeoutError on the give-up path.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

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

            def run(fn):
                now, sleep = _clock()
                check, n = _ready_after(k)
                try:
                    out = ("ok", fn(check, now, sleep, timeout, interval))
                except TimeoutError:
                    out = ("timeout", None)
                return out, n["c"], now()

            assert run(solve) == run(_reference)
