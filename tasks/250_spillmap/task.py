from collections import deque


def solve(floor, start):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    height, width = r.randint(4, 7), r.randint(4, 8)
    floor = [
        "".join("#" if r.random() < 0.3 else "." for _ in range(width)) for _ in range(height)
    ]
    row, col = r.randrange(height), r.randrange(width)
    # half the drills start against an edge, where a negative index quietly wraps
    if r.random() < 0.5:
        row, col = r.choice([(0, col), (height - 1, col), (row, 0), (row, width - 1)])
    return floor, (row, col)


def _reference(floor, start):
    cells = [list(line) for line in floor]
    height, width = len(cells), len(cells[0])
    row, col = start
    if cells[row][col] == ".":
        cells[row][col] = "~"
        queue = deque([(row, col)])
        while queue:
            row, col = queue.popleft()
            for next_row, next_col in (
                (row - 1, col),
                (row + 1, col),
                (row, col - 1),
                (row, col + 1),
            ):
                inside = 0 <= next_row < height and 0 <= next_col < width
                if inside and cells[next_row][next_col] == ".":
                    cells[next_row][next_col] = "~"
                    queue.append((next_row, next_col))
    return ["".join(line) for line in cells]


def test_solve():
    r = rng()
    for _ in range(12):
        floor, start = _gen(r)
        untouched = list(floor)
        got, want = solve(floor, start), _reference(floor, start)
        assert got == want, "spill from {}:\n{}\nexpected\n{}\ngot\n{}".format(
            start, "\n".join(floor), "\n".join(want), "\n".join(got)
        )
        assert floor == untouched, "hand back a new map, leave the one you were given alone"

    # column -1 of row 0 is the far end of the same row, and there is a wall between them
    edge = ["..#.", "####"]
    assert solve(edge, (0, 0)) == ["~~#.", "####"], "the map does not wrap around at the edges"
    assert solve(edge, (1, 1)) == edge, "nothing spreads from a cell that is already wall"
    assert solve(["...", ".#.", "..."], (0, 0)) == ["~~~", "~#~", "~~~"], "walls stay walls"
    assert solve([".#", "#."], (0, 0)) == ["~#", "#."], "no spreading through a diagonal corner"
