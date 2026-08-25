"""Floor division and modulo — whole bills out, the booth keeps the remainder."""
# SOURCE: exercism/python concept/currency-exchange (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex  — the
#       operator table again, this time for `//` (floor division) and `%` (remainder)
#   https://docs.python.org/3/library/functions.html#int  — int() truncates towards zero, which
#       is NOT the same thing as rounding
#   CONCEPT: numbers — mixing int and float in one expression: `//` on a float still hands back
#       a float, so the type you get out depends on what you put in.

import pytest
from _lib import rng

META = {"topic": 207, "title": "numbers — whole bills, leftovers and the booth's cut",
        "minutes": 15, "prereqs": [200, 206], "tags": ["exercism", "numbers", "core"]}


def solve():
    """WHY: Chandler's exchange calculator now has to face the counter clerk. A
    booth pays out in notes, not in exact amounts: ask for 127.50 in 20s and you
    get six notes — 120 — and the booth quietly keeps the 7.50. On top of that
    the booth adds a "spread", a percentage on the exchange rate that is its
    fee. Chandler wants to see, before he hands over any cash, exactly how many
    notes come back, exactly how much the booth pockets, and the final figure
    once the spread is in. Everything below is floor division and remainders,
    which is the same arithmetic as pagination, batch sizes and disk blocks.

    YOU GET: nothing. Every number arrives as an argument to one of your
    functions.

    YOU RETURN: a dict with these three functions.

      "get_number_of_bills" — takes `amount` (what is being paid out, e.g.
      127.5) and `denomination` (the face value of one note, a whole number,
      e.g. 5). Returns how many whole notes fit inside that amount. Fractions of
      a note do not exist.

      "get_leftover_of_bills" — takes the same `amount` and `denomination`.
      Returns the part of the amount that cannot be paid out in whole notes —
      the booth's bonus.

      "exchangeable_value" — takes `budget` (his money, e.g. 127.25),
      `exchange_rate` (how much of his money one unit of theirs costs, e.g.
      1.20), `spread` (the booth's fee as a whole-number percentage of the rate,
      e.g. 10) and `denomination` (e.g. 20). Returns the largest amount of
      foreign currency he can actually walk away with, in whole notes.

    ─── exact rules ───
    The dict keys are exactly the three strings above. Amounts are never
    negative, `denomination` is a whole number of at least 1, and the rate plus
    its spread is never zero.

    The spread is a percentage OF THE RATE, added to it: rate 1.20 with a spread
    of 10 means 10% of 1.20 is 0.12, so the real rate Chandler pays is 1.32.

        get_number_of_bills(127.5, 5)          ->  25    (25 notes of 5 = 125)
        get_leftover_of_bills(127.5, 20)       ->  7.5   (6 notes of 20 = 120)
        exchangeable_value(127.25, 1.20, 10, 20)  ->  80
            (127.25 at the real rate of 1.32 is 96.4; in notes of 20 that is
             four notes, so 80 — the rest stays behind the counter)
        exchangeable_value(127.25, 1.20, 10, 5)   ->  95
            (same 96.4, but notes of 5 waste far less)
    """
    raise NotImplementedError


HINTS = [
    ("Two operators do the whole first half. One tells you how many times a size "
    "fits completely inside an amount; the other tells you what is left over when "
    "it no longer fits. In Python they are two characters each, and they are "
    "neighbours in the operator table. The third function does not need new "
    "arithmetic — it is the exchange sum you already know, then the first two."),
    ("Order for `exchangeable_value`: work out the real rate first (rate plus the "
    "spread's share of the rate), convert the budget at that rate, then reduce that "
    "figure to whole notes and turn the note count back into money. Notice the "
    "answer is a count times a face value, so it comes out as a whole number even "
    "though the budget and the rate were not. Watch the type: `//` on a float still "
    "gives a float, so if the spec asks for an int, one int() in the right place "
    "settles it."),
    ("Different data, same shape. Shipping 1000 items in boxes of 48:\n"
    "    full_boxes = 1000 // 48      # 20   whole boxes\n"
    "    left_on_pallet = 1000 % 48   # 40   items with no box\n"
    "    shipped = full_boxes * 48    # 960  what actually leaves the warehouse\n"
    "The booth is the warehouse: notes are boxes, the leftover never ships."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    amount = round(r.uniform(5, 20000), 2)
    denomination = r.choice([1, 2, 5, 10, 20, 50, 100, 500])
    budget = round(r.uniform(100, 100000), 2)
    rate = round(r.uniform(0.2, 200), 4)
    spread = r.choice([1, 5, 10, 15, 20, 25, 30])
    return amount, denomination, budget, rate, spread


def _reference():
    def get_number_of_bills(amount, denomination):
        return int(amount) // denomination

    def get_leftover_of_bills(amount, denomination):
        return amount % denomination

    def exchangeable_value(budget, exchange_rate, spread, denomination):
        actual_rate = exchange_rate + (exchange_rate / 100) * spread
        exchanged = budget / actual_rate
        return (int(exchanged) // denomination) * denomination

    return {"get_number_of_bills": get_number_of_bills,
            "get_leftover_of_bills": get_leftover_of_bills,
            "exchangeable_value": exchangeable_value}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(5):
        amount, denomination, budget, rate, spread = _gen(r)
        assert (got["get_number_of_bills"](amount, denomination)
                == want["get_number_of_bills"](amount, denomination))
        assert got["get_leftover_of_bills"](amount, denomination) == pytest.approx(
            want["get_leftover_of_bills"](amount, denomination))
        assert (got["exchangeable_value"](budget, rate, spread, denomination)
                == want["exchangeable_value"](budget, rate, spread, denomination))

    # canonical cases from exercism's exchange_test.py
    for amount, denomination, expected in [(163270, 50000, 3), (54361, 1000, 54),
                                           (127.5, 5, 25)]:
        assert got["get_number_of_bills"](amount, denomination) == expected
    for amount, denomination, expected in [(10.1, 10, 0.1), (654321.0, 5, 1.0),
                                           (3.14, 2, 1.14)]:
        assert got["get_leftover_of_bills"](amount, denomination) == pytest.approx(expected)
    for budget, rate, spread, denomination, expected in [
            (100000, 10.61, 10, 1, 8568),
            (1500, 0.84, 25, 40, 1400),
            (470000, 1050, 30, 10000000000, 0),
            (425.33, 0.0009, 30, 700, 363300)]:
        assert got["exchangeable_value"](budget, rate, spread, denomination) == expected
