def solve(number):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    if r.random() < 0.3:
        return r.randint(1, 20)
    return r.randint(1, 500000)


def _reference(number):
    if number <= 0:
        raise ValueError("Only positive integers are allowed")
    count = 0
    while number > 1:
        number = number * 3 + 1 if number % 2 else number // 2
        count += 1
    return count


def test_solve():
    r = rng()
    for _ in range(6):
        number = _gen(r)
        assert solve(number) == _reference(number), f"number {number}"

    # canonical cases (exercism/python practice/collatz-conjecture)
    assert solve(1) == 0
    assert solve(16) == 4
    assert solve(12) == 9
    assert solve(1000000) == 152

    for bad in [0, -15, -r.randint(1, 1000)]:
        with pytest.raises(ValueError, match=r"^Only positive integers are allowed$"):
            solve(bad)
