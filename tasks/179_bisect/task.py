def solve(thresholds: list[int], labels: list[str], values: list[int]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    thresholds = sorted(r.sample(range(50, 2000), r.randint(2, 4)))
    names = ["fast", "normal", "slow", "critical", "dead"]
    labels = names[: len(thresholds) + 1]
    values = [r.choice(thresholds) for _ in range(3)]  # the boundary cases, always
    values += [r.randint(0, 2500) for _ in range(r.randint(3, 8))]
    r.shuffle(values)
    return thresholds, labels, values


def _reference(thresholds, labels, values):
    from bisect import bisect_right
    return [labels[bisect_right(thresholds, v)] for v in values]


def test_solve():
    r = rng()
    cases = [([100, 300, 1000], ["fast", "normal", "slow", "critical"], [99, 100, 300, 5000])]
    for _ in range(6):
        cases.append(_gen(r))
    for thresholds, labels, values in cases:
        assert solve(thresholds, labels, values) == _reference(thresholds, labels, values), (
            f"thresholds={thresholds} values={values}")
