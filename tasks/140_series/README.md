---
title: sequences — every window of n digits, in order
difficulty: medium
tier: core
minutes: 15
prereqs: [88, 90, 92, 95, 97, 101]
tags: [sequences]
source: exercism/python practice/series (MIT, adapted)
---
# sequences — every window of n digits, in order

*series — the sliding window, plus four error messages that must be exact.*

## Why
A sliding window is the shape behind "the last five minutes of latency", "any three consecutive failed health checks", "every 4-byte frame in this payload". Getting the count of windows right — and it is `len - n + 1`, not `len // n` and not `len - n` — is the kind of off-by-one that ships. The other half of this task is the guard clauses: four impossible inputs, four exact messages, checked before any work is done.

## Instructions
Given a string of digits, output all the contiguous substrings of length `n` in that string in the order that they appear.

For example, the string "49142" has the following 3-digit series:

- "491"
- "914"
- "142"

And the following 4-digit series:

- "4914"
- "9142"

And if you ask for a 6-digit series from a 5-digit string, you deserve whatever you get.

Note that these series are only required to occupy _adjacent positions_ in the input;
the digits need not be _numerically consecutive_.

### Exception messages

Sometimes it is necessary to [raise an exception](https://docs.python.org/3/tutorial/errors.html#raising-exceptions). When you do this, you should always include a **meaningful error message** to indicate what the source of the error is. This makes your code more readable and helps significantly with debugging. For situations where you know that the error source will be a certain type, you can choose to raise one of the [built in error types](https://docs.python.org/3/library/exceptions.html#base-classes), but should still include a meaningful message.

This particular exercise requires that you use the [raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement) to "throw" a `ValueError` if the series and/or length parameters input into the `slice()` function are empty or out of range. The tests will only pass if you both `raise` the `exception` and include a message with it.

To raise a `ValueError` with a message, write the message as an argument to the `exception` type:

```python
# if the slice length is zero.
raise ValueError("slice length cannot be zero")

# if the slice length is negative.
raise ValueError("slice length cannot be negative")

# if the series provided is empty.
raise ValueError("series cannot be empty")

# if the slice length is longer than the series.
raise ValueError("slice length cannot be greater than series length")
```

## You get
- `series` — a string of digits, e.g. `"49142"`. It may be empty.
- `length` — how long each window should be, e.g. `3`. It may be zero, negative, or longer than the series.

> [!NOTE]
> Exercism's stub is `def slices(series, length)`. Here the function is `solve(series, length)`; nothing else about the task changes.

## You return
A `list` of strings — every window of `length` characters, left to right, including overlaps and duplicates. The pieces stay **strings**; nothing is converted to `int`.

## Rules
- window `i` starts at index `i`, so the answer has `len(series) - length + 1` entries
- windows overlap: `"9142"` with `length` 2 gives `["91", "14", "42"]`, not `["91", "42"]`
- duplicates stay: `"777777"` with `length` 3 gives four identical windows
- when `length` equals `len(series)` there is exactly one window: the whole string

The four invalid inputs raise `ValueError` with exactly these messages, checked in this order:

| when | message |
| --- | --- |
| `series` is empty | `series cannot be empty` |
| `length` is 0 | `slice length cannot be zero` |
| `length` is negative | `slice length cannot be negative` |
| `length` is greater than `len(series)` | `slice length cannot be greater than series length` |

```python
solve("49142", 3)   # -> ["491", "914", "142"]
solve("12", 1)      # -> ["1", "2"]
solve("777777", 3)  # -> ["777", "777", "777", "777"]
solve("12345", 42)  # raises ValueError("slice length cannot be greater than series length")
```

> [!WARNING]
> The messages are compared character for character, lower case and without a full stop. Order matters as well: `solve("", 1)` must say `series cannot be empty`, so the empty-series check comes first.

## Read first
- [Sequence slicing](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations) — `series[start:start + length]` never raises, it just gives you a shorter piece, which is why the guard clauses have to do the rejecting
- [range()](https://docs.python.org/3/library/functions.html#func-range) — the exact set of start positions is a `range`, and getting its end right is the whole off-by-one
- [List comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) — one line once the range is right
- [Raising exceptions](https://docs.python.org/3/tutorial/errors.html#raising-exceptions) — `raise ValueError("message")` for the four rejected cases

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Write the guard clauses first and get them out of the way — four `if`s in the order given in the table, each raising immediately. After them, the input is guaranteed sane and you can think about one thing only: which index does the last window start at? Work it out on `"49142"` with `length` 3 by pointing at the characters.
### Hint 2
The last window starts at `len(series) - length`, so the start positions are `range(len(series) - length + 1)` — the `+ 1` is there because `range` stops one short. For each start, the window is `series[start:start + length]`. That is a single list comprehension. Watch the guards: slicing past the end of a string silently gives a short piece rather than an error, so if you skip the "length greater than series" check you get a wrong answer instead of a crash.
### Hint 3
Different data, same window — a rolling average over the last three samples:

```python
latencies = [100, 120, 90, 300]
size = 3
[sum(latencies[i:i + size]) / size for i in range(len(latencies) - size + 1)]
# -> [103.33333333333333, 170.0]
```

Two windows from four samples: `4 - 3 + 1`. Whenever you write a window loop, sanity-check that formula on a tiny example before you trust it.
