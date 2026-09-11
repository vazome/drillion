---
title: array — a compact buffer of signed shorts, and the readings it refuses to hold
difficulty: medium
tier: advanced
minutes: 18
prereqs: [219]
tags: [bytes, numbers]
---
# array — a compact buffer of signed shorts, and the readings it refuses to hold

*An `array` is a list that has agreed to hold one machine type, which is what makes it two bytes an item instead of eight plus an object — and what makes an out-of-range value an error rather than a bigger number.*

## Read first
- [`array`](https://devdocs.io/python~3.14/library/array) — the typecode table, `itemsize`, `append`, `frombytes`, `tobytes`
- [`OverflowError`](https://devdocs.io/python~3.14/library/exceptions#OverflowError) — what a machine type raises when a value will not fit in it
- [`bytes`](https://devdocs.io/python~3.14/library/stdtypes#bytes) — the raw form the buffer reads from and writes back to

## Why
A sensor rig reports a few million temperature deltas an hour, each one a small signed number, and the collector keeps the last hour in memory. As a list of Python ints that is a pointer per item plus an int object behind it, and the box runs out of memory long before the hour is up. `array("h", ...)` is the same numbers in two bytes each with no per-item object at all, and it appends and indexes and slices like the list it replaced. The trade is that the type is now real: a reading of `40000` is not a slightly large temperature, it is a value this buffer cannot represent, and the collector has to decide what to do with it rather than find out later that it silently became something else.

## You get
- `blob`, `bytes` written by the previous run — the raw contents of a `"h"` array, so its length is always a multiple of the item size. It can be empty.
- `readings`, a list of ints to add to it. Some of them are far outside what a signed short can hold, in both directions.

## You return
a dict with exactly three keys:

| key | value |
|---|---|
| `stored` | an `array` of typecode `"h"`: everything that was in `blob`, then every reading that fits, in order |
| `skipped` | the readings that do not fit, in the order they appeared in `readings` |
| `nbytes` | how many bytes `stored` occupies — its length times its item size |

## Rules
- `stored` is an `array.array` with typecode `"h"`, not a list. The grader checks the typecode, and a list of the same numbers is not equal to an array of them.
- A reading that does not fit is left out and recorded in `skipped`. Do not clamp it to the nearest value the type can hold: a temperature the rig could not measure must not turn into the hottest one it can.
- The range is **signed**: the negative end is as real as the positive one, and it is not symmetric with it. Reading it off the type rather than typing it in is both shorter and right.
- `skipped` is a plain list of the original ints.
- `nbytes` is computed from `stored`, so it tracks the type rather than assuming a number of bytes.

```python
solve(b"", [20, 40000, -40000, -20])
# -> {'stored': array('h', [20, -20]), 'skipped': [40000, -40000], 'nbytes': 4}
```

> [!NOTE]
> `tobytes` and the matching read-back use the **native** byte order and size of the machine that ran them, so a blob is a cache on one host, never a wire format between two. When the bytes have to travel, `struct` with an explicit `<` or `>` is the tool that says so out loud.

## Hints
### Hint 1
The array constructor takes the bytes directly: `array("h", blob)` starts you off with everything the previous run left, and an empty `blob` gives an empty array. `frombytes` does the same thing to an array you already have.
### Hint 2
You do not have to know the limits. `append` raises `OverflowError` for a value that will not fit, so a `try`/`except` around the append separates the two lists without a single number written down. If you would rather test before appending, the limits are available from the type itself rather than from memory.
### Hint 3
The parts, on a smaller type:

```python
from array import array

buf = array("b", b"\x01\x02")        # signed char: one byte, -128 to 127
buf.itemsize                          # -> 1
len(buf) * buf.itemsize               # -> 2

for value in (100, 200, -200):
    try:
        buf.append(value)
    except OverflowError:
        print("will not fit:", value)  # 200 and -200, and buf is untouched by both

list(buf)                             # -> [1, 2, 100]
buf.tobytes()                         # -> b'\x01\x02d'
array("b", buf.tobytes()) == buf       # -> True
```

An array of one typecode compares equal to an array of another when the numbers match, so the typecode is the part you have to get right deliberately.
