def solve(lines):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    from datetime import datetime, timedelta
    base = datetime(2026, r.randint(1, 12), r.randint(1, 28),  # noqa: DTZ001 — naive log times
                    r.randint(0, 22), r.randint(0, 50))
    methods = ["GET", "GET", "POST", "DELETE"]
    paths = ["/api/users", "/health", "/login", "/metrics", "/api/orders"]
    lines = []
    for _ in range(r.randint(10, 25)):
        t = base + timedelta(minutes=r.randint(0, 8), seconds=r.randint(0, 59))
        lines.append(f'{t.strftime("%Y-%m-%d %H:%M:%S")} '
                     f'{r.choice(methods)} {r.choice(paths)}')
    r.shuffle(lines)
    return lines


def _reference(lines):
    from collections import Counter
    from datetime import datetime
    times = [datetime.strptime(l[:19], "%Y-%m-%d %H:%M:%S") for l in lines]  # noqa: DTZ007
    counts = Counter(t.strftime("%Y-%m-%d %H:%M") for t in times)
    busiest = min(counts, key=lambda m: (-counts[m], m))
    return {"span_seconds": int((max(times) - min(times)).total_seconds()),
            "busiest_minute": busiest}


def test_solve():
    r = rng()
    for _ in range(4):
        lines = _gen(r)
        assert solve(list(lines)) == _reference(lines)
