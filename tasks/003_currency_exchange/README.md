---
title: numbers — the currency exchange desk
difficulty: easy
tier: core
minutes: 12
prereqs: [1]
tags: [numbers]
source: exercism/python concept/currency-exchange (MIT, adapted)
---
# numbers — the currency exchange desk

*Arithmetic operators — the three sums a currency desk does before anything else.*

## Read first
- [Arithmetic Operations](https://devdocs.io/python~3.14/library/stdtypes#numeric-types-int-float-complex) — the arithmetic operators table: `+ - * / // %` and what each returns
- [The Python Numbers tutorial](https://devdocs.io/python~3.14/tutorial/introduction#numbers) — the five-minute tour: `/` always hands back a float, even when the division comes out even
- [integers](https://devdocs.io/python~3.14/library/functions#int) — `int()`, whole numbers of arbitrary precision
- [floats](https://devdocs.io/python~3.14/library/functions#float) — `float()`, and the 15-digits-of-precision caveat
- [Operator Precedence](https://devdocs.io/python~3.14/reference/expressions#operator-precedence) — which part of a long expression happens first
- [Decimals](https://devdocs.io/python~3.14/library/decimal#decimal-decimal-fixed-point-and-floating-point-arithmetic) — what you reach for when float rounding is not acceptable (real money, later)
- [fractions](https://devdocs.io/python~3.14/library/fractions) — exact rational arithmetic
- [Python's numerical and mathematical modules](https://devdocs.io/python~3.14/library/numeric) — the wider shelf

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Your friend Chandler is going travelling and is convinced every exchange booth is out to cheat him. He wants a pocket calculator that shows him, before he hands over any cash, exactly what he should get back. This first version does the three plainest sums a booth does: how much foreign currency his money buys, how much of his own money he still has afterwards, and what a stack of bills is worth. Get these right and the fee arithmetic in the next task is just these three, chained.

## You get
Nothing. Every number arrives as an argument to one of your functions.

> [!NOTE]
> Exercism asks for all six functions in one `exchange.py`. Here the task is split in two: **this task covers tasks 1–3**, and tasks 4–6 are task `004_currency_exchange`. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"exchange_money"` | `budget` (how much of his own money he is changing, e.g. `127.5`), `exchange_rate` (how much of his own money one unit of the foreign currency costs, e.g. `1.2` means 1.20 USD buys 1 EUR) | how much foreign currency he gets |
| `"get_change"` | `budget` (what he had, e.g. `127.5`), `exchanging_value` (what he handed over the counter, e.g. `120`) | what is left in his own currency |
| `"get_value_of_bills"` | `denomination` (the face value of one bill, always a whole number, e.g. `5`), `number_of_bills` (e.g. `128`) | what that stack of bills is worth |

```python
desk = solve()
desk["exchange_money"](127.5, 1.2)     # -> 106.25   (127.50 of his money buys 106.25)
desk["get_change"](127.5, 120)         # -> 7.5      (he keeps the rest)
desk["get_value_of_bills"](5, 128)     # -> 640      (128 bills of 5)
```

## Rules
- this task implements **Exercism tasks 1, 2 and 3 only** — `get_number_of_bills`, `get_leftover_of_bills` and `exchangeable_value` belong to task `004_currency_exchange`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- `exchange_rate` is never zero
- answers may come out as floats; nothing is rounded, and nothing is converted to `int` in this task

## Hints
### Hint 1
One operator each, and the hard part is picking which. The rate is quoted as 'how much of MY money buys one of THEIRS', so going from his money to theirs is the [division](https://devdocs.io/python~3.14/tutorial/introduction#numbers) that undoes multiplying by the rate. The other two are the obvious ones: [subtraction](https://devdocs.io/python~3.14/tutorial/introduction#numbers) for what is left after handing some over, and [multiplication](https://devdocs.io/python~3.14/tutorial/introduction#numbers) for what N things of the same size add up to.
### Hint 2
Sanity-check each formula on a rate you can do in your head. At a rate of 2, 100 of his money must come back as 50 of theirs — so if your expression gives 200, you have the division the wrong way round. Then build the dict mapping each key string to the function object (no parentheses). The [Python numbers tutorial](https://devdocs.io/python~3.14/tutorial/introduction#numbers) and [Python numeric types](https://devdocs.io/python~3.14/library/stdtypes#numeric-types-int-float-complex) are a great introduction if any of the three operators is new.
### Hint 3
Different data, same shape. Petrol at 1.75 per litre, a 60-litre tank, a 50-euro note:

```python
litres = 50 / 1.75        # -> 28.571...  money -> litres, so divide by price
left_over = 60 - litres   # -> 31.428...  litres of tank still empty
tank_cost = 1.75 * 60     # -> 105.0      price per unit x number of units
```

Same three shapes, in the same order, on numbers you can check by eye.
