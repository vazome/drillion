def solve(values, pct):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    values = [round(r.uniform(0.001, 3.0), 3) for _ in range(r.randint(1, 40))]
    return values, r.choice([50, 90, 95, 99, 100])


def _reference(values, pct):
    import math
    return sorted(values)[math.ceil(pct / 100 * len(values)) - 1]


def test_solve():
    r = rng()
    for _ in range(6):
        values, pct = _gen(r)
        assert solve(list(values), pct) == _reference(values, pct)
