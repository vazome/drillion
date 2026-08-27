# given — do not edit
SUBLIST = "sublist"
SUPERLIST = "superlist"
EQUAL = "equal"
UNEQUAL = "unequal"


def solve(list_one: list[int] | list[object], list_two: list[int] | list[object]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _contains(big, small):
    return any(big[start:start + len(small)] == small
               for start in range(len(big) - len(small) + 1))


def _reference(list_one, list_two):
    if list_one == list_two:
        return EQUAL
    if _contains(list_one, list_two):
        return SUPERLIST
    if _contains(list_two, list_one):
        return SUBLIST
    return UNEQUAL


def _numbers(r, size):
    return [r.randrange(6) for _ in range(size)]


def _gen(r):
    roll = r.random()
    if roll < 0.20:
        one = _numbers(r, r.randint(0, 6))
        return one, list(one)
    if roll < 0.70:
        big = _numbers(r, r.randint(3, 9))
        start = r.randrange(len(big) + 1)
        end = r.randint(start, len(big))
        run = big[start:end]
        return (big, run) if roll < 0.45 else (run, big)
    return _numbers(r, r.randint(1, 6)), _numbers(r, r.randint(1, 6))


def test_solve():
    r = rng()
    for _ in range(6):
        one, two = _gen(r)
        assert solve(one, two) == _reference(one, two), f"lists {one!r} and {two!r}"

    # canonical cases (exercism/python practice/sublist)
    assert solve([], []) == EQUAL
    assert solve([], [1, 2, 3]) == SUBLIST
    assert solve([1, 2, 3], []) == SUPERLIST
    assert solve([1, 2, 3], [1, 2, 3]) == EQUAL
    assert solve([1, 2, 3], [2, 3, 4]) == UNEQUAL
    assert solve([1, 2, 5], [0, 1, 2, 3, 1, 2, 5, 6]) == SUBLIST
    assert solve([1, 1, 2], [0, 1, 1, 1, 2, 1, 2]) == SUBLIST
    assert solve([0, 1, 2, 3, 4, 5], [2, 3]) == SUPERLIST
    assert solve([1, 2], [1, 22]) == UNEQUAL
    assert solve([1, 0, 1], [10, 1]) == UNEQUAL
