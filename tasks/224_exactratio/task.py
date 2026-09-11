from fractions import Fraction


def solve(amounts: list[tuple[int, int]], scale: tuple[int, int]) -> tuple[list[Fraction], Fraction]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    # denominators with no exact binary form, so a float answer drifts on every one of them
    amounts = [(r.randint(1, 5), r.choice([3, 6, 7, 9, 12, 16]))
               for _ in range(r.randint(2, 6))]
    return amounts, r.choice([(5, 4), (2, 3), (3, 2), (1, 3), (7, 4), (1, 1)])


def _reference(amounts, scale):
    factor = Fraction(*scale)
    scaled = [Fraction(*pair) * factor for pair in amounts]
    return scaled, sum(scaled, Fraction(0))


def test_solve():
    thirds, total = solve([(1, 3), (1, 3), (1, 3)], (1, 1))
    assert total == 1, f"three exact thirds are one whole cup, got {total}"
    assert thirds == [Fraction(1, 3)] * 3, f"each third comes back unchanged, got {thirds}"
    assert solve([(1, 2), (2, 3)], (5, 4)) == (
        [Fraction(5, 8), Fraction(5, 6)],
        Fraction(35, 24),
    ), "half and two thirds, both at five quarters"
    assert solve([], (5, 4)) == ([], Fraction(0)), "an empty recipe totals to a Fraction, not to 0"

    r = rng()
    for _ in range(8):
        amounts, scale = _gen(r)
        mine_scaled, mine_total = solve(list(amounts), scale)
        want_scaled, want_total = _reference(amounts, scale)
        for pair, got, want in zip(amounts, mine_scaled, want_scaled):
            assert isinstance(got, Fraction), f"{pair} came back as {type(got).__name__}"
            # a float that passed through Fraction() keeps its drift as a vast denominator
            assert got.denominator <= 10_000, f"{pair} at {scale} went through a float: {got}"
            assert got == want, f"{pair} at {scale} is {want}, got {got}"
        assert mine_total == want_total, f"total of {amounts} at {scale}"
