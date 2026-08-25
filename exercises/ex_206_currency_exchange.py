"""Arithmetic operators — the three sums a currency desk does before anything else."""
# SOURCE: exercism/python concept/currency-exchange (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex  — the
#       arithmetic operators table: + - * / // % and what each returns
#   https://docs.python.org/3/tutorial/introduction.html#numbers  — the five-minute tour: `/`
#       always hands back a float, even when the division comes out even
#   CONCEPT: numbers — int and float, and the fact that Python quietly widens the narrower
#       type when you mix them in one expression.

import pytest
from _lib import rng

META = {"topic": 206, "title": "numbers — the currency exchange desk", "minutes": 12,
        "prereqs": [200], "tags": ["exercism", "numbers", "core"]}


def solve():
    """WHY: Your friend Chandler is going travelling and is convinced every
    exchange booth is out to cheat him. He wants a pocket calculator that shows
    him, before he hands over any cash, exactly what he should get back. This
    first version does the three plainest sums a booth does: how much foreign
    currency his money buys, how much of his own money he still has afterwards,
    and what a stack of bills is worth. Get these right and the fee arithmetic
    in the next drill is just these three, chained.

    YOU GET: nothing. Every number arrives as an argument to one of your
    functions.

    YOU RETURN: a dict with these three functions.

      "exchange_money" — takes `budget` (how much of his own money he is
      changing, e.g. 127.5) and `exchange_rate` (how much of his own money one
      unit of the foreign currency costs, e.g. 1.2 means 1.20 USD buys 1 EUR).
      Returns how much foreign currency he gets.

      "get_change" — takes `budget` (what he had, e.g. 127.5) and
      `exchanging_value` (what he handed over the counter, e.g. 120). Returns
      what is left in his own currency.

      "get_value_of_bills" — takes `denomination` (the face value of one bill,
      always a whole number, e.g. 5) and `number_of_bills` (e.g. 128). Returns
      what that stack of bills is worth.

    ─── exact rules ───
    The dict keys are exactly the three strings above. `exchange_rate` is never
    zero. Answers may come out as floats; nothing is rounded.

        exchange_money(127.5, 1.2)     ->  106.25   (127.50 of his money buys 106.25)
        get_change(127.5, 120)         ->  7.5      (he keeps the rest)
        get_value_of_bills(5, 128)     ->  640      (128 bills of 5)
    """
    raise NotImplementedError


HINTS = [
    ("One operator each, and the hard part is picking which. The rate is quoted as "
    "'how much of MY money buys one of THEIRS', so going from his money to theirs "
    "is the operation that undoes multiplying by the rate. The other two are the "
    "obvious ones: what is left after handing some over, and what N things of the "
    "same size add up to."),
    ("Sanity-check each formula on a rate you can do in your head. At a rate of 2, "
    "100 of his money must come back as 50 of theirs — so if your expression gives "
    "200, you have the division the wrong way round. Then build the dict mapping "
    "each key string to the function object (no parentheses)."),
    ("Different data, same shape. Petrol at 1.75 per litre, a 60-litre tank, a "
    "50-euro note:\n"
    "    litres = 50 / 1.75        # 28.57...  money -> litres, so divide by price\n"
    "    left_over = 60 - 28.57    # litres of tank still empty\n"
    "    tank_cost = 1.75 * 60     # 105.0     price per unit x number of units\n"
    "Same three shapes, in the same order, on numbers you can check by eye."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    budget = round(r.uniform(50, 500000), 2)
    rate = round(r.uniform(0.05, 15), 4)
    exchanging_value = round(r.uniform(0, budget), 2)
    denomination = r.choice([1, 5, 10, 20, 50, 100, 500, 1000])
    number_of_bills = r.randint(1, 900)
    return budget, rate, exchanging_value, denomination, number_of_bills


def _reference():
    def exchange_money(budget, exchange_rate):
        return budget / exchange_rate

    def get_change(budget, exchanging_value):
        return budget - exchanging_value

    def get_value_of_bills(denomination, number_of_bills):
        return denomination * number_of_bills

    return {"exchange_money": exchange_money, "get_change": get_change,
            "get_value_of_bills": get_value_of_bills}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(5):
        budget, rate, exchanging_value, denomination, bills = _gen(r)
        assert got["exchange_money"](budget, rate) == pytest.approx(
            want["exchange_money"](budget, rate))
        assert got["get_change"](budget, exchanging_value) == pytest.approx(
            want["get_change"](budget, exchanging_value))
        assert got["get_value_of_bills"](denomination, bills) == pytest.approx(
            want["get_value_of_bills"](denomination, bills))

    # canonical cases from exercism's exchange_test.py
    for budget, rate, expected in [(100000, 0.8, 125000), (700000, 10.0, 70000)]:
        assert got["exchange_money"](budget, rate) == pytest.approx(expected)
    for budget, handed_over, expected in [(463000, 5000, 458000), (1250, 120, 1130),
                                          (15000, 1380, 13620)]:
        assert got["get_change"](budget, handed_over) == pytest.approx(expected)
    for denomination, bills, expected in [(10000, 128, 1280000), (50, 360, 18000),
                                          (200, 200, 40000)]:
        assert got["get_value_of_bills"](denomination, bills) == expected
