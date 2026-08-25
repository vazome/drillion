"""Chained comparisons and `in` — the three decisions a blackjack player makes."""
# SOURCE: exercism/python concept/black-jack (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/reference/expressions.html#comparisons  — comparisons CHAIN:
#       `8 < total < 12` is one expression, and the middle is evaluated once
#   https://docs.python.org/3/reference/expressions.html#membership-test-operations  — `in`
#       asks "is this a member of that", which reads better than a pile of == joined by or
#   CONCEPT: comparisons — every comparison hands back True or False, so a function whose whole
#       body is one comparison can simply return it; no if statement is needed.

from _lib import rng

META = {"topic": 213, "title": "comparisons — blackjack hand decisions", "minutes": 15,
        "prereqs": [200, 203, 209, 212], "tags": ["exercism", "comparisons", "core"]}


# given — do not edit
def value_of_card(card):
    """The scoring value of one card: 'J', 'Q', 'K' are 10, 'A' is 1, the rest their number."""
    if card in ("J", "Q", "K"):
        return 10
    if card == "A":
        return 1
    return int(card)


def solve():
    """WHY: The scoring half of the casino's blackjack table is done — card
    values and rankings work. Now the table has to answer the three questions a
    player asks the moment their first two cards land: is this an instant win,
    may I split these into two hands, and may I double my bet? Each is a rule
    from the casino's rulebook, each is one line of comparisons, and each is
    the kind of rule that gets written wrong by summing when it should be
    checking membership.

    YOU GET: `value_of_card` is already written for you above — use it, do not
    rewrite it. Cards arrive as strings, always one of: '2' '3' '4' '5' '6' '7'
    '8' '9' '10' 'J' 'Q' 'K' 'A'.

    YOU RETURN: a dict with these three functions, all returning True or False.

      "is_blackjack" — takes `card_one`, `card_two`, the two cards dealt first.
      A "blackjack" (or "natural") is an ace together with any ten-card: '10',
      'J', 'Q' or 'K'. The casino wants this checked by looking for an ace AND a
      ten-card in the hand, not by adding the hand up to 21.

      "can_split_pairs" — takes `card_one`, `card_two`. A player may split the
      hand into two separate hands when the two cards have the same scoring
      value. Two sixes qualify; so do a queen and a king, because both score 10.

      "can_double_down" — takes `card_one`, `card_two`. A player may double
      their bet when the two cards total 9, 10 or 11 points, counting an ace as
      1.

    ─── exact rules ───
    The dict keys are exactly the three strings above.

        is_blackjack('A', 'K')      ->  True   (ace plus a ten-card)
        is_blackjack('A', 'A')      ->  False  (an ace is not a ten-card)
        can_split_pairs('Q', 'K')   ->  True   (both score 10)
        can_split_pairs('10', 'A')  ->  False  (10 against 1)
        can_double_down('A', '9')   ->  True   (1 + 9 = 10, inside 9..11)
        can_double_down('10', '2')  ->  False  (12 is one too many)
    """
    raise NotImplementedError


HINTS = [
    ("Each of the three is a single expression that is already True or False — you "
    "can return the comparison itself, no `if` and no `return True` / `return "
    "False`. For the first one, resist adding the two cards up: the rule is about "
    "WHICH two cards are present, and one of them is not identified by its score."),
    ("Blackjack: one of the two cards must be the ace and one of them must score 10 "
    "— two separate membership questions joined with `and`. Watch the ace-with-ace "
    "case: it has an ace, but no ten-card, so it must come out False. Doubling "
    "down: 9, 10 or 11 is one range, and Python lets you write a range as a single "
    "chained comparison with the total in the middle."),
    ("Different data, same shape. A delivery may go by bike when it has a small "
    "parcel and a city address, and it is 'oversize' when the two side lengths add "
    "up to somewhere between 100 and 150 cm:\n"
    "    def by_bike(a, b):\n"
    "        return 'small' in (a, b) and 'city' in (a, b)\n"
    "    def oversize(a, b):\n"
    "        return 99 < side(a) + side(b) < 151\n"
    "First one asks about membership twice; the second one chains a range around a "
    "sum. `'small' in (a, b)` is short for `a == 'small' or b == 'small'`."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
