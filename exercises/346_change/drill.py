def solve(coins, target):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng

PURSES = [[1, 5, 10, 25, 100], [1, 4, 15, 20, 50], [1, 5, 10, 21, 25],
          [2, 5, 10, 20, 50], [1, 10, 11], [4, 5], [1, 2, 5, 10, 20, 50, 100],
          [5, 10], [3, 7], [2, 7, 13]]


def _gen(r):
    coins = r.choice(PURSES)
    roll = r.random()
    if roll < 0.12:
        return coins, 0
    if roll < 0.24:
        return coins, -r.randint(1, 40)
    if roll < 0.42:
        return coins, r.randint(1, 60)          # may or may not be reachable
    handful = [r.choice(coins) for _ in range(r.randint(1, 9))]
    return coins, sum(handful)                  # reachable by construction


def _reference(coins, target):
    if target < 0:
        raise ValueError("target can't be negative")
    best = [None] * (target + 1)
    best[0] = []
    for amount in range(1, target + 1):
        for coin in coins:
            if coin <= amount and best[amount - coin] is not None:
                candidate = best[amount - coin] + [coin]
                if best[amount] is None or len(candidate) < len(best[amount]):
                    best[amount] = candidate
    if best[target] is None:
        raise ValueError("can't make target with given coins")
    return sorted(best[target])


def test_solve():
    r = rng()
    for _ in range(6):
        coins, target = _gen(r)
        case = f"coins {coins}, target {target}"
        try:
            expected = _reference(coins, target)
        except ValueError as err:
            message = str(err)
            with pytest.raises(ValueError, match=f"^{message}$"):
                solve(coins, target)
            continue
        got = solve(coins, target)
        assert isinstance(got, list), f"{case}: expected a list"
        assert sum(got) == target, f"{case}: the coins returned must add up to the target"
        assert set(got) <= set(coins), f"{case}: every coin returned must be an available one"
        assert got == sorted(got), f"{case}: the coins come back smallest first"
        assert len(got) == len(expected), f"{case}: fewest is {len(expected)} coins, e.g. {expected}"

    # canonical cases (exercism/python practice/change)
    assert solve([1, 5, 10, 25, 100], 15) == [5, 10], "multiple coin change"
    assert solve([1, 4, 15, 20, 50], 23) == [4, 4, 15], "change with lilliputian coins"
    assert solve([1, 10, 11], 20) == [10, 10], "a greedy approach is not optimal"
    assert solve([2, 5, 10, 20, 50], 21) == [2, 2, 2, 5, 10], \
        "possible change without unit coins available"
    assert solve([1, 5, 10, 21, 25], 0) == [], "no coins make 0 change"

    with pytest.raises(ValueError, match=r"^can't make target with given coins$"):
        solve([5, 10], 94)
    with pytest.raises(ValueError, match=r"^target can't be negative$"):
        solve([1, 2, 5], -5)
