from itertools import accumulate


def solve(readings, ranges):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    readings = [r.choice([r.randint(0, 90), r.randint(0, 90), -r.randint(0, 30), 0]) for _ in range(r.randint(1, 18))]
    last = len(readings) - 1
    ranges = []
    for _ in range(r.randint(0, 8)):
        a = r.randint(0, last)
        ranges.append((a, r.randint(a, last)))
    return readings, ranges


def _reference(readings, ranges):
    table = list(accumulate(readings, initial=0))
    return [table[last + 1] - table[first] for first, last in ranges]


def test_solve():
    r = rng()
    for _ in range(40):
        readings, ranges = _gen(r)
        original = list(readings)
        want = [sum(readings[first : last + 1]) for first, last in ranges]
        assert _reference(readings, ranges) == want, "grader bug"
        assert solve(readings, ranges) == want, f"readings={original} ranges={ranges}"
        assert readings == original, f"solve must not disturb its input: {original}"

    assert solve([3, 1, 4, 1, 5], [(0, 1), (2, 4), (3, 3), (0, 4)]) == [4, 10, 1, 14]
    assert solve([], []) == []
    assert solve([7], []) == [], "no ranges asked, nothing to answer"

    # a one-day range is the reading itself; dropping the first day makes every one of these 0
    assert solve([3, 1, 4, 1, 5], [(0, 0), (1, 1), (4, 4)]) == [3, 1, 5], "both ends are included"
    # a range that does not start at day 0 is where an off-by-one shows up as a plausible number
    assert solve([10, 20, 30, 40], [(1, 3)]) == [90], "days 1, 2 and 3, not 2 and 3"
    assert solve([5, -5, 5], [(0, 2), (1, 2)]) == [5, 0], "negative readings are real readings"
