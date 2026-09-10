---
title: decimal — a service charge that rounds the way the contract says it does
difficulty: medium
tier: core
minutes: 18
prereqs: [3]
tags: [exact-arithmetic, numbers]
---
# decimal — a service charge that rounds the way the contract says it does

*`Decimal` counts in the base people write prices in, and `quantize` is where you say out loud how many places you are keeping and which way half goes.*

## Read first
- [`decimal`](https://devdocs.io/python~3.14/library/decimal) — why `0.1 + 0.2` is a problem and what fixes it
- [`Decimal.quantize`](https://devdocs.io/python~3.14/library/decimal#decimal.Decimal.quantize) — rounding to a fixed number of places
- [Rounding modes](https://devdocs.io/python~3.14/library/decimal#rounding-modes) — `ROUND_HALF_UP` against the default `ROUND_HALF_EVEN`

## Why
A booking system adds a 12.5 percent service charge to every line on a bill. An eighth of a price lands exactly on half a cent surprisingly often — a four-pound-twenty ticket earns 52.5 pence — and the contract with the venue says half a cent goes up, in the customer's disfavour, every time. Python's own default disagrees: it rounds half to whichever neighbour is even, which is the right choice for statistics and the wrong one for a document somebody signed. The two answers differ by a penny per line, the bill footer stops matching the venue's, and the reconciliation takes a morning.

## You get
`prices` — a list of price strings, each with exactly two decimal places, like `["4.20", "12.04"]`. They are strings, not floats, on purpose.

`rate` — the service charge as a string, like `"0.125"`.

## You return
a tuple `(lines, total)`:

- `lines` — a list of `Decimal` values, one per price: the price plus its service charge.
- `total` — a `Decimal`, the sum of `lines`.

## Rules
- Build every `Decimal` from the string you were given. Never from a `float`.
- The service charge for a line is `price * rate`, rounded to two decimal places with `ROUND_HALF_UP`. Round the charge, then add it to the price — not the other way round.
- `total` is the sum of the already-rounded lines, so the footer of the bill is the sum of the rows on it.
- `prices` may be empty, and then `total` is `Decimal("0.00")`.

```python
solve(["4.20", "12.04"], "0.125")
# 4.20 * 0.125 is 0.52500 -> 0.53, so the line is 4.73
# 12.04 * 0.125 is 1.50500 -> 1.51, so the line is 13.55
# -> ([Decimal("4.73"), Decimal("13.55")], Decimal("18.28"))
```

> [!WARNING]
> `quantize` with no `rounding=` argument uses the context default, which is `ROUND_HALF_EVEN`. On the two prices above that gives 0.52 and 1.50 — a penny short on each — and every single non-tie in the list still agrees, so the bug hides until an eighth lands on the half.

> [!NOTE]
> `Decimal("0.01")` is what you quantize *to*: the exponent of that value is what says "two places", not a digit count you pass in.

## Hints
### Hint 1
`from decimal import Decimal, ROUND_HALF_UP` gives you both halves of the answer.
### Hint 2
One line's charge:

```python
charge = (Decimal(price) * Decimal(rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```
### Hint 3
`sum` starts from `0`, a plain `int`, which is fine for `Decimal` arithmetic but leaves an empty list returning `0` rather than a `Decimal`. `sum(lines, Decimal("0.00"))` sets the starting value, so the empty bill still totals to money.
