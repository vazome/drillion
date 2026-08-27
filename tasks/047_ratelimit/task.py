def solve(request, sleep, max_attempts: int, default_wait: float):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


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
