def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

import pytest
from _lib import rng

_PUNCTUATION = "()+-. "


def _digits(r, count):
    return "".join(str(r.randrange(10)) for _ in range(count))


def _format(r, digits):
    chars = list(digits)
    for _ in range(r.randint(0, 4)):
        chars.insert(r.randrange(len(chars) + 1), r.choice(" ..--()"))
    number = "".join(chars)
    if r.random() < 0.25:
        number = "+" + number
    return number


def _gen(r):
    area = r.choice("23456789") + _digits(r, 2)
    exchange = r.choice("23456789") + _digits(r, 2)
    roll = r.random()
    if roll < 0.10:
        area = r.choice("01") + _digits(r, 2)
    elif roll < 0.20:
        exchange = r.choice("01") + _digits(r, 2)
    digits = area + exchange + _digits(r, 4)

    shape = r.random()
    if shape < 0.10:
        digits = digits[:r.randint(3, 9)]
    elif shape < 0.20:
        digits = r.choice("023456789") + digits
    elif shape < 0.35:
        digits = "1" + digits
    elif shape < 0.42:
        digits = _digits(r, r.randint(1, 3)) + digits

    number = _format(r, digits)
    junk = r.random()
    if junk < 0.10:
        spot = r.randrange(len(number))
        number = number[:spot] + r.choice("abcXYZ") + number[spot + 1:]
    elif junk < 0.18:
        spot = r.randrange(len(number))
        number = number[:spot] + r.choice("@:!*&") + number[spot + 1:]
    return number


def _reference():
    class PhoneNumber:
        def __init__(self, number):
            digits = "".join(char for char in number
                             if char not in _PUNCTUATION and not char.isspace())
            if any(char.isalpha() for char in digits):
                raise ValueError("letters not permitted")
            if digits and not digits.isdigit():
                raise ValueError("punctuations not permitted")
            if len(digits) < 10:
                raise ValueError("must not be fewer than 10 digits")
            if len(digits) > 11:
                raise ValueError("must not be greater than 11 digits")
            if len(digits) == 11:
                if digits[0] != "1":
                    raise ValueError("11 digits must start with 1")
                digits = digits[1:]
            if digits[0] == "0":
                raise ValueError("area code cannot start with zero")
            if digits[0] == "1":
                raise ValueError("area code cannot start with one")
            if digits[3] == "0":
                raise ValueError("exchange code cannot start with zero")
            if digits[3] == "1":
                raise ValueError("exchange code cannot start with one")
            self.number = digits
            self.area_code = digits[:3]
            self.exchange_code = digits[3:6]
            self.subscriber_number = digits[6:]

        def pretty(self):
            return f"({self.area_code})-{self.exchange_code}-{self.subscriber_number}"

    return PhoneNumber


def _outcome(phone_class, number):
    try:
        phone = phone_class(number)
    except ValueError as err:
        return ("error", str(err))
    return ("ok", phone.number, phone.area_code, phone.pretty())


def test_solve():
    r = rng()
    PhoneNumber = solve()
    assert inspect.isclass(PhoneNumber), "solve() must return a class"
    Reference = _reference()
    for _ in range(6):
        number = _gen(r)
        assert _outcome(PhoneNumber, number) == _outcome(Reference, number), f"number {number!r}"

    # canonical cases (exercism/python practice/phone-number)
    assert PhoneNumber("(223) 456-7890").number == "2234567890"
    assert PhoneNumber("223.456.7890").number == "2234567890"
    assert PhoneNumber("223 456   7890   ").number == "2234567890"
    assert PhoneNumber("+1 (223) 456-7890").number == "2234567890"
    assert PhoneNumber("2234567890").area_code == "223"
    assert PhoneNumber("12234567890").pretty() == "(223)-456-7890"

    for bad, message in [("123456789", "must not be fewer than 10 digits"),
                         ("22234567890", "11 digits must start with 1"),
                         ("321234567890", "must not be greater than 11 digits"),
                         ("523-abc-7890", "letters not permitted"),
                         ("523-@:!-7890", "punctuations not permitted"),
                         ("(023) 456-7890", "area code cannot start with zero"),
                         ("(123) 456-7890", "area code cannot start with one"),
                         ("1 (223) 056-7890", "exchange code cannot start with zero"),
                         ("1 (223) 156-7890", "exchange code cannot start with one")]:
        with pytest.raises(ValueError, match=rf"^{message}$"):
            PhoneNumber(bad)
