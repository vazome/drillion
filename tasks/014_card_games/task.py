def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    size = r.choice([3, 5, 7])
    hand = [r.randrange(1, 12) for _ in range(size)]
    if r.random() < 0.4:                       # an even ladder makes the averages agree
        rise = r.randrange(1, 5)
        hand = [hand[0] + rise * step for step in range(size)]
    if r.random() < 0.4:                       # a Jack on the end, for maybe_double_last
        hand[-1] = 11
    return hand


def _reference():
    def card_average(hand):
        return sum(hand) / len(hand)

    def approx_average_is_average(hand):
        real_average = card_average(hand)
        return (card_average([hand[0], hand[-1]]) == real_average
                or hand[len(hand) // 2] == real_average)

    def average_even_is_average_odd(hand):
        return card_average(hand[::2]) == card_average(hand[1::2])

    def maybe_double_last(hand):
        if hand[-1] == 11:
            hand[-1] *= 2
        return hand

    return {"card_average": card_average,
            "approx_average_is_average": approx_average_is_average,
            "average_even_is_average_odd": average_even_is_average_odd,
            "maybe_double_last": maybe_double_last}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        hand = _gen(r)
        assert (got["card_average"](list(hand))
                == want["card_average"](list(hand))), f"card_average({hand})"
        assert (got["approx_average_is_average"](list(hand))
                == want["approx_average_is_average"](list(hand))), \
            f"approx_average_is_average({hand})"
        assert (got["average_even_is_average_odd"](list(hand))
                == want["average_even_is_average_odd"](list(hand))), \
            f"average_even_is_average_odd({hand})"
        assert (got["maybe_double_last"](list(hand))
                == want["maybe_double_last"](list(hand))), f"maybe_double_last({hand})"

    # canonical cases from exercism's lists_test.py
    for hand, expected in [([1], 1.0), ([5, 6, 7], 6.0), ([1, 2, 3, 4], 2.5),
                           ([1, 10, 100], 37.0)]:
        assert got["card_average"](list(hand)) == expected, f"card_average({hand})"
    for hand in [[1, 2, 3], [2, 3, 4], [2, 3, 4, 8, 8], [1, 2, 4, 5, 8]]:
        assert got["approx_average_is_average"](list(hand)) is True, f"approx({hand})"
    for hand in [[0, 1, 5], [3, 6, 9, 12, 150], [1, 2, 3, 5, 9], [2, 3, 4, 7, 8]]:
        assert got["approx_average_is_average"](list(hand)) is False, f"approx({hand})"
    for hand in [[1, 2, 3], [5, 6, 7], [1, 3, 5, 7, 9]]:
        assert got["average_even_is_average_odd"](list(hand)) is True, f"even/odd({hand})"
    for hand in [[5, 6, 8], [1, 2, 3, 4]]:
        assert got["average_even_is_average_odd"](list(hand)) is False, f"even/odd({hand})"
    for hand, expected in [([1, 2, 11], [1, 2, 22]), ([5, 9, 11], [5, 9, 22]),
                           ([5, 9, 10], [5, 9, 10]), ([1, 2, 3], [1, 2, 3]),
                           ([1, 11, 8], [1, 11, 8])]:
        assert got["maybe_double_last"](list(hand)) == expected, f"maybe_double_last({hand})"
