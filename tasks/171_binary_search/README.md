---
title: loops — find a value in a sorted list by halving
difficulty: medium
tier: core
minutes: 10
prereqs: [11, 18]
tags: [loops]
source: exercism/python practice/binary-search (MIT, adapted)
---
# loops — find a value in a sorted list by halving

*binary-search — two bounds closing in, and the index you hand back is the one you were standing on.*

## Read first
- [The `while` statement](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — loop while the two bounds have not yet crossed
- [Floor division `//`](https://devdocs.io/python~3.14/library/stdtypes#numeric-types-int-float-complex) — the midpoint of two indices, rounded down to a real index
- [Raising exceptions](https://devdocs.io/python~3.14/tutorial/errors#raising-exceptions) — `raise ValueError("…")` with the exact message

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Every lookup against a sorted index is this loop: a database walking a B-tree, a log reader seeking to a timestamp, `bisect` in the standard library. Writing it once by hand is how the off-by-one stops being frightening — the bug is never the halving, it is the bound you forgot to move, and then the loop either spins forever or stops one place short of the answer.

## You get
- `values` — a list of `int`s, sorted ascending, no duplicates, e.g. `[1, 3, 4, 6, 8, 9, 11]`. It may be empty.
- `target` — the value to find, an `int`, e.g. `6`.

> [!NOTE]
> Exercism's stub is `def find(search_list, value)`. Here it is `solve(values, target)` — same two arguments, same order.

## You return
An `int` — the index of `target` in `values`.

## Rules
- return the **index**, not the value
- if `target` is not there — an empty list included — raise `ValueError("value not in array")`
- halve; do not scan. `values.index(target)` finds the right index, but it scans — and when the
  value is absent it raises `ValueError` with Python's own wording, not the message above
- `values` arrives sorted, so you never sort it yourself

```python
solve([1, 3, 4, 6, 8, 9, 11], 6)  # -> 3
solve([1, 3, 4, 6, 8, 9, 11], 1)  # -> 0
solve([6], 6)                     # -> 0
```

## Hints
### Hint 1
Keep two indices: the lowest position still worth checking and the highest. Each pass looks at the middle of that span and throws away the half that cannot possibly hold the target. The search is over when the two bounds cross.

### Hint 2
The middle is the average of the two bounds, floored. Compare the value sitting there with the target: too big, and the answer is to the left, so the upper bound comes down to just below the middle; too small, and the lower bound goes up to just above it. Move *past* the middle, never onto it — leaving a bound where it already was is exactly how this loop hangs. If the loop finishes, there is nothing left to check, and that is your `ValueError`.

### Hint 3
Different data, same shape — guessing a number between 1 and 100:

```text
lo=1   hi=100  mid=50  too low   -> lo=51
lo=51  hi=100  mid=75  too high  -> hi=74
lo=51  hi=74   mid=62  too high  -> hi=61
lo=51  hi=61   mid=56  too low   -> lo=57
lo=57  hi=61   mid=59  correct
```

Each line halves what is left, and each line moves a bound *past* the value it has just ruled out. The list version is the same five columns; the only differences are that what you compare is the element at `mid` rather than `mid` itself, and that what you hand back is `mid`.
