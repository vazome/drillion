def solve(digits: str, span: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import math

import pytest
from _lib import rng


def _gen(r):
    digits = "".join(str(r.randrange(10)) for _ in range(r.randint(0, 14)))
    if r.random() < 0.12:
        digits = r.choice("09") * r.randint(2, 6)
    roll = r.random()
    if roll < 0.10:
        span = 0
    elif roll < 0.20:
        span = -r.randint(1, 4)
    elif roll < 0.34 or not digits:
        span = r.randint(len(digits) + 1, len(digits) + 5)
    else:
        span = r.randint(1, len(digits))
    if r.random() < 0.12 and digits:
        cut = r.randrange(len(digits))
        digits = digits[:cut] + r.choice("abc *-") + digits[cut + 1:]
    return digits, span


def _reference(digits, span):
    if span == 0:
        return 1
    if span > len(digits):
        raise ValueError("span must not exceed string length")
    if span < 0:
        raise ValueError("span must not be negative")
    if not all(char.isdigit() for char in digits):
        raise ValueError("digits input must only contain digits")
    numbers = [int(char) for char in digits]
    return max(math.prod(numbers[start:start + span])
               for start in range(len(numbers) - span + 1))


def _outcome(fn, digits, span):
    try:
        return ("ok", fn(digits, span))
    except ValueError as err:
        return ("error", str(err))


def test_solve():
    r = rng()
    for _ in range(6):
        digits, span = _gen(r)
        assert _outcome(solve, digits, span) == _outcome(_reference, digits, span), \
            f"digits {digits!r}, span {span}"

    # canonical cases (exercism/python practice/largest-series-product)
    assert solve("29", 2) == 18, "span equals length"
    assert solve("1027839564", 3) == 270, "largest product of 3"
    assert solve("73167176531330624919225119674426574742355349194934", 6) == 23520, \
        "largest product of a big number"
    assert solve("99099", 3) == 0, "every span includes a zero"
    assert solve("0123456789", 5) == 15120, "largest product of 5, digits in order"
    # a span of 0 is the empty product; from .meta/example.py, not the test file
    assert solve("", 0) == 1, "empty string and a span of 0"

    with pytest.raises(ValueError, match=r"^span must not exceed string length$"):
        solve("123", 4)
    with pytest.raises(ValueError, match=r"^span must not exceed string length$"):
        solve("", 1)
    with pytest.raises(ValueError, match=r"^span must not be negative$"):
        solve("12345", -1)
    with pytest.raises(ValueError, match=r"^digits input must only contain digits$"):
        solve("1234a5", 2)
