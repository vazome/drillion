def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


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

    # canonical cases from exercism's exchange_test.py + instructions.md
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
