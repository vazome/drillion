def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from dataclasses import FrozenInstanceError, dataclass, fields, is_dataclass

import pytest
from _lib import rng


def _gen(r):
    """Two squares, biased towards the three ways a queen can attack."""
    row, column = r.randint(0, 7), r.randint(0, 7)
    match r.choice(["row", "column", "diagonal", "any", "any"]):
        case "row":
            other = (row, r.randint(0, 7))
        case "column":
            other = (r.randint(0, 7), column)
        case "diagonal":
            step = r.choice([-1, 1]) * r.randint(0, 7)
            other = (row + step, column + step)
        case _:
            other = (r.randint(0, 7), r.randint(0, 7))
    return (row, column), other


def _reference():
    @dataclass(frozen=True)
    class Position:
        row: int
        column: int

        def __post_init__(self):
            if not (0 <= self.row <= 7 and 0 <= self.column <= 7):
                raise ValueError("off the board")

        def can_attack(self, other):
            return (
                self.row == other.row
                or self.column == other.column
                or abs(self.row - other.row) == abs(self.column - other.column)
            )

    return Position


def _on_board(square):
    return all(0 <= n <= 7 for n in square)


def test_solve():
    r = rng()
    mine, reference = solve(), _reference()

    assert is_dataclass(mine), "Position must be a dataclass"
    assert [f.name for f in fields(mine)] == ["row", "column"], (
        "the fields are row then column, positional"
    )
    with pytest.raises(FrozenInstanceError):
        p = mine(0, 0)
        p.row = 4  # a frozen dataclass refuses this

    assert mine(2, 3) == mine(2, 3), "equal by value: that is what the dataclass is for"
    assert mine(2, 3) != mine(3, 2)
    assert len({mine(2, 3), mine(2, 3)}) == 1, "frozen means hashable"

    for bad in [(-1, 0), (0, -1), (8, 0), (0, 8), (9, 9)]:
        with pytest.raises(ValueError):
            mine(*bad)

    cases = [((2, 3), (2, 7)), ((2, 3), (5, 6)), ((2, 3), (4, 7)), ((0, 0), (7, 7))]
    cases += [pair for pair in (_gen(r) for _ in range(60)) if _on_board(pair[1])]
    for here, there in cases:
        want = reference(*here).can_attack(reference(*there))
        got = mine(*here).can_attack(mine(*there))
        assert got == want, f"a queen on {here} against {there} is {want}"
