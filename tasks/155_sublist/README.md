---
title: comparisons — say how two lists relate to each other
difficulty: medium
tier: core
minutes: 15
prereqs: [6, 13]
tags: [comparisons]
source: exercism/python practice/sublist (MIT, adapted)
---
# comparisons — say how two lists relate to each other

*sublist — equal, contains, contained by, or none of the above — decided in that order.*

## Read first
- [Comparing sequences](https://devdocs.io/python~3.14/tutorial/datastructures#comparing-sequences-and-other-types) — `==` on lists compares element by element, in order
- [Slicing](https://devdocs.io/python~3.14/reference/expressions#slicings) — `big[i:i + len(small)]` is a candidate window
- [any()](https://devdocs.io/python~3.14/library/functions#any) — "is there at least one window that matches?" in one expression
- [range()](https://devdocs.io/python~3.14/library/stdtypes#range) — getting the last valid start index right is the only arithmetic here

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
"Did the expected sequence of steps actually happen?" is a question you ask of logs, of CI pipelines, of deployment histories. You have a list of what happened and a list of what should have happened, and you need one of four answers: identical, the real run contains the expected run, the expected run contains the real one, or they simply disagree. The subtlety is that *contiguous* matters — a rollout that did `pull, migrate, restart` is not the same as one that did `pull, panic, migrate, restart`, even though every expected step is present.

## Instructions
Given any two lists `A` and `B`, determine if:

- List `A` is equal to list `B`; or
- List `A` contains list `B` (`A` is a superlist of `B`); or
- List `A` is contained by list `B` (`A` is a sublist of `B`); or
- None of the above is true, thus lists `A` and `B` are unequal

Specifically, list `A` is equal to list `B` if both lists have the same values in the same order.
List `A` is a superlist of `B` if `A` contains a contiguous sub-sequence of values equal to `B`.
List `A` is a sublist of `B` if `B` contains a contiguous sub-sequence of values equal to `A`.

Examples:

- If `A = []` and `B = []` (both lists are empty), then `A` and `B` are equal
- If `A = [1, 2, 3]` and `B = []`, then `A` is a superlist of `B`
- If `A = []` and `B = [1, 2, 3]`, then `A` is a sublist of `B`
- If `A = [1, 2, 3]` and `B = [1, 2, 3, 4, 5]`, then `A` is a sublist of `B`
- If `A = [3, 4, 5]` and `B = [1, 2, 3, 4, 5]`, then `A` is a sublist of `B`
- If `A = [3, 4]` and `B = [1, 2, 3, 4, 5]`, then `A` is a sublist of `B`
- If `A = [1, 2, 3]` and `B = [1, 2, 3]`, then `A` and `B` are equal
- If `A = [1, 2, 3, 4, 5]` and `B = [2, 3, 4]`, then `A` is a superlist of `B`
- If `A = [1, 2, 4]` and `B = [1, 2, 3, 4, 5]`, then `A` and `B` are unequal
- If `A = [1, 2, 3]` and `B = [1, 3, 2]`, then `A` and `B` are unequal

## You get
`list_one` and `list_two` — two lists of small integers, either of which may be empty:

```python
solve([1, 2, 5], [0, 1, 2, 3, 1, 2, 5, 6])
```

Four constants are already defined at the top of `task.py` and marked *do not edit* — `SUBLIST`, `SUPERLIST`, `EQUAL` and `UNEQUAL`. Use them by name.

> [!NOTE]
> Exercism's stub is `def sublist(list_one, list_two)` plus four constants you choose the values of. Here the function is `solve(list_one, list_two)` and the constants come with values fixed, so that the grader and your code agree on what "equal" looks like.

## You return
One of the four constants — never a string you typed yourself, never a boolean.

```python
solve([1, 2, 3], [1, 2, 3])           # -> EQUAL
solve([], [1, 2, 3])                  # -> SUBLIST
solve([1, 2, 3], [])                  # -> SUPERLIST
solve([1, 2, 3], [2, 3, 4])           # -> UNEQUAL
```

## Rules
The four cases are answered in this order, and the first one that fits wins:

| test | answer |
| --- | --- |
| the two lists are equal | `EQUAL` |
| `list_two` appears inside `list_one` as a contiguous run | `SUPERLIST` |
| `list_one` appears inside `list_two` as a contiguous run | `SUBLIST` |
| neither | `UNEQUAL` |

- "contiguous" means side by side with nothing in between: `[1, 2, 4]` is **not** inside `[1, 2, 3, 4, 5]`
- the empty list is contained in every list, so `solve([1, 2, 3], [])` is `SUPERLIST` and `solve([], [])` is `EQUAL`
- values are compared with `==`, so `[1, 2]` and `[1, 22]` are unequal and `[1, 0, 1]` and `[10, 1]` are unequal
- the run may start anywhere, including at the very beginning or the very end

```python
solve([1, 2, 5], [0, 1, 2, 3, 1, 2, 5, 6])   # -> SUBLIST
solve([1, 1, 2], [0, 1, 1, 1, 2, 1, 2])      # -> SUBLIST
solve([0, 1, 2, 3, 4, 5], [2, 3])            # -> SUPERLIST
solve([1, 2, 3], [3, 2, 1])                  # -> UNEQUAL
```

> [!WARNING]
> `[1, 2, 5]` inside `[0, 1, 2, 3, 1, 2, 5, 6]` is the case that catches naive scanning: the run starts at index 1, matches `1, 2`, then fails at `3` — and the answer is still `SUBLIST`, because a *later* start works. A single pass with one pointer gives the wrong answer; you must be able to restart.

## Hints
### Hint 1
There is one hard question and three easy ones. The hard question is "does this list contain that list as a contiguous run?" — write it as its own helper that returns `True` or `False`, and the four cases above become four lines that call it. Decide early what the helper should say about an empty needle, because two of the examples depend on it.
### Hint 2
For the helper: every possible match is a window of the big list with the same length as the small one, so generate those windows and ask whether any of them is equal to the small list. Slicing gives you a window directly, and comparing two lists with `==` already does the element-by-element work — you do not need a nested loop or an index that walks both lists at once. Watch the last start position: if the big list has 8 items and the small one has 3, the last window starts at index 5, so the range ends at `len(big) - len(small) + 1`.
### Hint 3
Different data, same "slide a window and compare" shape — checking whether a deploy log contains the expected run of steps:

```python
steps = ['pull', 'build', 'migrate', 'restart', 'healthcheck']
wanted = ['migrate', 'restart']

found = any(steps[i:i + len(wanted)] == wanted
            for i in range(len(steps) - len(wanted) + 1))
found          # -> True

any(steps[i:i + 2] == ['build', 'restart'] for i in range(len(steps) - 1))  # -> False
```

The second one is `False` precisely because `migrate` sits between the two steps: contiguity is the whole point.
