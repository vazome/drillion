def solve(value: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_SMALL_PRIMES = [2, 2, 2, 3, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
_BIG_PRIMES = [101, 211, 461, 997, 4001, 9539, 15013]


def _gen(r):
    value = 1
    for _ in range(r.randint(0, 5)):
        value *= r.choice(_SMALL_PRIMES)
    if r.random() < 0.45:
        value *= r.choice(_BIG_PRIMES)
    return value


def _reference(value):
    found = []
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            found.append(divisor)
            value //= divisor
        divisor += 1
    if value > 1:
        found.append(value)
    return found


def test_solve():
    r = rng()
    for _ in range(6):
        value = _gen(r)
        assert solve(value) == _reference(value), f"value {value!r}"

    # canonical cases (exercism/python practice/prime-factors)
    assert solve(1) == []
    assert solve(2) == [2]
    assert solve(9) == [3, 3]
    assert solve(8) == [2, 2, 2]
    assert solve(12) == [2, 2, 3]
    assert solve(625) == [5, 5, 5, 5]
    assert solve(901255) == [5, 17, 23, 461]
    assert solve(93819012551) == [11, 9539, 894119]
