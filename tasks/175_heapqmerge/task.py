def solve(streams: list[list[tuple[str, str]]], n: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    services = ["api", "db", "worker", "cache"]
    events = ["up", "slow", "restarted", "failover", "timeout", "healthy"]
    minutes = r.sample(range(59), r.randint(4, 12))
    streams = [[] for _ in range(r.randint(1, 4))]
    for m in sorted(minutes):
        svc = r.choice(services)
        r.choice(streams).append((f"10:{m:02d}", f"{svc} {r.choice(events)}"))
    return streams, r.choice([1, 3, 5, 99])


def _reference(streams, n):
    import heapq
    from itertools import islice
    return list(islice(heapq.merge(*streams), n))


def test_solve():
    r = rng()
    cases = [([[("10:01", "api up"), ("10:04", "api slow")], [("10:02", "db up")]], 2),
             ([], 3), ([[], [("10:00", "web up")]], 5)]
    for _ in range(6):
        cases.append(_gen(r))
    for streams, n in cases:
        assert solve(streams, n) == _reference(streams, n), f"streams={streams} n={n}"
