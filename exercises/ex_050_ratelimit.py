"""A 429 is the server asking you to slow down; ignoring it is how you get an IP ban."""

from _lib import rng

META = {"topic": 50, "title": "rate limits — honour 429 and Retry-After",
        "tier": 3, "minutes": 15, "prereqs": [45]}


def solve(request, sleep, max_attempts, default_wait):
    """Call `request()` until it succeeds, waiting when told to.

    `request()` returns a dict shaped like an HTTP response:

        {"status": 200, "headers": {}, "body": {"items": 12}}
        {"status": 429, "headers": {"Retry-After": "3"}}
        {"status": 500, "headers": {}}

    Rules, in this order, for each of at most max_attempts attempts:
      - status 200            -> return resp["body"] straight away.
      - status is not 429     -> raise RuntimeError. Do not retry, do
                                 not sleep. This drill only retries the
                                 one status the server asked you to.
      - status 429, attempts left -> work out the wait and sleep(wait).
      - status 429, no attempts left -> raise RuntimeError.

    The wait is float(resp["headers"]["Retry-After"]) when that header
    is there, and default_wait when it is not. Header values arrive as
    strings, always — "3" is not 3.

        max_attempts=3, default_wait=1.0
        attempt 1 -> {"status": 429, "headers": {"Retry-After": "2"}}
        attempt 2 -> {"status": 429, "headers": {}}
        attempt 3 -> {"status": 200, "headers": {}, "body": {"items": 12}}
        ->  sleep(2.0), sleep(1.0), return {"items": 12}

    sleep is a parameter, not time.sleep, for the same reason as
    everywhere else: the test hands in a fake that records the delay
    instead of burning it. Never sleep before the first call, and never
    after the last failure — a wait nobody is waiting on is just a
    slower error.
    """
    raise NotImplementedError


HINTS = [
    "Each response has three possible endings, not two: done, wait and go "
    "round again, or give up right now. Sort out which status leads to which "
    "before writing the loop. The other easy miss is the header type — it is "
    "text off the wire, so it needs converting before sleep sees it.",
    "for attempt in range(max_attempts): resp = request(), then the status "
    "checks in the order the spec lists them. The missing-header case is "
    "resp['headers'].get('Retry-After', default_wait) wrapped in float(), "
    "which happily takes either a string or the number you defaulted to. The "
    "last-attempt test is attempt == max_attempts - 1, the same shape as in "
    "the retry drill.",
    "Different data — a queue API that answers with a wait hint:\n"
    "    replies = [{'code': 503, 'hdr': {'Retry-After': '4'}},\n"
    "               {'code': 200, 'hdr': {}, 'body': 'done'}]\n"
    "    waits = []\n"
    "    for reply in replies:\n"
    "        if reply['code'] == 200:\n"
    "            print(reply['body'])      # done\n"
    "            break\n"
    "        waits.append(float(reply['hdr'].get('Retry-After', 1)))\n"
    "    print(waits)                      # [4.0]\n"
    "Yours calls request() once per attempt instead of reading a list, and "
    "raises RuntimeError on the two paths that are not a 200.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _throttled(r):
    if r.random() < 0.25:
        return {"status": 429, "headers": {}}       # no hint, use default_wait
    return {"status": 429,
            "headers": {"Retry-After": r.choice(["1", "2", "3", "0.5", "10"])}}


def _gen(r):
    """A scripted sequence of responses, plus the knobs solve gets."""
    max_attempts = r.randint(2, 5)
    default_wait = r.choice([0.5, 1.0, 2.0])
    case = r.choice(["success", "success", "first-try", "exhausted", "hard-error"])
    script = []
    if case == "first-try":
        pass
    elif case == "success":
        script = [_throttled(r) for _ in range(r.randint(1, max_attempts - 1))]
    elif case == "exhausted":
        return [_throttled(r) for _ in range(max_attempts)], max_attempts, default_wait
    else:                                            # hard-error
        script = [_throttled(r) for _ in range(r.randint(0, max_attempts - 2))]
        script.append({"status": r.choice([500, 403, 404]), "headers": {}})
        return script, max_attempts, default_wait
    script.append({"status": 200, "headers": {}, "body": {"items": r.randint(1, 99)}})
    return script, max_attempts, default_wait


def _api(script):
    calls = {"n": 0}

    def request():
        calls["n"] += 1
        if calls["n"] > len(script):
            raise AssertionError("request() called after it should have stopped")
        return script[calls["n"] - 1]

    return request, calls


def _reference(request, sleep, max_attempts, default_wait):
    for attempt in range(max_attempts):
        resp = request()
        if resp["status"] == 200:
            return resp["body"]
        if resp["status"] != 429:
            raise RuntimeError(f"unretryable status {resp['status']}")
        if attempt == max_attempts - 1:
            raise RuntimeError("still rate limited after every attempt")
        sleep(float(resp["headers"].get("Retry-After", default_wait)))


def _run(fn, script, max_attempts, default_wait):
    request, calls = _api(script)
    delays = []
    try:
        out = ("returned", fn(request, delays.append, max_attempts, default_wait))
    except NotImplementedError:                  # the empty stub, not an answer
        raise
    except RuntimeError:
        out = ("raised", None)
    return out, [round(d, 9) for d in delays], calls["n"]


def test_solve():
    r = rng()
    for _ in range(5):
        script, max_attempts, default_wait = _gen(r)
        assert (_run(solve, script, max_attempts, default_wait)
                == _run(_reference, script, max_attempts, default_wait))
