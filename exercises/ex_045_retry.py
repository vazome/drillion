"""Retry with backoff and jitter — the standard whiteboard ask for SRE screens."""

import itertools

from _lib import rng

META = {"topic": 45, "title": "retry — exponential backoff with jitter, by hand", "tier": 4,
        "minutes": 20, "prereqs": [43]}


def solve(call, sleep, rand, max_attempts, base):
    """WHY: You run a nightly job that pushes metrics to a monitoring vendor's
    API. Their service sometimes refuses a request for a second or two (a
    restart, a network blip) and is then fine again. If your job gives up on
    the first failure, the on-call engineer gets paged at 3am for nothing; if
    it retries instantly and forever, it hammers a struggling service and
    makes the outage worse. The team lead asks for one helper every script
    can use: try again, wait a bit longer each time, add a little randomness
    so a thousand clients do not all retry in the same second, and give up
    after a fixed number of tries.

    YOU GET: `call` — a function that takes no arguments. Calling it either
    returns a result or fails with an error. The test hands in a stand-in
    that fails a set number of times and then succeeds (or never succeeds);
    nothing real is contacted.
    `sleep` — a function you call with a number of seconds to wait. The test
    hands in a fake that only writes the number down; no real waiting.
    `rand` — a function with no arguments that returns a number between 0
    and 1. The test hands in a fake with known values so the result is
    predictable.
    `max_attempts` — a whole number like 4: the most times you may try.
    `base` — a number like 1.0: the starting wait, in seconds.

    YOU RETURN: whatever `call()` returned the first time it worked. If every
    attempt fails, return nothing: let the last error escape so the caller
    sees it.

    ─── exact rules ───
    Call `call()` until it succeeds, backing off between failures.

    Rules:
      - Try call() at most max_attempts times. On success, return its value
        immediately.
      - If call() raises any Exception and attempts remain, wait and retry.
        For failure number i (0-based: first failure is i=0):
            delay = base * (2 ** i) * (1 + rand())
        Wait by calling sleep(delay) — never time.sleep.
      - If the last allowed attempt fails, re-raise that exception (a bare
        `raise` inside the except block).

    rand() returns a float in [0, 1), so each delay lands somewhere between
    base * 2**i and base * 2**(i+1). That randomness is the jitter: it stops
    a thousand retrying clients from hammering the server in lockstep.

        base=1, rand() returns 0.5 then 0.25, call fails twice then returns 7
        ->  sleeps 1.5, then 2.5, calls 3 times, returns 7

    Why sleep and rand are parameters instead of imports: the test passes a
    fake sleep that just records the delay, and a fake rand with known values.
    No real waiting, fully deterministic. This is dependency injection, and
    "inject the clock so tests control time" is itself an interview answer
    worth saying out loud.
    """
    raise NotImplementedError


HINTS = [
    ("Three moving parts: a loop over attempt numbers, a try/except around one "
    "call, and the decision inside except — is this the last attempt (give up, "
    "re-raise) or not (sleep, go around again). Get that skeleton before any "
    "delay math."),
    ("for attempt in range(max_attempts): try to return call(); except "
    "Exception: if attempt == max_attempts - 1, a bare `raise` re-raises the "
    "current exception; otherwise sleep(base * 2 ** attempt * (1 + rand())). "
    "Returning from inside try exits the loop on success."),
    ("Different data — retrying a flaky lookup, 2 failures allowed:\n"
    "    def lookup():\n"
    "        raise OSError('dns')\n"
    "\n"
    "    waits = []\n"
    "    for attempt in range(2):\n"
    "        try:\n"
    "            result = lookup()\n"
    "            break\n"
    "        except OSError:\n"
    "            if attempt == 1:\n"
    "                raise\n"
    "            waits.append(0.5 * 2 ** attempt)\n"
    "    # waits == [0.5], then the second failure re-raises OSError\n"
    "Yours returns instead of break, and multiplies in (1 + rand()) for jitter."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
