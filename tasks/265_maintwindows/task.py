def solve(booked, proposed):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from itertools import pairwise

from _lib import rng


def _gen(r):
    booked = []
    for _ in range(r.randint(0, 7)):
        start = r.randrange(0, 1400, 10)
        booked.append((start, start + r.choice([0, 10, 30, 120, 600])))  # some nest inside others
    start = r.randrange(0, 1400, 10)
    return booked, (start, start + r.choice([0, 20, 90, 400]))


def _reference(booked, proposed):
    merged = []
    for start, end in sorted([*booked, proposed]):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _covered(windows):
    return {minute for start, end in windows for minute in range(start, end + 1)}


def test_solve():
    r = rng()
    for _ in range(40):
        booked, proposed = _gen(r)
        original = list(booked)
        got = solve(booked, proposed)
        assert got == _reference(booked, proposed), f"booked={original} proposed={proposed}"
        assert booked == original, f"solve must not disturb its input: {original}"
        # the merged windows must cover the same minutes as the originals, no more, no fewer
        assert _covered(got) == _covered([*booked, proposed]), f"coverage changed: {original}"
        assert all(a[1] < b[0] for a, b in pairwise(got)), f"windows still touch: {got}"

    assert solve([(60, 180), (150, 240), (240, 270)], (600, 660)) == [(60, 270), (600, 660)]
    assert solve([], (30, 45)) == [(30, 45)]
    assert solve([(120, 180)], (120, 120)) == [(120, 180)], "a zero-length window merges in"
    assert solve([(60, 120)], (120, 180)) == [(60, 180)], "touching windows are one outage"
    assert solve([(60, 120)], (121, 180)) == [(60, 120), (121, 180)], "a one-minute gap is a gap"

    # taking the newer end on a merge shortens a long window that contains a short one
    assert solve([(0, 600)], (60, 120)) == [(0, 600)], "the merged end is the later of the two"
    assert solve([(0, 600), (60, 120), (30, 90)], (10, 20)) == [(0, 600)], "all nested inside one"
