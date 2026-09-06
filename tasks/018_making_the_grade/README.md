---
title: loops — rounding and counting exam scores
difficulty: medium
tier: core
minutes: 12
prereqs: [6, 15]
tags: [loops]
source: exercism/python concept/making-the-grade (MIT, adapted)
---
# loops — rounding and counting exam scores

*A `while` that drains a list, and two `for` loops — one that counts, one that collects.*

## Read first
- [`for` statements (Python tutorial)](https://devdocs.io/python~3.14/tutorial/controlflow#for-statements) — the `for each` loop, which is what Python's `for` really is
- [the `while` statement](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — keeps going while its test is truthy; an empty list is falsy
- [truth value testing](https://devdocs.io/python~3.14/library/stdtypes#truth-value-testing) — why `while student_scores:` is a complete stopping condition
- [`round()`](https://devdocs.io/python~3.14/library/functions#round) — one argument gives you an `int`; two give you a `float`
- [more on lists](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists) — `append()` and `pop()`, the two methods these three loops are built from
- [Loop Like a Native (Ned Batchelder)](https://nedbatchelder.com/text/iter.html) — the talk that explains why you almost never need an index
- [`for` loops in Python (Real Python)](https://realpython.com/python-for-loop/) — the long version, with `range()`
- [`while` loops in Python (Real Python)](https://realpython.com/python-while-loop/) — including the ways they fail to terminate
- [control flow for loops](https://devdocs.io/python~3.14/tutorial/controlflow#break-and-continue-statements-and-else-clauses-on-loops) — `break`, `continue` and the loop `else`, used properly in the next task

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
You are the teaching assistant with a pile of exam scores, and the three things you do with them are the three things every loop you write at work does: transform every item, count the items that match a rule, and collect the items that match a rule. Write them once as explicit loops with an explicit counter and an explicit results list, and you will recognise them instantly later — when they show up as a comprehension over a list of pods, a `sum()` over invoices, or a filter over a week of latency samples. This is the vocabulary task that makes those shorthands readable.

## You get
Nothing. `solve()` takes **no arguments**; the grader calls your functions with the score lists.

> [!NOTE]
> Exercism asks for all six functions in one `loops.py`. Here the task is split in two: **this task covers tasks 1–3**, and tasks 4–6 are task `019_making_the_grade`. There is one entry point — `solve()` returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"round_scores"` | `student_scores` — a list of scores, some of them `float` (partial credit), possibly empty | a new list of `int`s, one per score; the order is **not** graded |
| `"count_failed_students"` | `student_scores` — a list of `int` scores | how many students did not pass, as an `int` |
| `"above_threshold"` | `student_scores`, `threshold` | a list of the scores that reach the threshold, in the order they appeared |

```python
grades = solve()
grades["round_scores"]([90.33, 40.5, 30.55, 38.7])
# -> [39, 31, 40, 90]    any order; note 40.5 rounds DOWN to 40
grades["count_failed_students"]([90, 40, 55, 70, 30, 25, 80, 95, 38, 40])
# -> 5
grades["above_threshold"]([90, 40, 55, 70, 30, 68, 70, 75, 83, 96], 75)
# -> [90, 75, 83, 96]
```

## Rules
- this task implements **Exercism tasks 1, 2 and 3 only** — `letter_grades`, `student_ranking` and `perfect_score` belong to task `019_making_the_grade`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- a score **greater than 40** passes, so `40` itself is a failure and `41` is not
- `above_threshold` uses `>=`, keeps the original order and returns `[]` when nothing qualifies — including when the score list is empty
- `round_scores` order is not graded (both sides are sorted before comparing), but every score must appear exactly once, and an empty list in gives an empty list out
- rounding is the built-in `round()`, which is not the rounding you were taught at school: it sends halves to the nearest **even** integer, so `round(0.5)` is `0`, `round(1.5)` is `2` and `round(40.5)` is `40`

> [!WARNING]
> `round()` returns an `int` only when you call it with one argument. `round(40.5, 0)` gives the float `40.0`, and a list of floats fails a test that expects a list of ints.

## Hints
### Hint 1
Three loops, three shapes, and it is worth naming the shape before you write it.

The first is a `while`: it keeps executing until its test condition evaluates to `False`, so something inside the loop has to make progress towards that or it never stops. The second sets up a results counter before the loop and increments it inside — you return the count once the loop has terminated. The third does the same thing with an empty list instead of a counter, and adds to it.
### Hint 2
Most empty objects in Python are falsy, lists included, so `while student_scores:` is already the whole condition — no length check, no index. `<list>.pop()` removes **and returns** the last item, which is both "make progress" and "here is the value to work on". Round it and append it to your results list.

The other two are plain `for score in student_scores:` — there is no need to declare a loop counter or an index counter when you iterate over an object with a `for` loop. In the counting one, `+= 1` inside an `if`; in the collecting one, `<list>.append(score)` inside an `if`. Both return the thing you set up *before* the loop, *after* the loop has finished — a `return` inside the loop stops it on the first item.

Mind the two boundaries: failing is *at or below* 40, and "the best" is *at or above* the threshold.
### Hint 3
Different data, same three shapes — file sizes and request latencies:

```python
sizes = [4.2, 8.9, 1.5]
whole = []
while sizes:
    whole.append(round(sizes.pop()))
whole                       # -> [2, 9, 4]     reversed, because pop() takes from the end

latencies = [120, 340, 95, 780]
slow = 0
for ms in latencies:
    if ms > 300:
        slow += 1
slow                        # -> 2

worst = []
for ms in latencies:
    if ms >= 300:
        worst.append(ms)
worst                       # -> [340, 780]    original order preserved
```

Note `round(1.5)` came out as `2` and `round(4.2)` as `4` — halves go to the nearest even number, everything else goes the way you expect.
