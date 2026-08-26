def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng


def _gen(r):
    n = r.randint(1, 12)
    if r.random() < 0.35:
        pool = [r.randrange(0, 101, 10) for _ in range(3)]  # ties everywhere
        return [r.choice(pool) for _ in range(n)]
    return [r.randrange(0, 1000, 5) for _ in range(n)]


def _reference():
    class HighScores:
        def __init__(self, scores):
            self.scores = scores

        def latest(self):
            return self.scores[-1]

        def personal_best(self):
            return max(self.scores)

        def personal_top_three(self):
            return sorted(self.scores, reverse=True)[:3]

    return HighScores


def test_solve():
    r = rng()
    HighScores = solve()
    assert inspect.isclass(HighScores), "solve() must return a class"
    Reference = _reference()
    for _ in range(6):
        scores = _gen(r)
        mine, theirs = HighScores(list(scores)), Reference(list(scores))
        assert mine.personal_top_three() == theirs.personal_top_three(), f"top three of {scores}"
        assert mine.personal_best() == theirs.personal_best(), f"best of {scores}"
        assert mine.latest() == theirs.latest(), f"latest of {scores}"
        assert mine.scores == scores, f"scores must stay in the order given: {scores}"

    # canonical cases (exercism/python practice/high-scores)
    assert HighScores([30, 50, 20, 70]).scores == [30, 50, 20, 70]
    assert HighScores([100, 0, 90, 30]).latest() == 30
    assert HighScores([40, 100, 70]).personal_best() == 100
    assert HighScores([10, 30, 90, 30, 100, 20, 10, 0, 30, 40, 40, 70, 70]).personal_top_three() == [100, 90, 70]
    assert HighScores([40, 20, 40, 30]).personal_top_three() == [40, 40, 30]
    assert HighScores([30, 70]).personal_top_three() == [70, 30]
