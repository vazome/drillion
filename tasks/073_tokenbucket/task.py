def solve(requests: list[tuple[int, str]], capacity: int, rate: float, start: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    capacity = r.randint(2, 5)
    rate = r.choice([0.5, 1, 2])
    start = r.randint(0, 100)
    ids = [f"req-{i}" for i in range(1, r.randint(4, 9))]
    requests = []
    t = start
    for _ in range(r.randint(6, 14)):
        t += r.choice([0, 0, 1, 2, 4])      # bursts, then gaps that refill
        requests.append((t, r.choice(ids)))  # repeats exercise the retry path
    return requests, capacity, rate, start


def _reference(requests, capacity, rate, start):
    tokens = float(capacity)
    last = start
    seen = set()
    allowed = []
    for ts, rid in requests:
        tokens = min(capacity, tokens + (ts - last) * rate)
        last = ts
        if rid in seen:
            allowed.append(True)
        elif tokens >= 1:
            tokens -= 1
            seen.add(rid)
            allowed.append(True)
        else:
            allowed.append(False)
    return {"allowed": allowed, "tokens_left": round(tokens, 6)}


def test_solve():
    r = rng()
    for _ in range(4):
        requests, capacity, rate, start = _gen(r)
        got = solve(list(requests), capacity, rate, start)
        want = _reference(requests, capacity, rate, start)
        assert list(got["allowed"]) == want["allowed"]
        assert round(got["tokens_left"], 6) == want["tokens_left"]
