def solve(iterable: list[None] | list[int | None] | list[int | list[int | list[int | list[object]] | list[list[object]]]] | list[int | list[int | list[int] | list[list[None]] | list[list[object]] | None]] | list[int | list[int | list[int] | list[list[object]]]] | list[int | list[int]] | list[int] | list[list[list[None] | None] | list[list[list[None]]] | None] | list[list[list[object]]] | list[object]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _nest(r, depth):
    items = []
    for _ in range(r.randint(0, 4)):
        roll = r.random()
        if roll < 0.15:
            items.append(None)
        elif roll < 0.15 + 0.30 * depth:
            items.append(_nest(r, depth - 1))
        else:
            items.append(r.randint(-50, 200))
    return items


def _gen(r):
    return _nest(r, r.randint(1, 5))


def _reference(iterable):
    flattened = []
    for item in iterable:
        if isinstance(item, list):
            flattened.extend(_reference(item))
        elif item is not None:
            flattened.append(item)
    return flattened


def test_solve():
    r = rng()
    for _ in range(6):
        iterable = _gen(r)
        assert solve(iterable) == _reference(iterable), f"iterable {iterable!r}"

    # canonical cases (exercism/python practice/flatten-array)
    assert solve([]) == []
    assert solve([0, 1, 2]) == [0, 1, 2]
    assert solve([[[]]]) == []
    assert solve([1, [2, 3, 4, 5, 6, 7], 8]) == [1, 2, 3, 4, 5, 6, 7, 8]
    assert solve([0, 2, [[2, 3], 8, 100, 4, [[[50]]]], -2]) == [0, 2, 2, 3, 8, 100, 4, 50, -2]
    assert solve([1, [2, [[3]], [4, [[5]]], 6, 7], 8]) == [1, 2, 3, 4, 5, 6, 7, 8]
    assert solve([1, 2, None]) == [1, 2]
    assert solve([None, None, 3]) == [3]
    assert solve([0, 2, [[2, 3], 8, [[100]], None, [[None]]], -2]) == [0, 2, 2, 3, 8, 100, -2]
    assert solve([None, [[[None]]], None, None, [[None, None], None], None]) == []
