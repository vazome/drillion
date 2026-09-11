def solve(deltas: list[int]) -> tuple[int, int, int]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    size = r.randint(8, 20)
    if r.random() < 0.2:
        return [r.randint(1, 30) for _ in range(size)]  # nothing ever drops
    return [r.randint(-40, 25) for _ in range(size)]


def _reference(deltas):
    total = run = deltas[0]
    start = best_start = best_end = 0
    for i in range(1, len(deltas)):
        delta = deltas[i]
        if run > 0:
            run, start = delta, i  # carrying a gain forward only makes the stretch better
        else:
            run += delta
        if run < total:
            total, best_start, best_end = run, start, i
    return best_start, best_end, total


def test_solve():
    r = rng()
    known = [
        ([5], (0, 0, 5)),
        ([-7], (0, 0, -7)),
        ([0, 0, 0], (0, 0, 0)),
        # nothing drops, so the worst stretch is the single smallest reading, not nothing
        ([3, 1, 2], (1, 1, 1)),
        ([2, -8, 3, -2, 4, -10], (1, 5, -13)),
        ([-4, 6, -1, -1, 6, -4], (0, 0, -4)),
    ]
    for deltas, want in known:
        assert solve(list(deltas)) == want, f"{deltas} drops most over {want}"

    for _ in range(8):
        deltas = _gen(r)
        got = solve(list(deltas))
        assert tuple(got) == _reference(deltas), f"deltas={deltas}"
        start, end, total = got
        assert sum(deltas[start : end + 1]) == total, f"{deltas}: window and total disagree"
