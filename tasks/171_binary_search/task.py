def solve(values: list[int] | list[object], target: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    values = sorted(r.sample(range(-60, 400), r.randint(0, 25)))
    if values and r.random() < 0.7:
        return values, r.choice(values)
    return values, r.randint(-70, 410)


def _reference(values, target):
    low, high = 0, len(values) - 1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] > target:
            high = middle - 1
        elif values[middle] < target:
            low = middle + 1
        else:
            return middle
    raise ValueError("value not in array")


def _outcome(fn, values, target):
    try:
        return ("ok", fn(values, target))
    except ValueError as err:
        return ("error", str(err))


def test_solve():
    r = rng()
    for _ in range(6):
        values, target = _gen(r)
        assert _outcome(solve, values, target) == _outcome(_reference, values, target), \
            f"values {values}, target {target}"

    # canonical cases (exercism/python practice/binary-search)
    assert solve([6], 6) == 0, "one element"
    assert solve([1, 3, 4, 6, 8, 9, 11], 6) == 3, "middle of the array"
    assert solve([1, 3, 4, 6, 8, 9, 11], 1) == 0, "beginning of the array"
    assert solve([1, 3, 4, 6, 8, 9, 11], 11) == 6, "end of the array"
    assert solve([1, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 634], 144) == 9, "odd length"
    assert solve([1, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377], 21) == 5, "even length"

    with pytest.raises(ValueError, match=r"^value not in array$"):
        solve([1, 3, 4, 6, 8, 9, 11], 7)
    with pytest.raises(ValueError, match=r"^value not in array$"):
        solve([], 1)
    with pytest.raises(ValueError, match=r"^value not in array$"):
        solve([1, 2], 0)
