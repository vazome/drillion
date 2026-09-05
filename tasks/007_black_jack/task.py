# given — do not edit
def value_of_card(card):
    """The scoring value of one card: 'J', 'Q', 'K' are 10, 'A' is 1, the rest their number."""
    if card in ("J", "Q", "K"):
        return 10
    if card == "A":
        return 1
    return int(card)


def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_CARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def _gen(r):
    if r.random() < 0.3:                       # blackjacks are rare by chance alone
        return r.choice(["A", "10", "J", "Q", "K"]), r.choice(["A", "10", "J", "Q", "K"])
    return r.choice(_CARDS), r.choice(_CARDS)


def _reference():
    def is_blackjack(card_one, card_two):
        hand = (card_one, card_two)
        return "A" in hand and 10 in (value_of_card(card_one), value_of_card(card_two))

    def can_split_pairs(card_one, card_two):
        return value_of_card(card_one) == value_of_card(card_two)

    def can_double_down(card_one, card_two):
        return 8 < value_of_card(card_one) + value_of_card(card_two) < 12

    return {"is_blackjack": is_blackjack, "can_split_pairs": can_split_pairs,
            "can_double_down": can_double_down}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        card_one, card_two = _gen(r)
        assert (got["is_blackjack"](card_one, card_two)
                == want["is_blackjack"](card_one, card_two))
        assert (got["can_split_pairs"](card_one, card_two)
                == want["can_split_pairs"](card_one, card_two))
        assert (got["can_double_down"](card_one, card_two)
                == want["can_double_down"](card_one, card_two))

    # canonical cases from exercism's black_jack_test.py
    for card_one, card_two, expected in [("A", "K", True), ("10", "A", True),
                                         ("A", "A", False), ("Q", "K", False),
                                         ("10", "9", False)]:
        assert got["is_blackjack"](card_one, card_two) == expected
    for card_one, card_two, expected in [("Q", "K", True), ("6", "6", True),
                                         ("A", "A", True), ("10", "A", False),
                                         ("10", "9", False)]:
        assert got["can_split_pairs"](card_one, card_two) == expected
    for card_one, card_two, expected in [("A", "9", True), ("K", "A", True),
                                         ("4", "5", True), ("A", "A", False),
                                         ("10", "2", False), ("10", "9", False)]:
        assert got["can_double_down"](card_one, card_two) == expected
