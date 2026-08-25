---
title: comparisons — blackjack card values
minutes: 15
prereqs: [200, 203, 209]
tags: [exercism, comparisons, core]
source: exercism/python concept/black-jack (MIT, adapted)
---
# comparisons — blackjack card values

*Comparison operators — scoring and ranking blackjack cards.*

## Why
You are building the scoring half of a blackjack table for a casino
app. Cards arrive from the dealer as short strings — '2', '10', 'K', 'A' —
and before any rule about the game can be written, something has to turn
those strings into numbers and compare them. The awkward one is the ace: it
is worth 1 or 11, and which one depends on what is already on the table. So
this drill is three steps in order — score one card, rank two cards, then
make the ace decision that needs both.

## You get
nothing. Cards arrive as arguments to your functions, always as
strings, always one of: '2' '3' '4' '5' '6' '7' '8' '9' '10' 'J' 'Q' 'K' 'A'
(jacks, queens, kings and the ace; jokers do not exist here).

## You return
a dict with these three functions.

  "value_of_card" — takes one `card` string. Returns its scoring value as a
  number: the face cards 'J', 'Q' and 'K' are 10, an 'A' is 1 for now, and
  every other card is worth the number printed on it.

  "higher_card" — takes `card_one` and `card_two`. Returns the card with the
  higher scoring value, as the original string. When the two cards score the
  same, return BOTH, as a tuple in the order they were given. Aces still
  count as 1 here.

  "value_of_ace" — takes `card_one` and `card_two`, the two cards already in
  hand before an ace is dealt. Returns 1 or 11: whichever keeps the hand as
  high as possible without going over 21. An ace already sitting in the hand
  counts as 11, which is what forces the incoming one down to 1.

## Rules
The dict keys are exactly the three strings above.

```python
value_of_card('K')      ->  10
value_of_card('4')      ->  4
higher_card('4', '6')   ->  '6'
higher_card('K', '10')  ->  ('K', '10')   equal value, so both, in order
value_of_ace('7', '3')  ->  11   (7 + 3 + 11 = 21, dead on)
value_of_ace('6', 'K')  ->  1    (6 + 10 + 11 = 27, bust)
```

## Read first
- https://docs.python.org/3/reference/expressions.html#value-comparisons  — < > == and what "compare by value" means once the two sides are not the same type
- https://docs.python.org/3/library/stdtypes.html#comparisons  — the full operator table, including `in` (containment) and `is` (identity), which are NOT the same test
- CONCEPT: comparisons — a comparison operator looks at the values of two operands and hands back True or False; they all share one precedence level, above and / or / not.

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Only three cards are special: the three letter cards worth 10, and the ace. Everything else is the string of a number, and Python will turn that into a number for you in one call. Write that first function properly and the other two stop being about cards at all — they are about the numbers it gives back.
### Hint 2
`higher_card` has three outcomes, not two: bigger, smaller, and equal. Handle equal first and the rest is one comparison. Returning two things separated by a comma builds a tuple, which is exactly the shape the equal case wants. For `value_of_ace`, ask the one question that matters: would the hand plus 11 go over 21? Careful — inside THIS function an ace already in hand is worth 11, not the 1 your first function reports.
### Hint 3
Different data, same shape. Shirt sizes ranked by a lookup, then compared:

```python
def size_value(size):
    if size in ('S', 'M', 'L'):
        return {'S': 1, 'M': 2, 'L': 3}[size]
    return int(size)          # '42' -> 42, a numeric size
def bigger(one, two):
    if size_value(one) == size_value(two):
        return one, two
    return one if size_value(one) > size_value(two) else two
```

Note `bigger` never mentions 'S' or 'M': it only talks to `size_value`.
