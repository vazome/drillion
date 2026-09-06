---
title: numbers — whole bills, leftovers and the booth's cut
difficulty: medium
tier: core
minutes: 15
prereqs: [3]
tags: [numbers]
source: exercism/python concept/currency-exchange (MIT, adapted)
---
# numbers — whole bills, leftovers and the booth's cut

*Floor division and modulo — whole bills out, the booth keeps the remainder.*

## Read first
- [Arithmetic Operations](https://devdocs.io/python~3.14/library/stdtypes#numeric-types-int-float-complex) — the operator table again, this time for `//` (floor division) and `%` (remainder)
- [integers](https://devdocs.io/python~3.14/library/functions#int) — `int()` truncates towards zero, which is NOT the same thing as rounding
- [floats](https://devdocs.io/python~3.14/library/functions#float) — mixing int and float in one expression: `//` on a float still hands back a float, so the type you get out depends on what you put in
- [Operator Precedence](https://devdocs.io/python~3.14/reference/expressions#operator-precedence) — `*` and `/` before `+`, so the spread needs its own parentheses or its own line
- [Decimals](https://devdocs.io/python~3.14/library/decimal#decimal-decimal-fixed-point-and-floating-point-arithmetic) — the grown-up answer to money arithmetic
- [fractions](https://devdocs.io/python~3.14/library/fractions) — exact rational arithmetic
- [Python's numerical and mathematical modules](https://devdocs.io/python~3.14/library/numeric) — the wider shelf

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Chandler's exchange calculator now has to face the counter clerk. A booth pays out in notes, not in exact amounts: ask for 127.50 in 20s and you get six notes — 120 — and the booth quietly keeps the 7.50. On top of that the booth adds a "spread", a percentage on the exchange rate that is its fee. Chandler wants to see, before he hands over any cash, exactly how many notes come back, exactly how much the booth pockets, and the final figure once the spread is in. Everything below is floor division and remainders, which is the same arithmetic as pagination, batch sizes and disk blocks.

## You get
Nothing. Every number arrives as an argument to one of your functions.

> [!NOTE]
> Exercism asks for all six functions in one `exchange.py`. Here the task is split in two: tasks 1–3 are task `003_currency_exchange`, and **this task covers tasks 4–6**. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"get_number_of_bills"` | `amount` (what is being paid out, e.g. `127.5`), `denomination` (the face value of one note, a whole number, e.g. `5`) | how many whole notes fit inside that amount — fractions of a note do not exist |
| `"get_leftover_of_bills"` | the same `amount` and `denomination` | the part of the amount that cannot be paid out in whole notes — the booth's bonus |
| `"exchangeable_value"` | `budget` (his money, e.g. `127.25`), `exchange_rate` (how much of his money one unit of theirs costs, e.g. `1.20`), `spread` (the booth's fee as a whole-number percentage of the rate, e.g. `10`), `denomination` (e.g. `20`) | the largest amount of foreign currency he can actually walk away with, in whole notes |

```python
booth = solve()
booth["get_number_of_bills"](127.5, 5)             # -> 25    (25 notes of 5 = 125)
booth["get_leftover_of_bills"](127.5, 20)          # -> 7.5   (6 notes of 20 = 120)
booth["exchangeable_value"](127.25, 1.20, 10, 20)  # -> 80
# 127.25 at the real rate of 1.32 is 96.4; in notes of 20 that is
# four notes, so 80 — the rest stays behind the counter
booth["exchangeable_value"](127.25, 1.20, 10, 5)   # -> 95
# same 96.4, but notes of 5 waste far less
```

## Rules
- this task implements **Exercism tasks 4, 5 and 6 only** — `exchange_money`, `get_change` and `get_value_of_bills` belong to task `003_currency_exchange`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- amounts are never negative, `denomination` is a whole number of at least 1, and the rate plus its spread is never zero

The spread is a percentage OF THE RATE, added to it: rate 1.20 with a spread of 10 means 10% of 1.20 is 0.12, so the real rate Chandler pays is 1.32.

> [!WARNING]
> Types are graded. `get_number_of_bills` and `exchangeable_value` must return an `int` — the tests compare them with `==`, not approximately. `get_leftover_of_bills` keeps the fraction, so it stays a float when the amount is a float.

## Hints
### Hint 1
Two operators do the whole first half. One tells you how many times a size fits completely inside an amount; the other tells you what is left over when it no longer fits. In Python they are two characters each (`//` and `%`), and they are neighbours in the operator table. The third function does not need new arithmetic — it is the exchange sum you already know, then the first two.

To remove the decimal places from a `float`, you can convert it to `int`. **Note:** the `//` operator also does floor division, but if either operand is a `float`, the result is still a `float`.
### Hint 2
Order for `exchangeable_value`: calculate `spread` percent of `exchange_rate` and add it to `exchange_rate` to get the actual rate; convert the budget at that rate; then reduce that figure to whole notes and turn the note count back into money. Notice the answer is a count times a face value, so it comes out as a whole number even though the budget and the rate were not. Watch the type: `//` on a float still gives a float, so if the spec asks for an `int`, one `int()` in the right place settles it.

For the leftover, you need the remainder of `amount` that does not make up a whole `denomination` — the modulo operator `%` finds it.
### Hint 3
Different data, same shape. Shipping 1000 items in boxes of 48:

```python
full_boxes = 1000 // 48      # -> 20   whole boxes
left_on_pallet = 1000 % 48   # -> 40   items with no box
shipped = full_boxes * 48    # -> 960  what actually leaves the warehouse
```

The booth is the warehouse: notes are boxes, the leftover never ships.
