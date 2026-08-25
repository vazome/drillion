def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_CARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def _gen(r):
    return r.choice(_CARDS), r.choice(_CARDS)


def _reference():
    def value_of_card(card):
        if card in ("J", "Q", "K"):
            return 10
        if card == "A":
            return 1
        return int(card)

    def higher_card(card_one, card_two):
        one, two = value_of_card(card_one), value_of_card(card_two)
        if one == two:
            return card_one, card_two
        return card_one if one > two else card_two

    def value_of_ace(card_one, card_two):
        in_hand = sum(11 if card == "A" else value_of_card(card)
                      for card in (card_one, card_two))
        return 1 if in_hand + 11 > 21 else 11

    return {"value_of_card": value_of_card, "higher_card": higher_card,
            "value_of_ace": value_of_ace}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        card_one, card_two = _gen(r)
        assert got["value_of_card"](card_one) == want["value_of_card"](card_one)
        assert (got["higher_card"](card_one, card_two)
                == want["higher_card"](card_one, card_two))
        assert (got["value_of_ace"](card_one, card_two)
                == want["value_of_ace"](card_one, card_two))

    # canonical cases from exercism's black_jack_test.py
    for card, expected in [("2", 2), ("8", 8), ("A", 1), ("10", 10), ("Q", 10)]:
        assert got["value_of_card"](card) == expected
    for card_one, card_two, expected in [("A", "A", ("A", "A")), ("10", "J", ("10", "J")),
                                         ("3", "A", "3"), ("6", "9", "9"),
                                         ("9", "10", "10")]:
        assert got["higher_card"](card_one, card_two) == expected
    for card_one, card_two, expected in [("2", "3", 11), ("5", "5", 11), ("Q", "A", 1),
                                         ("7", "8", 1), ("A", "2", 1)]:
        assert got["value_of_ace"](card_one, card_two) == expected
