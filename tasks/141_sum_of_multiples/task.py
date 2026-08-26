def solve(level, base_values):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    level = r.choice([0, 1, r.randint(2, 30), r.randint(30, 200), r.randint(200, 3000)])
    roll = r.random()
    if roll < 0.08:
        base_values = []
    elif roll < 0.2:
        base_values = sorted({0, *r.sample(range(1, 26), r.randint(1, 3))})
    else:
        base_values = sorted(r.sample(range(1, 51), r.randint(1, 5)))
    return level, base_values


def _reference(level, base_values):
    return sum(value for value in range(level)
               if any(value % base == 0 for base in base_values if base > 0))


def test_solve():
    r = rng()
    for _ in range(6):
        level, base_values = _gen(r)
        assert solve(level, base_values) == _reference(level, base_values), \
            f"level {level}, base_values {base_values}"

    # canonical cases (exercism/python practice/sum-of-multiples)
    assert solve(1, [3, 5]) == 0
    assert solve(20, [3, 5]) == 78
    assert solve(100, [3, 5]) == 2318
    assert solve(10000, [43, 47]) == 2203160
    assert solve(10000, []) == 0
    assert solve(1, [0]) == 0
    assert solve(4, [3, 0]) == 3
    assert solve(10000, [2, 3, 5, 7, 11]) == 39614537
