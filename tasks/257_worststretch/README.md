---
title: Kadane's scan — the worst stretch in a series of deltas
difficulty: hard
tier: advanced
minutes: 22
prereqs: [19, 188]
tags: [dynamic-programming, loops]
---
# Kadane's scan — the worst stretch in a series of deltas

*One pass, three numbers carried along: what the run so far adds up to, where it started, and the worst one you have seen.*

## Read first
- [`enumerate()` and `range()`](https://devdocs.io/python~3.14/library/functions#func-range) — walking the readings once, with the index you will have to report
- [`sum()` and slicing](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — `sum(deltas[start:end + 1])`, which is what your answer has to agree with
- [Tuples](https://devdocs.io/python~3.14/library/stdtypes#tuple) — returning three values as one
- [Assignment to a tuple of targets](https://devdocs.io/python~3.14/reference/simple_stmts#assignment-statements) — updating several running values in one statement, so they cannot drift apart

## Why
A capacity dashboard records the change in free disk on a volume every hour: mostly small gains as logs rotate away, and losses when something goes wrong. Nobody wants the total for the day — that is on the graph already. What the post-mortem needs is the worst *stretch*: the run of consecutive hours over which the volume lost the most, because that is the window whose deploys, cron jobs and traffic you go and read. The naive answer adds up the hours that dropped and ignores the rest, which invents a stretch that never happened: an hour that gained a little in the middle of a bad afternoon is part of the bad afternoon. The honest answer is a contiguous run, and on a good day, when every hour gained, it is the single hour that gained the least.

## You get
`deltas` — the hourly changes, a list of `int`, oldest first. A positive number is free space gained, a negative number is space lost. There is always at least one reading. The test creates it and hands it to you; you never build it yourself.

## You return
a tuple `(start, end, total)` — the first and last index of the worst stretch, **both included**, and what it sums to.

## Rules
`total` is the smallest sum any contiguous run of `deltas` reaches, and `start`/`end` are that run.

- `sum(deltas[start:end + 1]) == total`. The run is contiguous, and `end` is part of it.
- A run of one reading is a run. There is no empty run, so when every reading is positive the answer is the smallest single reading and its index, never `0`.
- **Ties are decided for you.** More than one run often reaches the same total, so: the **earliest** `start` wins, and among runs with that start the **shortest** one wins.

```python
solve([2, -8, 3, -2, 4, -10])   # -> (1, 5, -13)
solve([3, 1, 2])                # -> (1, 1, 1)
solve([0, 0, 0])                # -> (0, 0, 0)
solve([-4, 6, -1, -1, 6, -4])   # -> (0, 0, -4)
```

> [!WARNING]
> Starting the worst-total-so-far at `0` is the near-miss, and it is invisible until a day when nothing goes wrong: on `[3, 1, 2]` it reports a total of `0` for a stretch that does not exist. Roughly one generated series in five gains in every single hour, so that answer fails. Start from the first reading instead of from nothing.

> [!NOTE]
> Trying every `start` and `end` is two nested loops and is correct. One pass is the same answer, and the reason it works is worth having: a run that has crept back above zero can never help the run that follows it.

## Hints
### Hint 1
Walk the readings once and carry the sum of the run you are currently in. At each new reading you have exactly two choices: extend the run you are in, or throw it away and start a fresh run here. Throwing it away is right whenever what you are carrying is a gain, because a positive carried forward only makes the next stretch look better than it was.
### Hint 2
That is three things to keep in step: the running sum, the index the running run started at, and the worst `(start, end, total)` you have seen. Update all three in the same pass, and record the worst only when the running sum is **strictly** less than it — strictly is what implements both tie rules, the earliest start and the shortest run. Seed everything from `deltas[0]` at index `0` so the answer is never an empty run.
### Hint 3
The same scan without the indices, so the shape is visible:

```python
def worst_total(deltas):
    total = run = deltas[0]
    for delta in deltas[1:]:
        run = delta if run > 0 else run + delta
        total = min(total, run)
    return total

worst_total([2, -8, 3, -2, 4, -10])   # -13
worst_total([3, 1, 2])                # 1
```

`run = delta if run > 0 else run + delta` is the whole decision. Adding the index bookkeeping around it is the rest of the task: the run's start moves only when the run restarts, and the answer's start and end move only when `total` does.
