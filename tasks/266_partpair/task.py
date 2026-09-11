def solve(sizes, target):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    sizes = sorted(r.choice([2, 4, 4, 5, 8, 9, 11, 16]) for _ in range(r.randint(0, 9)))
    return sizes, r.randint(4, 24)  # small values, so exact hits and equal pairs both turn up


def _reference(sizes, target):
    low, high = 0, len(sizes) - 1
    while low < high:
        total = sizes[low] + sizes[high]
        if total == target:
            return (sizes[low], sizes[high])
        if total < target:
            low += 1
        else:
            high -= 1
    return None


def _slow(sizes, target):
    for i in range(len(sizes)):
        for j in range(i + 1, len(sizes)):
            if sizes[i] + sizes[j] == target:
                return (sizes[i], sizes[j])
    return None


def test_solve():
    r = rng()
    for _ in range(60):
        sizes, target = _gen(r)
        original = list(sizes)
        want = _slow(sizes, target)
        assert _reference(sizes, target) == want, "grader bug"
        got = solve(sizes, target)
        assert got == want, f"sizes={original} target={target}"
        assert sizes == original, f"solve must not disturb its input: {original}"
        if got is not None:
            assert got[0] <= got[1], f"return (smaller, larger): {got}"

    assert solve([1, 2, 3, 4, 5], 6) == (1, 5), "smallest first size when several pairs work"
    assert solve([2, 4, 4, 9], 8) == (4, 4), "two shards of the same size are two shards"
    assert solve([2, 4, 9], 8) is None
    assert solve([], 8) is None
    assert solve([1, 3, 5, 7], 12) == (5, 7)
    assert solve([0, 0], 0) == (0, 0), "a zero-size shard is a shard"

    # one shard cannot fill a part with itself
    assert solve([4], 8) is None, "two different shards, so a lone 4 is not a pair"
    assert solve([1, 4, 9], 8) is None, "the single 4 must not pair with itself"
    assert solve([3], 6) is None, "low < high, strictly"
