---
title: allergies — unpack one test score into a list of allergies
minutes: 20
prereqs: [200, 206, 209, 227, 236, 248]
tags: [exercism, core]
source: exercism/python practice/allergies (MIT, adapted)
---
# allergies — unpack one test score into a list of allergies

*allergies — one integer, eight yes/no answers, and the arithmetic that gets each one back out.*

## Why
A lab sends back a single number to say which of eight things a patient reacts to, because one number is cheap to store, cheap to send and impossible to get half-written. Every system that has ever had to record a set of on/off facts in one field does this: Unix file permissions, Linux capability masks, feature flags packed into a bitmask column, the settings byte in a network protocol. Reading such a field is a skill you need long before you ever choose to write one — and the trap is always the same, a number can carry flags your code has never heard of, and it must ignore them rather than guess.

## Instructions
Given a person's allergy score, determine whether or not they're allergic to a given item, and their full list of allergies.

An allergy test produces a single numeric score which contains the information about all the allergies the person has (that they were tested for).

The list of items (and their value) that were tested are:

- eggs (1)
- peanuts (2)
- shellfish (4)
- strawberries (8)
- tomatoes (16)
- chocolate (32)
- pollen (64)
- cats (128)

So if Tom is allergic to peanuts and chocolate, he gets a score of 34.

Now, given just that score of 34, your program should be able to say:

- Whether Tom is allergic to any one of those allergens listed above.
- All the allergens Tom is allergic to.

Note: a given score may include allergens **not** listed above (i.e. allergens that score 256, 512, 1024, etc.).
Your program should ignore those components of the score.
For example, if the allergy score is 257, your program should only report the eggs (1) allergy.

## You get
Nothing to start — you return a **class**. The grader builds it as `Allergies(score)`, e.g. `Allergies(34)`. `score` is a non-negative `int` and may be larger than `255`.

> [!NOTE]
> Exercism's stub is a `class Allergies` in `allergies.py`. Here the entry point is `solve()`, which takes **no arguments** and returns the class itself — not an instance.

## You return
The class. The grader uses it like this:

```python
Allergies = solve()
Allergies(34).allergic_to("peanuts")    # -> True
Allergies(34).allergic_to("eggs")       # -> False
Allergies(34).lst                       # -> ["peanuts", "chocolate"]
```

| member | is | behaviour |
| --- | --- | --- |
| `allergic_to(item)` | method | `True` or `False` — does this score include that allergen |
| `.lst` | attribute or property | a `list[str]` of every allergen in the score, in scoring order |

## Rules
- the eight allergens, in the order that matters, are `eggs`, `peanuts`, `shellfish`, `strawberries`, `tomatoes`, `chocolate`, `pollen`, `cats`, scoring `1, 2, 4, 8, 16, 32, 64, 128`
- `.lst` is read as a plain attribute — `person.lst`, no brackets — so make it either an attribute set in `__init__` or a `@property`
- `.lst` is in **scoring order**, not alphabetical order: `eggs` comes before `cats` because 1 comes before 128
- `allergic_to` must hand back a real `bool`. The grader compares with `is`, so `1` and `0` fail even though they are truthy and falsy
- `allergic_to` is only ever called with one of the eight names above, spelled exactly as listed
- any part of the score at 256 or above belongs to an allergen nobody told you about — leave it out of both answers, do not raise
- a score of `0` means no allergies: every `allergic_to` is `False` and `.lst` is `[]`

```python
Allergies = solve()
Allergies(0).allergic_to("eggs")       # -> False
Allergies(255).allergic_to("cats")     # -> True
Allergies(257).lst                     # -> ["eggs"]
Allergies(248).lst                     # -> ["strawberries", "tomatoes", "chocolate", "pollen", "cats"]
```

> [!WARNING]
> `257` is `256 + 1`. A solution that tests the score by subtracting values largest-first, or by asking "is the score equal to 128?", gets this one wrong. Each allergen has to be answered on its own, without reference to the rest of the number.

## Read first
- [Bitwise operations](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types) — `&` keeps only the bits both numbers have, `<<` slides a `1` up to the position you want
- [`bool()`](https://docs.python.org/3/library/functions.html#bool) — turning a non-zero number into the actual `True` the grader is comparing against
- [`enumerate()`](https://docs.python.org/3/library/functions.html#enumerate) — pairing each allergen with its position, which is all you need to work out its score
- [`property`](https://docs.python.org/3/library/functions.html#property) — how `.lst` can be computed on access instead of stored

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Eight allergens, and the eight scores are `1, 2, 4, 8, 16, 32, 64, 128` — each one twice the last. That doubling is the whole exercise: it means every allergen owns a different digit of the score written in base 2, so no combination of the other seven can ever add up to yours. Find the operation that asks about one digit and ignores the rest, and both members become one line.

### Hint 2
Write the eight names down **once**, in scoring order, as a class-level tuple, and never write the numbers at all — an allergen's position in that tuple already tells you its score, because position `n` scores `2 ** n`. Then: `allergic_to` looks up the item's position and asks whether the score has that one bit set, remembering to convert the result to a genuine `bool`. And `.lst` is the same question asked eight times — a comprehension over the tuple that keeps the names for which `allergic_to` says yes, which also gives you the scoring order for free and drops the 256-and-above bits without a special case, because you never look at those positions.

### Hint 3
Different data, same shape — the permission byte on a file, with its three flags written out as the plain numbers they are:

```python
FLAGS = {"execute": 1, "write": 2, "read": 4}

def granted(mode, action):
    return bool(mode & FLAGS[action])

granted(0o6, "write")      # -> True
granted(0o6, "execute")    # -> False
granted(0o644, "read")     # -> True
```

Two things to copy. First, `0o644` carries plenty of bits this table has never heard of — the group and owner digits — and no code was needed to ignore them, because `granted` only ever asks about the one bit it was handed. Second, `bool(...)` is not decoration: without it the function returns `4`, which behaves like `True` everywhere except the one place the grader looks.

What the snippet does *not* do is the part left to you: it spells its three numbers out by hand. Eight allergens spelled out by hand is eight chances to mistype a power of two — Hint 2 says where those numbers should come from instead.
