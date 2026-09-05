def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


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
    for budget, rate, expected in [(100000, 0.8, 125000), (700000, 10.0, 70000),
                                  (127.5, 1.2, 106.25)]:
        assert got["exchange_money"](budget, rate) == pytest.approx(expected)
    for budget, handed_over, expected in [(463000, 5000, 458000), (1250, 120, 1130),
                                          (15000, 1380, 13620)]:
        assert got["get_change"](budget, handed_over) == pytest.approx(expected)
    for denomination, bills, expected in [(10000, 128, 1280000), (50, 360, 18000),
                                          (200, 200, 40000)]:
        assert got["get_value_of_bills"](denomination, bills) == expected
