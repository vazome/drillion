def solve(rows: list[tuple[str, float]]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    names = ["api", "db", "cache", "queue", "ingest", "worker", "gateway"]
    picked = r.sample(names, r.randint(3, 6))
    rows = [(n, round(r.uniform(0, 999), 2)) for n in picked]
    i = r.randrange(len(rows))
    rows[i] = (rows[i][0], round(r.uniform(1000, 99999), 2))
    return rows


def _reference(rows):
    return "\n".join(f"{name:<14}{value:>12,.2f}" for name, value in rows)


def test_solve():
    r = rng()
    for _ in range(4):
        rows = _gen(r)
        assert solve(list(rows)) == _reference(rows)
