def solve(lines):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    ips = [f"10.0.{r.randint(0, 3)}.{i}" for i in range(1, 6)]
    paths = ["/api/users", "/health", "/api/orders", "/metrics"]
    # distinct hit-counts per IP: no ties, so top-3 order is unambiguous
    hits = r.sample(range(2, 12), len(ips))
    pool = [ip for ip, n in zip(ips, hits) for _ in range(n)]
    r.shuffle(pool)
    lines = []
    for ip in pool:
        st = r.choice([200, 200, 200, 201, 404, 500])
        dur = round(r.uniform(0.001, 2.0), 3)
        ts = f"0{r.randint(1,9)}/Aug/2026:10:{r.randint(10,59)}:{r.randint(10,59)} +1000"
        lines.append(f'{ip} - - [{ts}] "GET {r.choice(paths)} HTTP/1.1" '
                     f'{st} {r.randint(0, 2000)} {dur}')
    return lines


def _reference(lines):
    import math
    from collections import Counter
    parts = [line.split() for line in lines]
    ips = Counter(p[0] for p in parts)
    statuses = Counter(f"{int(p[8]) // 100}xx" for p in parts)
    durs = sorted(float(p[-1]) for p in parts)
    return {"top_ips": ips.most_common(3),
            "statuses": dict(statuses),
            "p95": durs[math.ceil(0.95 * len(durs)) - 1]}


def test_solve():
    r = rng()
    for _ in range(3):
        lines = _gen(r)
        assert solve(list(lines)) == _reference(lines)
