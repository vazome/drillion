---
title: flatten-array — unpack the nested boxes into one flat list
minutes: 10
prereqs: [200, 209, 215, 221, 224, 227]
tags: [exercism, core]
source: exercism/python practice/flatten-array (MIT, adapted)
---
# flatten-array — unpack the nested boxes into one flat list

*flatten-array — one list out, whatever the depth in, and no `None` survives.*

## Why
Nested data arrives from everywhere: a JSON API that wraps results in results, a config file where a group can contain groups, a Terraform output whose lists hold lists. The consumer almost never wants the shape — it wants the items, in order, ready to iterate once. Flattening is also where "unknown depth" first bites: you cannot write two `for` loops when tomorrow's payload has four levels. Getting comfortable with a function that calls itself for the nested case is worth more than this exercise, because directory trees, org charts and dependency graphs all have the same shape.

## Introduction
A shipment of emergency supplies has arrived, but there's a problem.
To protect from damage, the items — flashlights, first-aid kits, blankets — are packed inside boxes, and some of those boxes are nested several layers deep inside other boxes!

To be prepared for an emergency, everything must be easily accessible in one box.
Can you unpack all the supplies and place them into a single box, so they're ready when needed most?

## Instructions
Take a nested array of any depth and return a fully flattened array.

Note that some language tracks may include null-like values in the input array, and the way these values are represented varies by track.
Such values should be excluded from the flattened array.

Additionally, the input may be of a different data type and contain different types, depending on the track.

Check the test suite for details.

### Example

input: `[1, [2, 6, null], [[null, [4]], 5]]`

output: `[1, 2, 6, 4, 5]`

## You get
`iterable` — a list that may contain numbers, `None`, and more lists, nested to any depth:

```python
[0, 2, [[2, 3], 8, 100, 4, [[[50]]]], -2]
```

Python's stand-in for the `null` in the instructions is `None`. Lists may be empty at any level.

> [!NOTE]
> Exercism's stub is `def flatten(iterable)`. Here the function is `solve(iterable)`; nothing else about the task changes.

## You return
A new flat `list` of the values, in the order they were met reading left to right, depth first.

## Rules
- a nested list is opened and its items take its place, however deep the nesting goes
- `None` is dropped wherever it appears
- an empty list contributes nothing, so `[[[]]]` flattens to `[]`
- the values themselves are not changed: `0` and `-2` are values and stay
- leave the input alone; build and return a new list

| in | out |
| --- | --- |
| `[]` | `[]` |
| `[0, 1, 2]` | `[0, 1, 2]` |
| `[[[]]]` | `[]` |
| `[1, [2, [[3]], [4, [[5]]], 6, 7], 8]` | `[1, 2, 3, 4, 5, 6, 7, 8]` |
| `[None, None, 3]` | `[3]` |

```python
solve([1, [2, 6, None], [[None, [4]], 5]])  # -> [1, 2, 6, 4, 5]
solve([0, 2, [[2, 3], 8, 100, 4, [[[50]]]], -2])  # -> [0, 2, 2, 3, 8, 100, 4, 50, -2]
```

> [!WARNING]
> `0` is falsy and `None` is falsy, so a filter written as `if item:` throws away the zeros too. Test against `None` by identity — `if item is not None` — not by truthiness.

## Read first
- [Recursion in the Python tutorial](https://docs.python.org/3/tutorial/controlflow.html#defining-functions) — a function is free to call itself; the nested case is just a smaller version of the same problem
- [isinstance()](https://docs.python.org/3/library/functions.html#isinstance) — "is this item a list, or a plain value?"
- [list.extend() vs list.append()](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists) — `extend` pours a list in, `append` puts the list itself in as one item
- [The `is` operator](https://docs.python.org/3/reference/expressions.html#is-not) — identity, and why `None` is always tested with it

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Walk the input one item at a time and ask a single question about each: is this a box, or is this a thing? Only three answers are possible — a nested list, `None`, or a value to keep — so the body of the loop has three branches and nothing else. The interesting branch is the box one, and the trick is that you already have a function which knows how to empty a box.

### Hint 2
Start a result list, loop over the items, and handle the three cases: for a plain value, add it; for `None`, skip; for a list, call your own function on it and add every item it hands back — `extend`, not `append`, or you rebuild the nesting you just removed. The recursion terminates on its own because each call is handed something strictly shallower than what it was given, and an empty list simply loops zero times. If recursion still feels like a leap of faith, trust the base case and check one two-level example by hand.

### Hint 3
Different data, same descend-and-collect — adding up file sizes in a directory listing that nests, where the accumulator is a number instead of a list:

```python
sizes = [12, [4, [8, 3]], None, [[5]]]

def total(node):
    running = 0
    for item in node:
        if isinstance(item, list):
            running += total(item)
        elif item is not None:
            running += item
    return running

total(sizes)   # -> 32
```

Three branches per item — a nested container, a hole, or a value — and the container branch calls the same function again and folds its answer in. Swap "add to a running number" for "add to a running list" and you have the shape this drill wants.
