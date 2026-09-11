from collections import deque


def solve(load, window):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    load = [r.randint(0, 9) for _ in range(r.randint(1, 16))]  # a small range, so ties are common
    return load, r.randint(1, len(load))


def _reference(load, window):
    dq, out = deque(), []
    for i, value in enumerate(load):
        while dq and load[dq[-1]] < value:  # strictly less, so the earliest of equal peaks survives
            dq.pop()
        dq.append(i)
        if dq[0] <= i - window:
            dq.popleft()
        if i >= window - 1:
            out.append((dq[0], load[dq[0]]))
    return out


def _slow(load, window):
    out = []
    for start in range(len(load) - window + 1):
        piece = load[start : start + window]
        peak = max(piece)
        out.append((start + piece.index(peak), peak))
    return out


def test_solve():
    r = rng()
    for _ in range(40):
        load, window = _gen(r)
        original = list(load)
        want = _slow(load, window)
        assert _reference(load, window) == want, "grader bug"
        assert solve(load, window) == want, f"load={original} window={window}"
        assert load == original, f"solve must not disturb its input: {original}"

    assert solve([4, 1, 7, 7, 2], 3) == [(2, 7), (2, 7), (2, 7)], "earliest minute on a tie"
    assert solve([9, 8], 1) == [(0, 9), (1, 8)], "window 1 is one entry per minute"
    assert solve([3, 3, 3], 3) == [(0, 3)], "an all-equal window reports its first minute"

    # index() over the whole list reports a minute that is not even in the window
    assert solve([5, 1, 5], 2) == [(0, 5), (2, 5)], "the minute must lie inside its own window"
    got = solve([1, 9, 2, 2, 9, 1], 2)
    assert got == [(1, 9), (1, 9), (2, 2), (4, 9), (4, 9)], f"windows of 2 over one dip: {got}"
    assert len(solve(list(range(10)), 4)) == 7, "there are len - window + 1 windows"
