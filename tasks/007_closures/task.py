def solve(n: int, x: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    return r.randint(3, 7), r.randint(2, 12)


def _reference(n, x):
    gs = [lambda: x * i for i in range(n)]  # noqa: B023 — late binding is the point
    late = [g() for g in gs]

    def make(i):
        return lambda: x * i

    fs = [make(i) for i in range(n)]
    frozen = [f() for f in fs]
    return (late, frozen)


def test_solve():
    r = rng()
    for _ in range(4):
        n, x = _gen(r)
        assert solve(n, x) == _reference(n, x)
