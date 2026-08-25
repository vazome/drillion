---
title: hamming — how many positions do two strands differ in?
minutes: 10
prereqs: [200, 206, 209, 221, 227]
tags: [exercism, generator-expressions, raising-and-handling-errors, sequences, data-structures]
source: exercism/python practice/hamming (MIT, adapted)
---
# hamming — how many positions do two strands differ in?

*hamming — count differing positions, and refuse the comparison that makes no sense.*

## Why
When a cell divides, its DNA is copied, and copies pick up mistakes. Lay two strands side by side, count the positions where the letters disagree, and you have measured how many mistakes crept in — the Hamming distance. The same count is used far outside biology: how many bits of a checksum differ, how many fields drifted between two config versions. The second half of the job matters just as much: comparing strands of different lengths is not a small answer, it is a bug in whoever called you, so it has to fail loudly instead of quietly measuring the overlap.

## Introduction
Your body is made up of cells that contain DNA.
Those cells regularly wear out and need replacing, which they achieve by dividing into daughter cells.
In fact, the average human body experiences about 10 quadrillion cell divisions in a lifetime!

When cells divide, their DNA replicates too.
Sometimes during this process mistakes happen and single pieces of DNA get encoded with the incorrect information.
If we compare two strands of DNA and count the differences between them, we can see how many mistakes occurred.
This is known as the "Hamming distance".

The Hamming distance is useful in many areas of science, not just biology, so it's a nice phrase to be familiar with :)

## Instructions
Calculate the Hamming distance between two DNA strands.

We read DNA using the letters C, A, G and T.
Two strands might look like this:

    GAGCCTACTAACGGGAT
    CATCGTAATGACGGCCT
    ^ ^ ^  ^ ^    ^^

They have 7 differences, and therefore the Hamming distance is 7.

### Implementation notes

The Hamming distance is only defined for sequences of equal length, so an attempt to calculate it between sequences of different lengths should not work.

### Exception messages

Sometimes it is necessary to [raise an exception](https://docs.python.org/3/tutorial/errors.html#raising-exceptions). When you do this, you should always include a **meaningful error message** to indicate what the source of the error is. This makes your code more readable and helps significantly with debugging. For situations where you know that the error source will be a certain type, you can choose to raise one of the [built in error types](https://docs.python.org/3/library/exceptions.html#base-classes), but should still include a meaningful message.

This particular exercise requires that you use the [raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement) to "throw" a `ValueError` when the strands being checked are not the same length. The tests will only pass if you both `raise` the `exception` and include a message with it.

To raise a `ValueError` with a message, write the message as an argument to the `exception` type:

```python
# When the sequences being passed are not the same length.
raise ValueError("Strands must be of equal length.")
```

## You get
`strand_a`, `strand_b` — two strings of the DNA letters A, C, G and T, e.g. `"GAGCCTACTAACGGGAT"`. Either may be empty.

> [!NOTE]
> Exercism's stub is `def distance(strand_a, strand_b)`. Here the function is `solve(strand_a, strand_b)`; nothing else about the task changes.

## You return
An `int` — the number of positions at which the two strands hold different letters.

## Rules
Compare position by position: position 0 with position 0, and so on. Two empty strands differ in nothing, so the answer is 0.

If the two strands are NOT the same length, raise `ValueError` with exactly this message:

```python
raise ValueError("Strands must be of equal length.")
```

Do not return a number in that case and do not compare only the part they have in common — an empty strand against a one-letter strand is an error too.

```python
solve("GGACTGAAATCTG", "GGACTGAAATCTG")  # -> 0
solve("GGACGGATTCTG", "AGGACGGATTCT")    # -> 9
solve("AATG", "AAA")                     # -> raises ValueError
```

> [!WARNING]
> The test matches the message text, full stop included: `Strands must be of equal length.` A `ValueError` with any other wording still fails.

## Read first
- [zip()](https://docs.python.org/3/library/functions.html#zip) — `zip()` walks two sequences side by side and stops at the shorter one (which is why you must check lengths yourself)
- [Raising exceptions](https://docs.python.org/3/tutorial/errors.html#raising-exceptions) — `raise`, and why the message matters as much as the exception type
- [Generator expressions](https://docs.python.org/3/reference/expressions.html#generator-expressions) — the `(x for y in z)` form you can hand straight to `sum()`
- [Built-in exceptions](https://docs.python.org/3/library/exceptions.html#base-classes) — picking the type that says what actually went wrong

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Two jobs in one function, and the order matters: first decide whether this comparison is even legal, then do the counting. The legality test is about lengths only — nothing to do with which letters are in the strands. The Hamming distance is only defined for sequences of equal length, so an attempt to calculate it between sequences of different lengths should not work.
### Hint 2
For the guard: compare the two lengths and use the [raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement) to "throw" a `ValueError`, writing the message as an argument to the exception type — spelled exactly as the caller expects, full stop included. The tests will only pass if you both `raise` the exception and include a message with it.

For the count: `zip(a, b)` hands you the pairs one position at a time, and a comparison like `x != y` is already worth 1 when you add it up, because `True` counts as 1 — so a single `sum()` over a generator expression finishes the job.
### Hint 3
Different data, same two shapes:

```python
changed = sum(old[k] != new[k] for k in keys)   # count of drifted keys
```

and the guard you have written in every HTTP handler — validate the input, raise on nonsense, and only then do the work. Note that `zip()` silently stops at the shorter input, so without the guard you would happily return a wrong, plausible-looking number.
