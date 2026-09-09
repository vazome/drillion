def solve(rows: list[tuple], threshold: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _reference(rows, threshold):
    return {name: round(sum(samples) / len(samples), 2)
            for name, *samples in rows
            if samples and any(value >= threshold for value in samples)}


def _gen(r):
    names = r.sample(["cpu", "memory", "disk", "queue", "latency", "errors"], r.randint(3, 6))
    rows = [(name, *(r.randint(0, 100) for _ in range(r.randint(1, 5))))
            for name in names]
    return rows, r.randint(20, 80)


def test_solve():
    rows = [("cpu", 20, 80), ("disk", 10, 15), ("queue", 90)]
    assert solve(rows, 75) == {"cpu": 50.0, "queue": 90.0}
    r = rng()
    for _ in range(6):
        rows, threshold = _gen(r)
        assert solve(list(rows), threshold) == _reference(rows, threshold)
