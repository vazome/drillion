---
title: comparisons — blackjack hand decisions
minutes: 15
prereqs: [200, 203, 209, 212]
tags: [exercism, comparisons, core]
source: exercism/python concept/black-jack (MIT, adapted)
---
# comparisons — blackjack hand decisions

*Chained comparisons and `in` — the three decisions a blackjack player makes.*

## Why
The scoring half of the casino's blackjack table is done — card
values and rankings work. Now the table has to answer the three questions a
player asks the moment their first two cards land: is this an instant win,
may I split these into two hands, and may I double my bet? Each is a rule
from the casino's rulebook, each is one line of comparisons, and each is
the kind of rule that gets written wrong by summing when it should be
checking membership.

## You get
`value_of_card` is already written for you above — use it, do not
rewrite it. Cards arrive as strings, always one of: '2' '3' '4' '5' '6' '7'
'8' '9' '10' 'J' 'Q' 'K' 'A'.

## You return
a dict with these three functions, all returning True or False.

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

## Rules
The dict keys are exactly the three strings above.

```python
is_blackjack('A', 'K')      ->  True   (ace plus a ten-card)
is_blackjack('A', 'A')      ->  False  (an ace is not a ten-card)
can_split_pairs('Q', 'K')   ->  True   (both score 10)
can_split_pairs('10', 'A')  ->  False  (10 against 1)
can_double_down('A', '9')   ->  True   (1 + 9 = 10, inside 9..11)
can_double_down('10', '2')  ->  False  (12 is one too many)
```

## Read first
- https://docs.python.org/3/reference/expressions.html#comparisons  — comparisons CHAIN: `8 < total < 12` is one expression, and the middle is evaluated once
- https://docs.python.org/3/reference/expressions.html#membership-test-operations  — `in` asks "is this a member of that", which reads better than a pile of == joined by or
- CONCEPT: comparisons — every comparison hands back True or False, so a function whose whole body is one comparison can simply return it; no if statement is needed.

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Each of the three is a single expression that is already True or False — you can return the comparison itself, no `if` and no `return True` / `return False`. For the first one, resist adding the two cards up: the rule is about WHICH two cards are present, and one of them is not identified by its score.
### Hint 2
Blackjack: one of the two cards must be the ace and one of them must score 10 — two separate membership questions joined with `and`. Watch the ace-with-ace case: it has an ace, but no ten-card, so it must come out False. Doubling down: 9, 10 or 11 is one range, and Python lets you write a range as a single chained comparison with the total in the middle.
### Hint 3
Different data, same shape. A delivery may go by bike when it has a small parcel and a city address, and it is 'oversize' when the two side lengths add up to somewhere between 100 and 150 cm:

```python
def by_bike(a, b):
    return 'small' in (a, b) and 'city' in (a, b)
def oversize(a, b):
    return 99 < side(a) + side(b) < 151
```

First one asks about membership twice; the second one chains a range around a sum. `'small' in (a, b)` is short for `a == 'small' or b == 'small'`.
