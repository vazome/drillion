def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng


def _checksum(digits):
    total = 0
    for index, char in enumerate(reversed(digits)):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total


def _gen(r):
    length = r.choice([1, 2, 3, 3, 8, 9, 10, 12, 16, 16, 20])
    digits = "".join(str(r.randrange(10)) for _ in range(length))
    if r.random() < 0.45 and length > 1:
        body = digits[:-1]
        digits = next(body + last for last in "0123456789"
                      if _checksum(body + last) % 10 == 0)
    if r.random() < 0.2:
        spot = r.randrange(len(digits))
        digits = digits[:spot] + r.choice("ab:#%-$") + digits[spot + 1:]
    chars = list(digits)
    for _ in range(r.randint(0, 4)):
        chars.insert(r.randrange(len(chars) + 1), " ")
    return "".join(chars)


def _reference():
    class Luhn:
        def __init__(self, card_num):
            self.card_num = card_num

        def valid(self):
            digits = self.card_num.replace(" ", "")
            if len(digits) <= 1 or not digits.isdigit():
                return False
            return _checksum(digits) % 10 == 0

    return Luhn


def test_solve():
    r = rng()
    Luhn = solve()
    assert inspect.isclass(Luhn), "solve() must return a class"
    Reference = _reference()
    for _ in range(6):
        card_num = _gen(r)
        assert Luhn(card_num).valid() is Reference(card_num).valid(), f"card_num {card_num!r}"

    # canonical cases (exercism/python practice/luhn)
    assert Luhn("1").valid() is False
    assert Luhn("059").valid() is True
    assert Luhn("055 444 285").valid() is True
    assert Luhn("055 444 286").valid() is False
    assert Luhn("8273 1232 7352 0569").valid() is False
    assert Luhn("055-444-285").valid() is False
    assert Luhn("0000 0").valid() is True
    assert Luhn(" 0").valid() is False

    # valid() may be called more than once on the same object
    number = Luhn("055 444 285")
    assert number.valid() is True
    assert number.valid() is True
