def solve(readings: list[int]) -> int:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    value = r.randint(50, 200)
    readings = []
    for _ in range(r.randint(30, 45)):
        value += r.randint(-25, 20)  # drifts up on average, noisy enough to break a consecutive scan
        readings.append(value)
    return readings


def _reference(readings):
    best = []
    for i, value in enumerate(readings):
        best.append(1 + max((best[j] for j in range(i) if readings[j] < value), default=0))
    return max(best, default=0)


def test_solve():
    r = rng()
    known = [
        ([], 0),
        ([7], 1),
        ([9, 8, 7, 6, 5], 1),
        ([5, 5, 5], 1),
        ([10, 22, 9, 33, 21, 50, 41, 60, 80], 6),
        ([4, 8, 7, 5, 1, 12, 2, 3, 9], 4),
    ]
    for readings, want in known:
        assert solve(list(readings)) == want, f"{readings} improves for {want}"

    for _ in range(6):
        readings = _gen(r)
        assert solve(list(readings)) == _reference(readings), f"readings={readings}"
