def solve(capacity: int, items: list[tuple[int, int]]) -> int:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    items = [(r.randint(1, 40), r.randint(1, 100)) for _ in range(r.randint(25, 28))]
    return sum(w for w, _ in items) // r.choice([2, 3]), items


def _reference(capacity, items):
    from functools import cache

    @cache
    def best(index, left):
        if index == len(items):
            return 0
        weight, value = items[index]
        skip = best(index + 1, left)
        if weight > left:
            return skip
        return max(skip, value + best(index + 1, left - weight))

    return best(0, capacity)


def test_solve():
    r = rng()
    known = [
        (100, [], 0),
        (10, [(5, 10), (4, 40), (6, 30), (4, 50)], 90),
        (10, [(2, 15), (3, 20), (2, 10)], 45),
        (0, [(1, 1)], 0),
        (4, [(5, 100)], 0),
    ]
    for capacity, items, want in known:
        assert solve(capacity, list(items)) == want, f"{capacity} {items} is {want}"

    for _ in range(3):
        capacity, items = _gen(r)
        assert solve(capacity, list(items)) == _reference(capacity, tuple(items)), (
            f"capacity={capacity} items={items}"
        )
