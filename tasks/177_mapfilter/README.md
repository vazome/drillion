---
title: map and filter — a pipeline that stays lazy
difficulty: medium
tier: core
minutes: 12
prereqs: [5, 7]
tags: [iteration, functions]
---
# map and filter — a pipeline that stays lazy

*`map` and `filter` hand back an iterator, so nothing is computed until something asks.*

## Read first
- [map()](https://devdocs.io/python~3.14/library/functions#map) — apply a function to every item, lazily
- [filter()](https://devdocs.io/python~3.14/library/functions#filter) — keep the items a function says yes to, lazily
- [Iterators](https://devdocs.io/python~3.14/tutorial/classes#iterators) — what "an iterator, not a list" means, and why `iter(it) is it` is true for one

## Why
The log you are reading is larger than memory and the caller only wants the first few matching lines. If your function returns a list, you have already read the whole file to answer a question about its first screenful, and the caller's `break` saves nothing. Returning an iterator moves the decision to the caller: work happens per item, as they ask for it, and stopping early actually stops the work.

## You get
`lines` — an iterable of raw log lines, e.g. `["10:01 ERROR disk full", "10:02 INFO ok"]`. It may be a list, or a generator you can only walk once.

## You return
an **iterator** over the messages of the ERROR lines, in order: for `"10:01 ERROR disk full"` that is `"disk full"`.

## Rules
Keep the ERROR lines and strip them down to the message.

- A line is an ERROR line when its second word is exactly `"ERROR"`.
- The message is everything after that second word, e.g. `"10:01 ERROR disk full"` gives `"disk full"`.
- What you return must be an iterator, not a list: the test checks `iter(result) is result`, and that a caller who takes two items has caused only two lines to be read.

```python
list(solve(["10:01 ERROR disk full", "10:02 INFO ok", "10:03 ERROR conn reset"]))
# -> ["disk full", "conn reset"]
```

> [!WARNING]
> `[m for m in ...]` builds a list and fails the iterator check. A generator expression `(m for m in ...)` passes it, and so does `map`/`filter`; all three are fine, a list is not.

## Hints
### Hint 1
Two steps: drop the lines you do not want, then transform the ones you keep. `filter(keep, lines)` does the first, `map(clean, ...)` the second, and each hands its iterator to the next without walking it.
### Hint 2
`line.split(maxsplit=2)` gives at most three pieces: time, level, and the rest untouched. That is the level you test and the message you return, from one split.
### Hint 3
Different data, same shape:

```python
nums = [1, 2, 3, 4, 5, 6]
evens = filter(lambda n: n % 2 == 0, nums)
doubled = map(lambda n: n * 2, evens)
print(next(doubled), next(doubled))   # 4 8
print(iter(doubled) is doubled)       # True
```

Nothing ran until `next` asked, and only as far as it asked.
