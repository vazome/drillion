def solve(weights: list[int]) -> bool:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    weights = [r.randint(1, 25) for _ in range(r.randint(10, 18))]
    if r.random() < 0.5:  # half the batches are plantedly splittable, half are luck
        weights += [sum(weights) % 2]
        weights = [w for w in weights if w]
    return weights


def _reference(weights):
    total = sum(weights)
    if total % 2:
        return False
    half = total // 2
    reachable = {0}
    for weight in weights:
        reachable |= {reached + weight for reached in reachable if reached + weight <= half}
    return half in reachable


def test_solve():
    r = rng()
    known = [
        ([], True),
        ([4], False),
        ([1, 3], False),
        ([2, 2, 3], False),
        ([3, 1, 1, 2, 2, 1], True),
        # heaviest-first onto the lighter van makes 5, 5, 7 and misses the 6, 6 split
        ([3, 3, 2, 2, 2], True),
        ([8, 7, 5, 4, 3, 3], True),
    ]
    for weights, want in known:
        got = solve(list(weights))
        assert got is want, f"{weights} splits evenly: {want} (got {got!r})"

    for _ in range(8):
        weights = _gen(r)
        got, want = solve(list(weights)), _reference(weights)
        assert got is want, f"weights={weights} splits evenly: {want} (got {got!r})"
