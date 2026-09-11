def solve(bays: list[list[int]]) -> int:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    rows, cols = r.randint(4, 7), r.randint(4, 7)
    grid = [[r.randint(1, 9) for _ in range(cols)] for _ in range(rows)]
    # one cheap lane and one wall, so a locally greedy walk has something to fall for
    lane = r.randrange(rows)
    for j in range(cols):
        grid[lane][j] = r.choice([1, 1, 40])
    return grid


def _reference(bays):
    row = list(bays[0])
    for j in range(1, len(row)):
        row[j] += row[j - 1]
    for cells in bays[1:]:
        row[0] += cells[0]
        for j in range(1, len(cells)):
            # row[j] is still the row above; row[j - 1] is already this row
            row[j] = cells[j] + min(row[j], row[j - 1])
    return row[-1]


def test_solve():
    r = rng()
    known = [
        ([[7]], 7),
        ([[2, 1], [3, 1], [4, 2]], 6),
        ([[2, 1, 4], [2, 1, 3], [3, 2, 1]], 7),
        ([[1, 2, 3, 4, 5]], 15),
        ([[1], [2], [3]], 6),
        # the cheapest first step walks into a wall: greedy pays 103, the answer is 10
        ([[1, 2, 3], [1, 100, 3], [50, 50, 1]], 10),
    ]
    for bays, want in known:
        assert solve([list(cells) for cells in bays]) == want, f"{bays} costs {want}"

    for _ in range(6):
        bays = _gen(r)
        assert solve([list(cells) for cells in bays]) == _reference(bays), f"bays={bays}"

    # the caller's grid is the caller's: adding the running totals into it is a side effect
    bays = _gen(r)
    before = [list(cells) for cells in bays]
    solve(bays)
    assert bays == before, "leave the grid you were handed unchanged"
