def solve(matrix: list[list[int] | list[object]] | list[list[int]] | list[object]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    roll = r.random()
    if roll < 0.08:
        return []
    rows = r.randint(1, 5)
    columns = r.randint(1, 5)
    highest = r.choice([2, 4, 9])
    matrix = [[r.randint(0, highest) for _ in range(columns)] for _ in range(rows)]
    if roll > 0.90 and rows > 1:
        matrix[r.randrange(rows)].pop()
    return matrix


def _reference(matrix):
    if not matrix:
        return []
    if any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("irregular matrix")
    row_max = [max(row) for row in matrix]
    column_min = [min(column) for column in zip(*matrix)]
    return [{"row": index + 1, "column": spot + 1}
            for index, _ in enumerate(matrix)
            for spot, _ in enumerate(matrix[0])
            if row_max[index] == column_min[spot]]


def _sorted(points):
    return sorted(points, key=lambda point: (point["row"], point["column"]))


def _outcome(fn, matrix):
    try:
        return ("ok", _sorted(fn(matrix)))
    except ValueError as err:
        return ("error", str(err))


def test_solve():
    r = rng()
    for _ in range(6):
        matrix = _gen(r)
        assert _outcome(solve, matrix) == _outcome(_reference, matrix), f"matrix {matrix!r}"

    # canonical cases (exercism/python practice/saddle-points)
    assert _sorted(solve([[9, 8, 7], [5, 3, 2], [6, 6, 7]])) == [{"row": 2, "column": 1}]
    assert _sorted(solve([])) == []
    assert _sorted(solve([[1, 2, 3], [3, 1, 2], [2, 3, 1]])) == []
    assert _sorted(solve([[4, 5, 4], [3, 5, 5], [1, 5, 4]])) == [
        {"row": 1, "column": 2}, {"row": 2, "column": 2}, {"row": 3, "column": 2}]
    assert _sorted(solve([[6, 7, 8], [5, 5, 5], [7, 5, 6]])) == [
        {"row": 2, "column": 1}, {"row": 2, "column": 2}, {"row": 2, "column": 3}]
    assert _sorted(solve([[3, 1, 3], [3, 2, 4]])) == [
        {"row": 1, "column": 1}, {"row": 1, "column": 3}]
    assert _sorted(solve([[2], [1], [4], [1]])) == [
        {"row": 2, "column": 1}, {"row": 4, "column": 1}]
    assert _sorted(solve([[2, 5, 3, 5]])) == [
        {"row": 1, "column": 2}, {"row": 1, "column": 4}]

    with pytest.raises(ValueError, match=r"^irregular matrix$"):
        solve([[3, 2, 1], [0, 1], [2, 1, 0]])
