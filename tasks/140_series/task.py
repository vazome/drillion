def solve(series: str, length: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    digits = "".join(str(r.randrange(10)) for _ in range(r.randint(0, 12)))
    if r.random() < 0.15:
        digits = str(r.randrange(10)) * r.randint(2, 6)
    roll = r.random()
    if roll < 0.12:
        length = 0
    elif roll < 0.24:
        length = -r.randint(1, 4)
    elif roll < 0.4 or not digits:
        length = r.randint(len(digits) + 1, len(digits) + 6)
    else:
        length = r.randint(1, len(digits))
    return digits, length


def _reference(series, length):
    if not series:
        raise ValueError("series cannot be empty")
    if length == 0:
        raise ValueError("slice length cannot be zero")
    if length < 0:
        raise ValueError("slice length cannot be negative")
    if length > len(series):
        raise ValueError("slice length cannot be greater than series length")
    return [series[start:start + length] for start in range(len(series) - length + 1)]


def _outcome(fn, series, length):
    try:
        return ("ok", fn(series, length))
    except ValueError as err:
        return ("error", str(err))


def test_solve():
    r = rng()
    for _ in range(6):
        series, length = _gen(r)
        assert _outcome(solve, series, length) == _outcome(_reference, series, length), \
            f"series {series!r}, length {length}"

    # canonical cases (exercism/python practice/series)
    assert solve("1", 1) == ["1"]
    assert solve("12", 1) == ["1", "2"]
    assert solve("9142", 2) == ["91", "14", "42"]
    assert solve("777777", 3) == ["777", "777", "777", "777"]
    assert solve("918493904243", 5) == ["91849", "18493", "84939", "49390", "93904",
                                        "39042", "90424", "04243"]

    with pytest.raises(ValueError, match=r"^slice length cannot be greater than series length$"):
        solve("12345", 6)
    with pytest.raises(ValueError, match=r"^slice length cannot be zero$"):
        solve("12345", 0)
    with pytest.raises(ValueError, match=r"^slice length cannot be negative$"):
        solve("123", -1)
    with pytest.raises(ValueError, match=r"^series cannot be empty$"):
        solve("", 1)
