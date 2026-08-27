def solve(from_base: int, digits: list[int] | list[object], to_base: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    from_base = r.randint(2, 40)
    to_base = r.randint(2, 40)
    digits = [r.randrange(from_base) for _ in range(r.randint(0, 6))]
    roll = r.random()
    if roll < 0.10:
        digits = [0] * r.randint(1, 4) + digits          # leading zeros
    elif roll < 0.18:
        from_base = r.randint(-3, 1)                     # bad input base
    elif roll < 0.26:
        to_base = r.randint(-3, 1)                       # bad output base
    elif roll < 0.36 and digits:
        digits = list(digits)
        digits[r.randrange(len(digits))] = r.choice([-r.randint(1, 5), from_base + r.randint(0, 5)])
    return from_base, digits, to_base


def _reference(from_base, digits, to_base):
    if from_base < 2:
        raise ValueError("input base must be >= 2")
    if to_base < 2:
        raise ValueError("output base must be >= 2")
    if any(digit < 0 or digit >= from_base for digit in digits):
        raise ValueError("all digits must satisfy 0 <= d < input base")
    number = 0
    for digit in digits:
        number = number * from_base + digit
    out = []
    while number > 0:
        number, remainder = divmod(number, to_base)
        out.append(remainder)
    return out[::-1] or [0]


def _outcome(fn, from_base, digits, to_base):
    try:
        return ("ok", fn(from_base, digits, to_base))
    except ValueError as err:
        return ("error", str(err))


def test_solve():
    r = rng()
    for _ in range(6):
        from_base, digits, to_base = _gen(r)
        assert _outcome(solve, from_base, digits, to_base) == \
            _outcome(_reference, from_base, digits, to_base), \
            f"from_base {from_base}, digits {digits}, to_base {to_base}"

    # canonical cases (exercism/python practice/all-your-base)
    assert solve(2, [1, 0, 1, 0, 1, 0], 10) == [4, 2], "binary to multiple decimal"
    assert solve(3, [1, 1, 2, 0], 16) == [2, 10], "trinary to hexadecimal"
    assert solve(97, [3, 46, 60], 73) == [6, 10, 45], "15-bit integer"
    assert solve(7, [0, 6, 0], 10) == [4, 2], "leading zeros"
    assert solve(2, [], 10) == [0], "empty list"
    assert solve(10, [0, 0, 0], 2) == [0], "multiple zeros"

    with pytest.raises(ValueError, match=r"^input base must be >= 2$"):
        solve(1, [0], 10)
    with pytest.raises(ValueError, match=r"^output base must be >= 2$"):
        solve(10, [7], 0)
    with pytest.raises(ValueError, match=r"^all digits must satisfy 0 <= d < input base$"):
        solve(2, [1, 2, 1, 0, 1, 0], 10)
    with pytest.raises(ValueError, match=r"^all digits must satisfy 0 <= d < input base$"):
        solve(2, [1, -1, 1, 0, 1, 0], 10)
    with pytest.raises(ValueError, match=r"^input base must be >= 2$"):
        solve(-2, [1], -7)
