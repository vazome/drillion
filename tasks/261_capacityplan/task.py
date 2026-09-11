def solve(files, hours):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    files = [r.randint(1, 400) for _ in range(r.randint(1, 9))]
    return files, r.randint(len(files), len(files) * 4)


def _hours_needed(files, capacity):
    return sum(-(-n // capacity) for n in files)


def _reference(files, hours):
    lo, hi = 1, max(files)
    while lo < hi:
        mid = (lo + hi) // 2
        if _hours_needed(files, mid) <= hours:
            hi = mid
        else:
            lo = mid + 1
    return lo


def test_solve():
    r = rng()
    for _ in range(60):
        files, hours = _gen(r)
        got = solve(files, hours)
        assert got == _reference(files, hours), f"files={files}, hours={hours}"
        assert isinstance(got, int), f"return the capacity as an int: files={files}"
        # it fits, and one row an hour less does not: that is what "smallest" means
        assert _hours_needed(files, got) <= hours, f"{got} does not fit: files={files}, hours={hours}"
        assert got == 1 or _hours_needed(files, got - 1) > hours, (
            f"{got - 1} also fits, so {got} is not the smallest: files={files}, hours={hours}"
        )

    # a leftover row still needs an hour of its own; floor division says capacity 3 fits here
    assert solve([3, 6, 7, 11], 8) == 4
    assert solve([3, 6, 7, 11], 4) == 11, "one hour per file means capacity = the biggest file"
    assert solve([30, 11, 23, 4, 20], 5) == 30
    assert solve([12], 1) == 12
