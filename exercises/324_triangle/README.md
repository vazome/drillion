---
title: triangle — equilateral, isosceles or scalene
minutes: 10
prereqs: [200, 203, 206]
tags: [exercism, bools, core]
source: exercism/python practice/triangle (MIT, adapted)
---
# triangle — equilateral, isosceles or scalene

*triangle — three predicates that all share one validity check.*

## Why
Three questions, one shared precondition — that is the pattern here, and it is everywhere. Is this deployment production? Is it canary? Is it rollback? None of those questions has an answer at all if the manifest is malformed, so every one of them has to run the same validation first. The lazy version duplicates the check three times and drifts; the version worth writing pulls it into one helper that all three call. The classification itself is a good exercise in reading a definition literally: "at least two sides equal" is not the same as "exactly two", and the difference decides whether an equilateral triangle is also isosceles.

## Instructions
Determine if a triangle is equilateral, isosceles, or scalene.

An _equilateral_ triangle has all three sides the same length.

An _isosceles_ triangle has at least two sides the same length.
(It is sometimes specified as having exactly two sides the same length, but for the purposes of this exercise we'll say at least two.)

A _scalene_ triangle has all sides of different lengths.

### Note

For a shape to be a triangle at all, all sides have to be of length > 0, and the sum of the lengths of any two sides must be greater than or equal to the length of the third side.

> [!NOTE]
> _Degenerate triangles_ are triangles where the sum of the length of two sides is **equal** to the length of the third side, e.g. `1, 1, 2`.
> We opted to not include tests for degenerate triangles in this exercise.
> You may handle those situations if you wish to do so, or safely ignore them.

In equations:

Let `a`, `b`, and `c` be sides of the triangle.
Then all three of the following expressions must be true:

```text
a + b ≥ c
b + c ≥ a
a + c ≥ b
```

See [Triangle Inequality][triangle-inequality]

[triangle-inequality]: https://en.wikipedia.org/wiki/Triangle_inequality

## You get
Nothing. `solve()` takes **no arguments**; the sides arrive as an argument to each of the functions you hand back. That argument, `sides`, is always a list of three numbers — `int` or `float`:

```python
[3, 4, 4]
```

> [!NOTE]
> Exercism asks for three functions, `equilateral(sides)`, `isosceles(sides)` and `scalene(sides)`, in one `triangle.py`. Here there is one entry point: `solve()` returns a dict that hands all three to the grader, keyed by name.

## You return
A dict with these three functions. Each one takes `sides` and returns a `bool`.

| key | `True` when |
| --- | --- |
| `"equilateral"` | it is a valid triangle and all three sides are the same length |
| `"isosceles"` | it is a valid triangle and **at least** two sides are the same length |
| `"scalene"` | it is a valid triangle and all three sides differ |

```python
shapes = solve()
shapes["equilateral"]([2, 2, 2])  # -> True
shapes["equilateral"]([0, 0, 0])  # -> False   not a triangle at all
shapes["isosceles"]([4, 4, 4])    # -> True    equilateral counts as isosceles
shapes["isosceles"]([1, 1, 3])    # -> False   1 + 1 is less than 3
shapes["scalene"]([5, 4, 6])      # -> True
shapes["scalene"]([4, 3, 3])      # -> False
```

## Rules
- validity comes first: every side must be greater than 0, and the two shorter sides added together must be at least as long as the longest one. An invalid triple is `False` for all three questions
- the categories overlap by design: every equilateral triangle is also isosceles, and no isosceles triangle is scalene
- sides may be floats, and the order of the three sides in the list means nothing
- the three functions are independent — each is handed a fresh `sides` list and answers on its own

> [!WARNING]
> Return real `True` / `False`, not something merely truthy. The grader compares with `is`, so `1`, `0`, `[]` and `None` all fail even where they would "work" in an `if`.

## Read first
- [Boolean values](https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values) — `True` and `False` are the objects the grader compares against by identity
- [Boolean operations: and, or, not](https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not) — and the fact that `and` returns an operand, not always a `bool`
- [Truth value testing](https://docs.python.org/3/library/stdtypes.html#truth) — why "truthy" and "is `True`" are different questions
- [all() and any()](https://docs.python.org/3/library/functions.html#all) — three comparisons collapsed into one call, and both do return real bools
- [sorted()](https://docs.python.org/3/library/functions.html#sorted) — put the sides in order once and the inequality check stops needing three cases

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Write the validity check as its own small function before you touch the three categories, because all three begin with it and you do not want the rule written down three times. Then look at the inequality: the instructions list three comparisons, but if you know which side is the longest, two of them are free. Sorting the list gives you that for nothing.

### Hint 2
A private helper — call it `valid` — answers "is this a triangle at all": every side above zero, and the two smallest adding up to at least the largest. Sort a copy of the list and that second condition is one comparison. Each category function is then a call to `valid` combined with the one test that is actually its own. For the categories, count how many distinct lengths there are: three distinct means scalene, one means equilateral, and "at least two the same" means fewer than three distinct. A set built from the sides tells you that count in one step. Wrap the final expression in `bool(...)` if you are chaining `and`s, since `and` hands back an operand rather than a boolean.

### Hint 3
Different data, same shared-guard-then-classify shape — bucketing a service by its replica count, where nothing can be classified until the manifest is sane:

```python
def usable(spec):
    return spec.get('replicas', 0) > 0 and bool(spec.get('image'))

def single(spec):
    return usable(spec) and spec['replicas'] == 1

def scaled(spec):
    return usable(spec) and spec['replicas'] > 1

single({'replicas': 1, 'image': 'api:v2'})   # -> True
scaled({'replicas': 0, 'image': 'api:v2'})   # -> False
```

One guard, written once, reused by every question; each question then adds only the part that is actually its own. The `bool(...)` is there so the answer is a real boolean and not whatever the last operand happened to be.
