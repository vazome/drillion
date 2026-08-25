---
title: leap — does this year have a 29 February?
minutes: 10
prereqs: [200, 203, 206]
tags: [exercism, bools, core]
source: exercism/python practice/leap (MIT, adapted)
---
# leap — does this year have a 29 February?

*leap — three divisibility rules where the exceptions decide the answer.*

## Why
Anything that plans ahead — a shift rota, a billing cycle, a
backup that runs "on the last day of February" — has to know whether
the year has 366 days. The rule looks like one line of arithmetic but
it is really a rule with an exception and then an exception to the
exception, which is exactly the shape people get wrong. 1900 was not a
leap year; 2000 was. Software that assumed "every four years" shipped
bugs that only surfaced once a century.

## You get
`year` — a whole number, e.g. 1996.

## You return
`True` if that year is a leap year in the Gregorian
calendar, `False` if it is not. A real boolean, not the string "True".

## Rules
A year is a leap year when it divides evenly by 4 — unless it also
divides evenly by 100, in which case it is not, unless it divides
evenly by 400, in which case it is after all.

```python
solve(1996)  ->  True    (divides by 4, not by 100)
solve(1900)  ->  False   (divides by 100 but not by 400)
solve(2000)  ->  True    (divides by 400)
solve(2015)  ->  False   (does not divide by 4 at all)
```

## Read first
- https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not  — and / or / not, and the fact that they return a value, not just steer an `if`
- https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values  — True and False are ordinary values you can return straight out of an expression
- https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations  — `%`, the remainder operator you test divisibility with

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Three facts about the year: divisible by 4, by 100, by 400. Say the rule out loud in English first and notice which fact wins when several are true at once — 2000 is divisible by all three and is still a leap year.
### Hint 2
`year % 4 == 0` is already True or False, so you never need an `if` here: combine the three tests with `and`, `or` and `not` and return the whole expression. The 100-rule can only ever cancel a year that already passed the 4-rule, and the 400-rule only rescues a year the 100-rule cancelled.
### Hint 3
Different data, same shape: a subscription is active if it is paid, unless it was suspended, unless an admin overrode the suspension:

```
active = paid and (not suspended or override)
```

One general rule, an exception, an exception to the exception — the brackets are what keep the two exceptions from fighting.
