def solve(readings: list[int], n: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _reference(readings, n):
    from collections import deque
    from itertools import pairwise

    return list(deque((current - previous for previous, current in pairwise(readings)), maxlen=n))


def test_solve():
    assert solve([10, 13, 12, 20, 25], 3) == [-1, 8, 5]
    assert solve([4], 5) == []
    assert solve([1, 3, 7], 0) == []
    r = rng()
    for _ in range(7):
        readings = [r.randint(-20, 100) for _ in range(r.randint(1, 12))]
        n = r.randint(0, 6)
        assert solve(list(readings), n) == _reference(readings, n)
