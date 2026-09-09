---
title: comprehensions — select and summarise sensor rows
difficulty: medium
tier: advanced
minutes: 15
prereqs: [21, 29, 130]
tags: [comprehension, generator-expressions, unpacking]
---
# comprehensions — select and summarise sensor rows

*Unpack variable-width rows, test their values lazily, and build the result in one pass.*

## Read first
- [List displays](https://devdocs.io/python~3.14/reference/expressions#list-displays) — comprehension clauses and filtering
- [Generator expressions](https://devdocs.io/python~3.14/reference/expressions#generator-expressions) — values consumed one at a time by `any`
- [Assignment statements](https://devdocs.io/python~3.14/reference/simple_stmts#assignment-statements) — extended unpacking with `name, *samples`

## Why
Sensor rows begin with a name and carry however many samples arrived. A summary should include only sensors that crossed an alert threshold, without building a second list just to ask whether one sample crossed it.

## You get
`rows`, tuples such as `("cpu", 20, 80)`, and an integer `threshold`.

## You return
A dictionary mapping each sensor that has at least one sample at or above the threshold to its mean, rounded to two decimals.

## Rules
Use a dictionary comprehension with extended unpacking in its `for` clause. Its filter must use `any` with a generator expression. Rows always carry at least one sample.

```python
solve([("cpu", 20, 80), ("disk", 10, 15), ("queue", 90)], 75)
# -> {"cpu": 50.0, "queue": 90.0}
```

## Hints
### Hint 1
The loop target can split a row directly: `for name, *samples in rows`.
### Hint 2
The filter is `any(value >= threshold for value in samples)`. Those parentheses feed values lazily to `any`.
### Hint 3
The dictionary's key is `name`; its value is `round(sum(samples) / len(samples), 2)`. Put the `any(...)` expression after the comprehension's `if`.
