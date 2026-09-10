from decimal import ROUND_HALF_UP, Decimal


def solve(prices: list[str], rate: str) -> tuple[list[Decimal], Decimal]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_CENT = Decimal("0.01")


def _gen(r):
    # dollars a multiple of 4 and cents from this set puts every charge exactly on half a
    # cent, where ROUND_HALF_UP and the ROUND_HALF_EVEN default disagree
    prices = [f"{r.randrange(4, 41, 4)}.{r.choice(['04', '20', '36', '52', '68', '84'])}"
              for _ in range(r.randint(2, 6))]
    prices += [f"{r.randint(1, 60)}.{r.randrange(0, 100):02d}" for _ in range(r.randint(1, 4))]
    r.shuffle(prices)
    return prices, "0.125"


def _reference(prices, rate):
    charge_rate = Decimal(rate)
    lines = [Decimal(p) + (Decimal(p) * charge_rate).quantize(_CENT, rounding=ROUND_HALF_UP)
             for p in prices]
    return lines, sum(lines, Decimal("0.00"))


def test_solve():
    lines, total = solve(["4.20", "12.04"], "0.125")
    assert lines == [Decimal("4.73"), Decimal("13.55")], (
        f"half a cent rounds up: 0.52500 -> 0.53 and 1.50500 -> 1.51, got {lines}"
    )
    assert total == Decimal("18.28"), f"the footer is the sum of the rows, got {total}"
    assert solve([], "0.125") == ([], Decimal("0.00")), "an empty bill totals to money, not to 0"

    r = rng()
    for _ in range(8):
        prices, rate = _gen(r)
        mine_lines, mine_total = solve(list(prices), rate)
        want_lines, want_total = _reference(prices, rate)
        assert all(isinstance(line, Decimal) for line in mine_lines), "every line is a Decimal"
        for price, got, want in zip(prices, mine_lines, want_lines):
            assert got == want, f"{price} at {rate} is {want}, got {got}"
        assert mine_total == want_total, f"total of {prices} at {rate}"
