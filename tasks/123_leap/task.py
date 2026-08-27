def solve(year: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    kind = r.randrange(4)
    if kind == 0:                                   # century years: the interesting ones
        return 100 * r.randrange(15, 25)
    if kind == 1:
        return 400 * r.randrange(4, 7)
    if kind == 2:
        return 4 * r.randrange(400, 600)
    return r.randrange(1500, 2500)


def _reference(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def test_solve():
    r = rng()
    for _ in range(6):
        year = _gen(r)
        assert solve(year) == _reference(year), f"year {year}"

    # canonical cases (exercism/python practice/leap)
    assert solve(2015) is False
    assert solve(1996) is True
    assert solve(2100) is False
    assert solve(2000) is True
    assert solve(1800) is False
