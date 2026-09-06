---
title: tuples — reading the treasure coordinates
difficulty: easy
tier: core
minutes: 12
prereqs: [3, 18]
tags: [tuples]
source: exercism/python concept/tisbury-treasure-hunt (MIT, adapted)
---
# tuples — reading the treasure coordinates

*Indexing a tuple and building one — the two smallest tuple moves.*

## Read first
- [tuple](https://devdocs.io/python~3.14/library/stdtypes#tuple) — the constructor and the literal, and why a one-element tuple needs its trailing comma
- [Sequence types — list, tuple, range](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — where tuples sit among Python's sequences
- [Common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — indexing, `in`, `+` and `*`, all shared with strings and lists
- [Ned Batchelder: Lists vs Tuples](https://nedbatchelder.com/blog/201608/lists_vs_tuples.html) — the useful mental model: a list is a collection, a tuple is a record
- [Stack Overflow: what's the difference between lists and tuples?](https://stackoverflow.com/a/626871) — the short answer
- [James Tauber: tuples are not just constant lists](https://jtauber.com/blog/2006/04/15/python_tuples_are_not_just_constant_lists/) — why position means something in a tuple and nothing in a list
- [hashable](https://devdocs.io/python~3.14/glossary#term-hashable) — the property that lets a tuple be a dict key when a list cannot be

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Two treasure hunters kept their notes in different shapes. Azara writes a treasure and where it is as one pair — `('Brass Spyglass', '4B')` — while Rui writes the location with the coordinate already split into a tuple of its own: `('Abandoned Lighthouse', ('4', 'B'), 'Blue')`. Nothing can be matched until the two shapes agree, so the first job is the least glamorous one in any integration: pull the field you need out of one record, and reshape it into the format the other side speaks.

## You get
Nothing. The records arrive as arguments to your functions.

> [!NOTE]
> Exercism asks for five functions in one `tuples.py`. Here the task is split in two: **this task covers tasks 1–2**, and tasks 3–5 are task `024_tisbury_treasure_hunt`. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your two functions to the grader, keyed by name.

## You return
A dict with these two functions.

| key | parameters | returns |
| --- | --- | --- |
| `"get_coordinate"` | `record` — one `(treasure, coordinate)` pair from Azara's list | just the coordinate, the string exactly as it was stored |
| `"convert_coordinate"` | `coordinate` — a coordinate string like `'2A'` | a tuple of its two parts, `('2', 'A')`, both still strings |

```python
hunt = solve()
hunt["get_coordinate"](('Scrimshawed Whale Tooth', '2A'))  # -> '2A'
hunt["get_coordinate"](('Brass Spyglass', '4B'))           # -> '4B'
hunt["convert_coordinate"]('2A')                           # -> ('2', 'A')
hunt["convert_coordinate"]('7F')                           # -> ('7', 'F')
```

## Rules
- this task implements **Exercism tasks 1 and 2 only** — `compare_records`, `create_record` and `clean_up` belong to task `024_tisbury_treasure_hunt`
- a coordinate here is always exactly two characters: one digit, then one letter
- `convert_coordinate` returns the digit and the letter as **strings**, not as an `int` and a `str`
- neither function changes the record it is given

> [!WARNING]
> A list is not a tuple. `['2', 'A'] == ('2', 'A')` is `False`, and the tests compare with `==`, so returning a list fails even though it looks the same when printed.

## Hints
### Hint 1
A tuple is a sequence, so task 1 is plain bracket notation: index `0` is the leftmost item, index `1` the one after it (and `-1` counts back from the right). Task 2 goes the other way — you have a string and you want a tuple of its parts. The thing worth remembering is that a **string is itself iterable**, one character at a time.
### Hint 2
`tuple(<iterable>)` walks whatever you hand it and puts each element into the new tuple, so it is worth typing `tuple("hello")` into a REPL before you write anything — the result answers task 2 by itself. Because a coordinate is always exactly two characters, you need no slicing, no `split`, and no arithmetic.

Two things to keep in mind about the constructor: it needs an *iterable*, so a single value has to be wrapped in a list or another tuple first (`tuple([16])`), and a tuple literal holding one item needs its trailing comma (`("Guava",)`) or the parentheses are just parentheses.
### Hint 3
Different data, same shape. Boarding passes, where the gate code is one letter and one digit:

```python
def seat_of(booking):
    return booking[1]

def split_gate(gate):
    return tuple(gate)

seat_of(('Tess Okafor', '12B'))   # -> '12B'
split_gate('B7')                  # -> ('B', '7')
```

`seat_of` never looks at the passenger name — it only knows *where in the record* the field it wants lives.
