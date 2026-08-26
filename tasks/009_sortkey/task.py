def solve(services):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    names = ["api", "db", "web", "cache", "queue", "auth", "cron"]
    picked = r.sample(names, r.randint(4, 7))
    counts = r.sample(range(41), len(picked))    # distinct: no tie ambiguity
    return [[n, c] for n, c in zip(picked, counts)]


def _reference(services):
    return sorted(services, key=lambda s: s[1], reverse=True)


def test_solve():
    r = rng()
    for _ in range(4):
        svc = _gen(r)
        assert solve([list(s) for s in svc]) == _reference(svc)
