---
title: comparisons — blackjack card values
difficulty: medium
tier: core
minutes: 15
prereqs: [5]
tags: [comparisons]
source: exercism/python concept/black-jack (MIT, adapted)
---
# comparisons — blackjack card values

*Comparison operators — scoring and ranking blackjack cards.*

## Read first
- [Value comparisons](https://devdocs.io/python~3.14/reference/expressions#value-comparisons) — `<` `>` `==` and what "compare by value" means once the two sides are not the same type
- [Comparisons in Python](https://devdocs.io/python~3.14/library/stdtypes#comparisons) — the full operator table, including `in` (containment) and `is` (identity), which are NOT the same test
- [Comparisons in Python (language reference)](https://devdocs.io/python~3.14/reference/expressions#comparisons) — they all share one precedence level, above `and` / `or` / `not`
- [Identity comparisons](https://devdocs.io/python~3.14/reference/expressions#is-not) — `is` / `is not`, and why they belong to `None`, not to cards
- [Numeric types](https://devdocs.io/python~3.14/library/stdtypes#typesnumeric) — the ints your card values become
- [Sequence types](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — the tuple the tie case returns
- [Python basic operators (Tutorials Point)](https://www.tutorialspoint.com/python/python_basic_operators.htm) — a worked list with output
- [Python Object Model](https://devdocs.io/python~3.14/reference/datamodel#objects) — what identity actually is

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
You are building the scoring half of a blackjack table for a casino app. Cards arrive from the dealer as short strings — '2', '10', 'K', 'A' — and before any rule about the game can be written, something has to turn those strings into numbers and compare them. The awkward one is the ace: it is worth 1 or 11, and which one depends on what is already on the table. So this task is three steps in order — score one card, rank two cards, then make the ace decision that needs both.

## You get
Nothing. Cards arrive as arguments to your functions, always as strings, always one of: `'2' '3' '4' '5' '6' '7' '8' '9' '10' 'J' 'Q' 'K' 'A'` (jacks, queens, kings and the ace; jokers do not exist here).

> [!NOTE]
> Exercism asks for all six functions in one `black_jack.py`. Here the task is split in two: **this task covers tasks 1–3**, and tasks 4–6 are task `007_black_jack`. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"value_of_card"` | one `card` string | its scoring value as a number: the face cards `'J'`, `'Q'` and `'K'` are 10, an `'A'` is 1 for now, and every other card is worth the number printed on it |
| `"higher_card"` | `card_one`, `card_two` | the card with the higher scoring value, as the original string. When the two cards score the same, BOTH, as a tuple in the order they were given. Aces still count as 1 here |
| `"value_of_ace"` | `card_one`, `card_two` — the two cards already in hand before an ace is dealt | 1 or 11: whichever keeps the hand as high as possible without going over 21. An ace already sitting in the hand counts as 11, which is what forces the incoming one down to 1 |

```python
table = solve()
table["value_of_card"]('K')      # -> 10
table["value_of_card"]('4')      # -> 4
table["higher_card"]('4', '6')   # -> '6'
table["higher_card"]('K', '10')  # -> ('K', '10')   equal value, so both, in order
table["value_of_ace"]('7', '3')  # -> 11   (7 + 3 + 11 = 21, dead on)
table["value_of_ace"]('6', 'K')  # -> 1    (6 + 10 + 11 = 27, bust)
```

## Rules
- this task implements **Exercism tasks 1, 2 and 3 only** — `is_blackjack`, `can_split_pairs` and `can_double_down` belong to task `007_black_jack`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- `higher_card` returns the *card string*, not its value; on a tie it returns a tuple `(card_one, card_two)` in the argument order, which the tests compare with `==`
- `value_of_ace` returns the number 1 or 11, not a card

## Hints
### Hint 1
Only three cards are special: the three letter cards worth 10, and the ace. Everything else is the string of a number, and the [`int` constructor](https://devdocs.io/python~3.14/library/functions#int) will turn that into a number for you in one call — `int('13')`. You can use the equality operator to spot the ace (`card == 'A'`) and the containment operator to spot a face card (`'Q' in 'KJQ'`). Write that first function properly and the other two stop being about cards at all — they are about the numbers it gives back.
### Hint 2
Once you have defined `value_of_card`, you can call it from the other two functions.

`higher_card` has three outcomes, not two: bigger, smaller, and equal. Use `==` for the equal case and handle it first; then one `>` decides the rest. Returning two things separated by a comma builds a tuple, which is exactly the shape the equal case wants.

For `value_of_ace`, one order comparison (`>`) decides everything: would the hand plus 11 go over 21? Careful — inside THIS function an ace already in hand is worth 11, not the 1 your first function reports; if we already have an ace in hand, then the value for the upcoming ace would be 1.
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
