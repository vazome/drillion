def solve(xs: list[int]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    return [r.randint(10, 99) for _ in range(r.randint(5, 10))]


def _reference(xs):
    return {
        "trim": xs[1:-1],
        "odds": xs[1::2],
        "rev": xs[::-1],
        "inner": xs[1:-1:2],
        "last3": xs[-3:],
    }


def test_solve():
    r = rng()
    for _ in range(4):
        xs = _gen(r)
        assert solve(list(xs)) == _reference(xs)
