---
title: comparisons — blackjack hand decisions
difficulty: easy
tier: core
minutes: 15
prereqs: [6]
tags: [comparisons]
source: exercism/python concept/black-jack (MIT, adapted)
---
# comparisons — blackjack hand decisions

*Chained comparisons and `in` — the three decisions a blackjack player makes.*

## Read first
- [Comparisons in Python (language reference)](https://devdocs.io/python~3.14/reference/expressions#comparisons) — comparisons CHAIN: `8 < total < 12` is one expression, and the middle is evaluated once
- [Membership test operations](https://devdocs.io/python~3.14/reference/expressions#membership-test-operations) — `in` asks "is this a member of that", which reads better than a pile of `==` joined by `or`
- [Value comparisons](https://devdocs.io/python~3.14/reference/expressions#value-comparisons) — every comparison hands back `True` or `False`, so a function whose whole body is one comparison can simply return it; no `if` statement is needed
- [Comparisons in Python (stdtypes)](https://devdocs.io/python~3.14/library/stdtypes#comparisons) — the operator table
- [Sequence types](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — a tuple is the cheapest thing to ask `in` about
- [Conditional expressions](https://devdocs.io/python~3.14/reference/expressions#conditional-expressions) — `a if test else b`, for when a branch really is needed
- [Python basic operators (Tutorials Point)](https://www.tutorialspoint.com/python/python_basic_operators.htm) — a worked list with output

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
The scoring half of the casino's blackjack table is done — card values and rankings work. Now the table has to answer the three questions a player asks the moment their first two cards land: is this an instant win, may I split these into two hands, and may I double my bet? Each is a rule from the casino's rulebook, each is one line of comparisons, and each is the kind of rule that gets written wrong by summing when it should be checking membership.

## You get
`value_of_card` is already written for you above the stub, marked `# given — do not edit` — use it, do not rewrite it. Cards arrive as strings, always one of: `'2' '3' '4' '5' '6' '7' '8' '9' '10' 'J' 'Q' 'K' 'A'`.

> [!NOTE]
> Exercism asks for all six functions in one `black_jack.py`. Here the task is split in two: tasks 1–3 are task `006_black_jack`, and **this task covers tasks 4–6**. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions, all returning `True` or `False`.

| key | parameters | returns `True` when |
| --- | --- | --- |
| `"is_blackjack"` | `card_one`, `card_two` — the two cards dealt first | the hand is a "blackjack" (or "natural"): an ace together with any ten-card (`'10'`, `'J'`, `'Q'` or `'K'`) |
| `"can_split_pairs"` | `card_one`, `card_two` | the two cards have the same scoring value, so the player may split the hand into two separate hands. Two sixes qualify; so do a queen and a king, because both score 10 |
| `"can_double_down"` | `card_one`, `card_two` | the two cards total 9, 10 or 11 points, counting an ace as 1, so the player may double their bet |

```python
hand = solve()
hand["is_blackjack"]('A', 'K')      # -> True   (ace plus a ten-card)
hand["is_blackjack"]('A', 'A')      # -> False  (an ace is not a ten-card)
hand["can_split_pairs"]('Q', 'K')   # -> True   (both score 10)
hand["can_split_pairs"]('10', 'A')  # -> False  (10 against 1)
hand["can_double_down"]('A', '9')   # -> True   (1 + 9 = 10, inside 9..11)
hand["can_double_down"]('10', '2')  # -> False  (12 is one too many)
```

## Rules
- this task implements **Exercism tasks 4, 5 and 6 only** — `value_of_card`, `higher_card` and `value_of_ace` belong to task `006_black_jack`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- all three return booleans — the tests compare with `==`, so `1`/`0` would pass here, but neighbouring tasks check `is True`; write `True`/`False`
- the casino wants `is_blackjack` checked by looking for an ace AND a ten-card in the hand, not by adding the hand up to 21

## Hints
### Hint 1
Each of the three is a single expression that is already `True` or `False` — you can return the comparison itself, no `if` and no `return True` / `return False`. All three may reuse the already-implemented `value_of_card`. For the first one, resist adding the two cards up: the rule is about WHICH two cards are present, and one of them is not identified by its score.
### Hint 2
Blackjack: one of the two cards must be the ace and one of them must score 10 — two separate membership questions joined with `and`. You can chain BOTH comparison operators and boolean operators arbitrarily: `y < z < x`, or `(y or z) and (x or z)`. Watch the ace-with-ace case: it has an ace, but no ten-card, so it must come out `False`.

Splitting pairs is one `==` between the two card values; you can handle the `'A'` case separately if that reads more clearly.

Doubling down: 9, 10 or 11 is one range, and Python lets you write a range as a single chained comparison with the total in the middle. An `'A'` scored at 11 would never allow doubling down with two cards in hand, which is exactly why `value_of_card` scoring it as 1 is the version you want here.
### Hint 3
Different data, same shape. A delivery may go by bike when it has a small parcel and a city address, and it is 'oversize' when the two side lengths add up to somewhere between 100 and 150 cm:

```python
def by_bike(a, b):
    return 'small' in (a, b) and 'city' in (a, b)
def oversize(a, b):
    return 99 < side(a) + side(b) < 151
```

First one asks about membership twice; the second one chains a range around a sum. `'small' in (a, b)` is short for `a == 'small' or b == 'small'`.
