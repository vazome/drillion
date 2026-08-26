def solve(lines, n):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    ips = [f"10.0.{r.randint(0, 5)}.{i}" for i in range(1, 6)]
    weights = r.sample([12, 8, 5, 3, 1], 5)
    pool = [ip for ip, w in zip(ips, weights) for _ in range(w)]
    r.shuffle(pool)
    paths = ["/api/users", "/health", "/api/orders"]
    lines = [f"{ip} GET {r.choice(paths)} {r.choice([200, 200, 404, 500])}" for ip in pool]
    return lines, r.choice([2, 3])


def _reference(lines, n):
    from collections import Counter
    return Counter(line.split()[0] for line in lines).most_common(n)


def test_solve():
    r = rng()
    for _ in range(4):
        lines, n = _gen(r)
        assert solve(lines, n) == _reference(lines, n)
