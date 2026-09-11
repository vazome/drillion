---
title: longest increasing subsequence — the longest run of genuine improvement
difficulty: medium
tier: advanced
minutes: 20
prereqs: [19, 188]
tags: [dynamic-programming, loops]
---
# longest increasing subsequence — the longest run of genuine improvement

*The best nights do not have to be consecutive: how many measurements can you keep, in the order they were taken, with every one better than the last?*

## Read first
- [`enumerate()`](https://devdocs.io/python~3.14/library/functions#enumerate) — you need the position as well as the value, because only earlier readings may come before this one
- [`max()`](https://devdocs.io/python~3.14/library/functions#max) — and its `default=` argument, for the case where nothing earlier qualifies
- [Generator expressions](https://devdocs.io/python~3.14/tutorial/classes#generator-expressions) — scanning the readings before this one without building a list to throw away

## Why
A nightly benchmark records one number per run and the numbers bounce: a noisy neighbour, a cold cache, a run that landed on a slower machine. Somebody asks whether the last quarter was actually a story of improvement, and "it went up 41 times and down 39" tells them nothing. The honest measure is the longest chain of runs, in the order they happened, where each one beat the one before it. It ignores the bad nights instead of averaging them away, and it is the same shape of question as the longest chain of versions where each is compatible with the last, or the most jobs you can keep from a schedule you are not allowed to reorder.

## You get
`readings` — a list of `int`, one per run, in the order the runs happened, e.g. `[10, 22, 9, 33, 21, 50]`. It may be empty, values may repeat, and it may go steadily downhill.

## You return
an `int` — how many readings the longest improving chain contains.

## Rules
Keep some of the readings and drop the rest. What you keep has to stay in the order it was recorded, and each kept reading has to be **strictly** greater than the kept reading before it. Return the size of the largest such selection.

- An empty `readings` is `0`.
- Readings that only ever go down give `1` — a single reading is a chain of one.
- Equal readings are not an improvement: `[5, 5, 5]` is `1`, not `3`.

```python
solve([10, 22, 9, 33, 21, 50, 41, 60, 80])   # -> 6   (10, 22, 33, 41, 60, 80)
solve([4, 8, 7, 5, 1, 12, 2, 3, 9])          # -> 4   (1, 2, 3, 9)
solve([9, 8, 7, 6, 5])                       # -> 1
solve([])                                    # -> 0
```

> [!WARNING]
> This is not the longest *run of consecutive* improving readings. The chain is allowed to step over any number of readings, and on the first example the longest consecutive run is `41, 60, 80` — three — while the answer is six. The generated series are noisy on purpose, so the consecutive answer is wrong on nearly every one of them.

> [!NOTE]
> Forty readings is a comfortable double loop. Trying every subset is a trillion.

## Hints
### Hint 1
Ask a smaller question, once per reading: *how long is the best chain that **ends** at this reading?* The answer for the whole series is then the largest of those, and the empty series has none at all — which is where `max(..., default=0)` earns its keep.
### Hint 2
The chain ending at reading `i` is `1` plus the best chain ending at some earlier reading that is smaller than `readings[i]`. So keep the per-reading answers in a list as you go, and to fill in position `i` you look back over the positions you have already filled.
### Hint 3
Same shape, on words getting longer instead of numbers getting bigger:

```python
words = ["ox", "cat", "ax", "bird", "eagle", "hen"]
best = []
for i, word in enumerate(words):
    best.append(1 + max((best[j] for j in range(i) if len(words[j]) < len(word)), default=0))
print(best)             # [1, 2, 1, 3, 4, 3]
print(max(best))        # 4   -> ox, cat, bird, eagle
```

Each entry is read only from entries to its left, which is why one forward pass is enough.
