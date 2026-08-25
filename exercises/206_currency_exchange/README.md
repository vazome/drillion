---
title: numbers — the currency exchange desk
minutes: 12
prereqs: [200]
tags: [exercism, numbers, core]
source: exercism/python concept/currency-exchange (MIT, adapted)
---
# numbers — the currency exchange desk

*Arithmetic operators — the three sums a currency desk does before anything else.*

## Why
Your friend Chandler is going travelling and is convinced every
exchange booth is out to cheat him. He wants a pocket calculator that shows
him, before he hands over any cash, exactly what he should get back. This
first version does the three plainest sums a booth does: how much foreign
currency his money buys, how much of his own money he still has afterwards,
and what a stack of bills is worth. Get these right and the fee arithmetic
in the next drill is just these three, chained.

## You get
nothing. Every number arrives as an argument to one of your
functions.

## You return
a dict with these three functions.

  "exchange_money" — takes `budget` (how much of his own money he is
  changing, e.g. 127.5) and `exchange_rate` (how much of his own money one
  unit of the foreign currency costs, e.g. 1.2 means 1.20 USD buys 1 EUR).
  Returns how much foreign currency he gets.

  "get_change" — takes `budget` (what he had, e.g. 127.5) and
  `exchanging_value` (what he handed over the counter, e.g. 120). Returns
  what is left in his own currency.

  "get_value_of_bills" — takes `denomination` (the face value of one bill,
  always a whole number, e.g. 5) and `number_of_bills` (e.g. 128). Returns
  what that stack of bills is worth.

## Rules
The dict keys are exactly the three strings above. `exchange_rate` is never
zero. Answers may come out as floats; nothing is rounded.

```python
exchange_money(127.5, 1.2)     ->  106.25   (127.50 of his money buys 106.25)
get_change(127.5, 120)         ->  7.5      (he keeps the rest)
get_value_of_bills(5, 128)     ->  640      (128 bills of 5)
```

## Read first
- https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex  — the arithmetic operators table: + - * / // % and what each returns
- https://docs.python.org/3/tutorial/introduction.html#numbers  — the five-minute tour: `/` always hands back a float, even when the division comes out even
- CONCEPT: numbers — int and float, and the fact that Python quietly widens the narrower type when you mix them in one expression.

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
One operator each, and the hard part is picking which. The rate is quoted as 'how much of MY money buys one of THEIRS', so going from his money to theirs is the operation that undoes multiplying by the rate. The other two are the obvious ones: what is left after handing some over, and what N things of the same size add up to.
### Hint 2
Sanity-check each formula on a rate you can do in your head. At a rate of 2, 100 of his money must come back as 50 of theirs — so if your expression gives 200, you have the division the wrong way round. Then build the dict mapping each key string to the function object (no parentheses).
### Hint 3
Different data, same shape. Petrol at 1.75 per litre, a 60-litre tank, a 50-euro note:

```
litres = 50 / 1.75        # 28.57...  money -> litres, so divide by price
left_over = 60 - 28.57    # litres of tank still empty
tank_cost = 1.75 * 60     # 105.0     price per unit x number of units
```

Same three shapes, in the same order, on numbers you can check by eye.
