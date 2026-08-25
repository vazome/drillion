def solve(scores):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    base = r.sample(range(1, 60), r.randint(3, 7))
    # always duplicate the maximum: sorted(vals)[-2] without a set must fail
    vals = base + [max(base)] + [r.choice(base) for _ in range(r.randint(0, 2))]
    r.shuffle(vals)
    return vals


def _reference(scores):
    return sorted(set(scores))[-2]


def test_solve():
    r = rng()
    for _ in range(4):
        s = _gen(r)
        assert solve(list(s)) == _reference(s)
