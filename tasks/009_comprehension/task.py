def solve(records):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    names = ["ana", "bo", "cy", "dee", "eli", "fay", "gus", "hal"]
    return [[n, r.randint(0, 100)] for n in r.sample(names, r.randint(4, 8))]


def _reference(records):
    return [name.upper() for name, score in records if score >= 50]


def test_solve():
    r = rng()
    for _ in range(4):
        recs = _gen(r)
        assert solve(recs) == _reference(recs)
