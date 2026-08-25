---
title: numbers — whole bills, leftovers and the booth's cut
minutes: 15
prereqs: [200, 206]
tags: [exercism, numbers, core]
source: exercism/python concept/currency-exchange (MIT, adapted)
---
# numbers — whole bills, leftovers and the booth's cut

*Floor division and modulo — whole bills out, the booth keeps the remainder.*

## Why
Chandler's exchange calculator now has to face the counter clerk. A
booth pays out in notes, not in exact amounts: ask for 127.50 in 20s and you
get six notes — 120 — and the booth quietly keeps the 7.50. On top of that
the booth adds a "spread", a percentage on the exchange rate that is its
fee. Chandler wants to see, before he hands over any cash, exactly how many
notes come back, exactly how much the booth pockets, and the final figure
once the spread is in. Everything below is floor division and remainders,
which is the same arithmetic as pagination, batch sizes and disk blocks.

## You get
nothing. Every number arrives as an argument to one of your
functions.

## You return
a dict with these three functions.

  "get_number_of_bills" — takes `amount` (what is being paid out, e.g.
  127.5) and `denomination` (the face value of one note, a whole number,
  e.g. 5). Returns how many whole notes fit inside that amount. Fractions of
  a note do not exist.

  "get_leftover_of_bills" — takes the same `amount` and `denomination`.
  Returns the part of the amount that cannot be paid out in whole notes —
  the booth's bonus.

  "exchangeable_value" — takes `budget` (his money, e.g. 127.25),
  `exchange_rate` (how much of his money one unit of theirs costs, e.g.
  1.20), `spread` (the booth's fee as a whole-number percentage of the rate,
  e.g. 10) and `denomination` (e.g. 20). Returns the largest amount of
  foreign currency he can actually walk away with, in whole notes.

## Rules
The dict keys are exactly the three strings above. Amounts are never
negative, `denomination` is a whole number of at least 1, and the rate plus
its spread is never zero.

The spread is a percentage OF THE RATE, added to it: rate 1.20 with a spread
of 10 means 10% of 1.20 is 0.12, so the real rate Chandler pays is 1.32.

```python
get_number_of_bills(127.5, 5)          ->  25    (25 notes of 5 = 125)
get_leftover_of_bills(127.5, 20)       ->  7.5   (6 notes of 20 = 120)
exchangeable_value(127.25, 1.20, 10, 20)  ->  80
    (127.25 at the real rate of 1.32 is 96.4; in notes of 20 that is
     four notes, so 80 — the rest stays behind the counter)
exchangeable_value(127.25, 1.20, 10, 5)   ->  95
    (same 96.4, but notes of 5 waste far less)
```

## Read first
- https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex  — the operator table again, this time for `//` (floor division) and `%` (remainder)
- https://docs.python.org/3/library/functions.html#int  — int() truncates towards zero, which is NOT the same thing as rounding
- CONCEPT: numbers — mixing int and float in one expression: `//` on a float still hands back a float, so the type you get out depends on what you put in.

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Two operators do the whole first half. One tells you how many times a size fits completely inside an amount; the other tells you what is left over when it no longer fits. In Python they are two characters each, and they are neighbours in the operator table. The third function does not need new arithmetic — it is the exchange sum you already know, then the first two.
### Hint 2
Order for `exchangeable_value`: work out the real rate first (rate plus the spread's share of the rate), convert the budget at that rate, then reduce that figure to whole notes and turn the note count back into money. Notice the answer is a count times a face value, so it comes out as a whole number even though the budget and the rate were not. Watch the type: `//` on a float still gives a float, so if the spec asks for an int, one int() in the right place settles it.
### Hint 3
Different data, same shape. Shipping 1000 items in boxes of 48:

```
full_boxes = 1000 // 48      # 20   whole boxes
left_on_pallet = 1000 % 48   # 40   items with no box
shipped = full_boxes * 48    # 960  what actually leaves the warehouse
```

The booth is the warehouse: notes are boxes, the leftover never ships.
