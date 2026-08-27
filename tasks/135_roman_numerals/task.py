def solve(number: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_NUMERALS = ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
             (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"))

_INTERESTING = [1, 4, 9, 14, 40, 44, 49, 90, 99, 400, 444, 490, 900, 999, 1000, 3999]


def _gen(r):
    if r.random() < 0.3:
        return r.choice(_INTERESTING)
    return r.randint(1, 3999)


def _reference(number):
    pieces = []
    for value, numeral in _NUMERALS:
        while number >= value:
            pieces.append(numeral)
            number -= value
    return "".join(pieces)


def test_solve():
    r = rng()
    for _ in range(6):
        number = _gen(r)
        assert solve(number) == _reference(number), f"number {number}"

    # canonical cases (exercism/python practice/roman-numerals)
    assert solve(1) == "I"
    assert solve(4) == "IV"
    assert solve(48) == "XLVIII"
    assert solve(163) == "CLXIII"
    assert solve(1666) == "MDCLXVI"
    assert solve(3999) == "MMMCMXCIX"
