def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    return None


def _reference():
    return {1: "b", 2: "c", 3: "b", 4: "b", 5: "c", 6: "b", 7: "c", 8: "b", 9: "b", 10: "b"}


def test_solve():
    rng()
    got = solve()
    want = _reference()
    assert set(got) == set(want), f"answer all of {sorted(want)}"
    wrong = [q for q in want if got[q] != want[q]]
    assert not wrong, f"re-think question(s) {wrong}"
