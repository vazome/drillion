---
title: loops — find a value in a sorted list by halving
difficulty: medium
tier: core
minutes: 10
prereqs: [96, 101]
tags: [loops]
source: exercism/python practice/binary-search (MIT, adapted)
---
# loops — find a value in a sorted list by halving

*binary-search — two bounds closing in, and the index you hand back is the one you were standing on.*

## Read first
- [The `while` statement](https://docs.python.org/3/reference/compound_stmts.html#the-while-statement) — loop while the two bounds have not yet crossed
- [Floor division `//`](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex) — the midpoint of two indices, rounded down to a real index
- [Raising exceptions](https://docs.python.org/3/tutorial/errors.html#raising-exceptions) — `raise ValueError("…")` with the exact message

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Every lookup against a sorted index is this loop: a database walking a B-tree, a log reader seeking to a timestamp, `bisect` in the standard library. Writing it once by hand is how the off-by-one stops being frightening — the bug is never the halving, it is the bound you forgot to move, and then the loop either spins forever or stops one place short of the answer.

## Introduction
You have stumbled upon a group of mathematicians who are also singer-songwriters.
They have written a song for each of their favorite numbers, and, as you can imagine, they have a lot of favorite numbers (like [0][zero] or [73][seventy-three] or [6174][kaprekars-constant]).

You are curious to hear the song for your favorite number, but with so many songs to wade through, finding the right song could take a while.
Fortunately, they have organized their songs in a playlist sorted by the title — which is simply the number that the song is about.

You realize that you can use a binary search algorithm to quickly find a song given the title.

[zero]: https://en.wikipedia.org/wiki/0
[seventy-three]: https://en.wikipedia.org/wiki/73_(number)
[kaprekars-constant]: https://en.wikipedia.org/wiki/6174_(number)

## Instructions
Your task is to implement a binary search algorithm.

A binary search algorithm finds an item in a list by repeatedly splitting it in half, only keeping the half which contains the item we're looking for.
It allows us to quickly narrow down the possible locations of our item until we find it, or until we've eliminated all possible locations.

> [!WARNING]
> Binary search only works when a list has been sorted.

The algorithm looks like this:

- Find the middle element of a _sorted_ list and compare it with the item we're looking for.
- If the middle element is our item, then we're done!
- If the middle element is greater than our item, we can eliminate that element and all the elements **after** it.
- If the middle element is less than our item, we can eliminate that element and all the elements **before** it.
- If every element of the list has been eliminated then the item is not in the list.
- Otherwise, repeat the process on the part of the list that has not been eliminated.

Here's an example:

Let's say we're looking for the number 23 in the following sorted list: `[4, 8, 12, 16, 23, 28, 32]`.

- We start by comparing 23 with the middle element, 16.
- Since 23 is greater than 16, we can eliminate the left half of the list, leaving us with `[23, 28, 32]`.
- We then compare 23 with the new middle element, 28.
- Since 23 is less than 28, we can eliminate the right half of the list: `[23]`.
- We've found our item.

### Exception messages

Sometimes it is necessary to [raise an exception](https://docs.python.org/3/tutorial/errors.html#raising-exceptions). When you do this, you should always include a **meaningful error message** to indicate what the source of the error is. This makes your code more readable and helps significantly with debugging. For situations where you know that the error source will be a certain type, you can choose to raise one of the [built in error types](https://docs.python.org/3/library/exceptions.html#base-classes), but should still include a meaningful message.

This particular exercise requires that you use the [raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement) to "throw" a `ValueError` when the given value is not found within the array. The tests will only pass if you both `raise` the `exception` and include a message with it.

To raise a `ValueError` with a message, write the message as an argument to the `exception` type:

```python
# example when value is not found in the array.
raise ValueError("value not in array")
```

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
