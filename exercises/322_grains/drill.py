def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    return r.randint(1, 64)


def _reference():
    def square(number):
        if number < 1 or number > 64:
            raise ValueError("square must be between 1 and 64")
        return 2 ** (number - 1)

    def total():
        return 2 ** 64 - 1

    return {"square": square, "total": total}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        number = _gen(r)
        assert got["square"](number) == want["square"](number), f"square {number}"
    assert got["total"]() == want["total"]()

    # canonical cases (exercism/python practice/grains)
    for number, expected in [(1, 1), (2, 2), (3, 4), (4, 8), (16, 32768),
                             (32, 2147483648), (64, 9223372036854775808)]:
        assert got["square"](number) == expected
    assert got["total"]() == 18446744073709551615

    for bad in [0, -1, 65, r.randint(65, 500), -r.randint(1, 500)]:
        with pytest.raises(ValueError, match=r"^square must be between 1 and 64$"):
            got["square"](bad)
