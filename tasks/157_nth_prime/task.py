def solve(number: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    roll = r.random()
    if roll < 0.15:
        return r.randint(-20, 0)
    if roll < 0.55:
        return r.randint(1, 30)
    return r.randint(30, 1500)


def _is_prime(candidate, primes):
    for prime in primes:
        if prime * prime > candidate:
            return True
        if candidate % prime == 0:
            return False
    return True


def _reference(number):
    if number < 1:
        raise ValueError("there is no zeroth prime")
    primes = [2]
    candidate = 3
    while len(primes) < number:
        if _is_prime(candidate, primes):
            primes.append(candidate)
        candidate += 2
    return primes[number - 1]


def _outcome(fn, number):
    try:
        return ("ok", fn(number))
    except ValueError as err:
        return ("error", str(err))


def test_solve():
    r = rng()
    for _ in range(6):
        number = _gen(r)
        assert _outcome(solve, number) == _outcome(_reference, number), f"number {number!r}"

    # canonical cases (exercism/python practice/nth-prime)
    assert solve(1) == 2
    assert solve(2) == 3
    assert solve(6) == 13
    assert solve(10001) == 104743
    assert [solve(n) for n in range(1, 21)] == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
                                                31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
    for bad in (0, -1):
        with pytest.raises(ValueError, match=r"^there is no zeroth prime$"):
            solve(bad)
