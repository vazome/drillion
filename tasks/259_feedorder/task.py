def solve(arrivals):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    n = r.randint(0, 14)
    values = [r.randint(1, 12) for _ in range(n)]
    return values


def _reference(arrivals):
    if len(arrivals) <= 1:
        return list(arrivals), 0
    mid = len(arrivals) // 2
    left, left_swaps = _reference(arrivals[:mid])
    right, right_swaps = _reference(arrivals[mid:])
    merged, swaps = [], left_swaps + right_swaps
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
            swaps += len(left) - i  # everything still queued on the left crossed this item
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, swaps


def test_solve():
    r = rng()
    for _ in range(40):
        arrivals = _gen(r)
        original = list(arrivals)
        got = solve(arrivals)
        assert got == _reference(arrivals), f"arrivals={original}"
        assert arrivals == original, f"solve must not disturb its input: {original}"
        assert got[0] is not arrivals, "return a new list, not the one you were given"

    assert solve([]) == ([], 0)
    assert solve([7]) == ([7], 0)
    assert solve([2, 2, 2]) == ([2, 2, 2], 0), "equal numbers are not out of order"

    # neighbours out of order is a different, smaller number than pairs out of order
    assert solve([3, 1, 2]) == ([1, 2, 3], 2), "3 is ahead of both 1 and 2: that is two pairs"
    assert solve([5, 4, 3, 2, 1]) == ([1, 2, 3, 4, 5], 10), "a reversed feed has n*(n-1)/2 pairs"
