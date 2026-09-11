import random


def solve(latencies, k):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    # a small pool of values, so bursts of identical latencies are the normal case
    pool = [r.randint(10, 40) * 5 for _ in range(r.randint(2, 6))]
    latencies = [r.choice(pool) for _ in range(r.randint(1, 25))]
    return latencies, r.randint(1, len(latencies))


def _reference(latencies, k):
    pivot = random.choice(latencies)
    bigger = [v for v in latencies if v > pivot]
    same = [v for v in latencies if v == pivot]
    if k <= len(bigger):
        return _reference(bigger, k)
    if k <= len(bigger) + len(same):
        return pivot
    smaller = [v for v in latencies if v < pivot]
    return _reference(smaller, k - len(bigger) - len(same))


def test_solve():
    r = rng()
    for _ in range(60):
        latencies, k = _gen(r)
        original = list(latencies)
        got = solve(latencies, k)
        assert got == sorted(latencies)[-k], f"latencies={original}, k={k}"
        assert got == _reference(latencies, k), f"latencies={original}, k={k}"
        assert latencies == original, f"solve must not disturb its input: {original}"

    assert solve([7], 1) == 7
    assert solve([120, 45, 300, 45, 89], 1) == 300
    assert solve([120, 45, 300, 45, 89], 4) == 45

    # repeats are counted, not collapsed: a two-bucket split loses them
    assert solve([9, 9, 4], 2) == 9, "the second slowest of [9, 9, 4] is 9, not 4"
    assert solve([5, 5, 5, 5], 3) == 5
    assert solve([2, 8, 8, 8, 1], 2) == 8, "three 8s means k=2, 3 and 4 are all 8"
    assert solve([2, 8, 8, 8, 1], 5) == 1
