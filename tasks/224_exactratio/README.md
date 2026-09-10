---
title: fractions — scale a recipe without the thirds drifting
difficulty: easy
tier: core
minutes: 12
prereqs: [3]
tags: [exact-arithmetic, numbers]
---
# fractions — scale a recipe without the thirds drifting

*A `Fraction` is a numerator and a denominator kept apart, so a third stays a third instead of becoming 0.3333333333333333.*

## Read first
- [`fractions`](https://devdocs.io/python~3.14/library/fractions) — `Fraction(numerator, denominator)` and the arithmetic it supports
- [`Fraction`](https://devdocs.io/python~3.14/library/fractions#fractions.Fraction) — why it normalises to lowest terms on its own
- [Floating-point arithmetic](https://devdocs.io/python~3.14/tutorial/floatingpoint) — what a binary float can and cannot hold

## Why
A kitchen sheet lists each ingredient as a fraction of a cup, and the head chef wants tonight's batch at five quarters of the usual size. Do it in floats and three one-third cups add up to 0.9999999999999998 of a cup, which prints as `1.0` on the sheet, compares as not equal to one in the check that follows, and sets off an alarm about a missing ingredient that is not missing. Thirds, sixths and twelfths have no exact form in binary, and a kitchen deals in nothing else.

## You get
`amounts` — a list of `(numerator, denominator)` integer pairs, each one an ingredient's quantity in cups.

`scale` — a single `(numerator, denominator)` pair, the factor to multiply the whole recipe by.

## You return
a tuple `(scaled, total)`:

- `scaled` — a list of `Fraction` values, one per ingredient, each already multiplied by `scale`.
- `total` — a `Fraction`, the sum of `scaled`.

## Rules
- Every value in and out is exact. No `float` appears anywhere in the arithmetic, not even briefly.
- A `Fraction` reduces itself, so `Fraction(2, 4)` and `Fraction(1, 2)` are the same object's worth of value and compare equal. You never have to reduce anything by hand.
- Denominators are never zero.
- `amounts` may be empty, and then `total` is `Fraction(0)`.

```python
solve([(1, 3), (1, 3), (1, 3)], (1, 1))
# -> ([Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)], Fraction(1, 1))

solve([(1, 2), (2, 3)], (5, 4))
# -> ([Fraction(5, 8), Fraction(5, 6)], Fraction(35, 24))
```

> [!NOTE]
> `Fraction(1, 3) + Fraction(1, 3) + Fraction(1, 3) == 1` is `True`. The same sum in floats is not, and no amount of rounding at the end recovers what the middle of the calculation threw away.

## Hints
### Hint 1
`Fraction(*pair)` unpacks a `(numerator, denominator)` tuple straight into the constructor.
### Hint 2
Build the scale once, outside the loop, and multiply each ingredient by it — `Fraction` supports `*` with another `Fraction` and gives a `Fraction` back.
### Hint 3
`sum` on `Fraction` values works and returns a `Fraction`, but on an empty list it returns the `int` `0`. Give it a start value — `sum(scaled, Fraction(0))` — so an empty recipe still totals to a `Fraction`.
