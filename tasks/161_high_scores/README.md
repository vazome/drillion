---
title: classes — a score list that answers three questions
difficulty: medium
tier: core
minutes: 20
prereqs: [35]
tags: [classes]
source: exercism/python practice/high-scores (MIT, adapted)
---
# classes — a score list that answers three questions

*high-scores — keep the raw series in the order it arrived, and answer questions with copies of it.*

## Read first
- [Sorting techniques](https://devdocs.io/python~3.14/howto/sorting) — `sorted(...)` hands back a new list; `.sort()` rewrites the one you already have
- [`max()`](https://devdocs.io/python~3.14/library/functions#max) — the highest score without sorting anything
- [Lists](https://devdocs.io/python~3.14/tutorial/introduction#lists) — negative indexing for "the last one", and slicing that is happy to be asked for more items than exist
- [A first look at classes](https://devdocs.io/python~3.14/tutorial/classes#a-first-look-at-classes) — `__init__`, `self`, and storing state on the instance

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
This is every metrics object you will ever write: something collects a series of numbers in the order they happened — request latencies, deploy durations, daily error counts — and the rest of the program asks it a small set of questions. What was the last one? What is the worst? Show me the top three. The trap is not the questions, it is that the easiest way to answer the third one is to sort, and if you sort the list you were handed, the *order it arrived in* is gone forever and the "last one" answer silently starts lying. Answering a question must not damage the data it was asked about.

## You get
Nothing to start — you return a **class**. The grader builds it as `HighScores(scores)`, where `scores` is a non-empty list of `int` scores in the order the player set them, e.g. `[30, 50, 20, 70]`.

> [!NOTE]
> Exercism's stub is a `class HighScores` in `high_scores.py`. Here the entry point is `solve()`, which takes **no arguments** and returns the class itself — not an instance.

## You return
The class. The grader uses it like this:

```python
HighScores = solve()
board = HighScores([10, 30, 90, 30, 100, 20])
board.personal_top_three()  # -> [100, 90, 30]
board.personal_best()       # -> 100
board.latest()              # -> 20
board.scores                # -> [10, 30, 90, 30, 100, 20]
```

| member | is | behaviour |
| --- | --- | --- |
| `.scores` | attribute | the list the object was built with, in the order it was given |
| `.latest()` | method | the score added last |
| `.personal_best()` | method | the highest score |
| `.personal_top_three()` | method | a list of the three highest scores, highest first |

## Rules
- `.scores` keeps the arrival order for the life of the object — asking any question must leave it exactly as it was handed over
- `latest()` is the **last** element of that list, not the largest
- `personal_top_three()` returns at most three scores, highest first; with fewer than three scores it returns all of them, still highest first
- equal scores are separate entries, not one: `[40, 20, 40, 30]` has a top three of `[40, 40, 30]`
- the score list is never empty, so you do not need a story for that case

```python
HighScores = solve()
HighScores([100, 0, 90, 30]).latest()         # -> 30
HighScores([40, 100, 70]).personal_best()     # -> 100
HighScores([20, 10, 30]).personal_top_three() # -> [30, 20, 10]
HighScores([40]).personal_top_three()         # -> [40]
```

> [!WARNING]
> The grader calls `personal_top_three()` **first** and then asks the same object for `.scores` and `.latest()`. Sorting the stored list in place passes the top-three check and fails both of the others.

## Hints
### Hint 1
Three questions, one stored list, and `__init__` has nothing to do but keep that list. Two of the three questions are a single expression each with no sorting involved at all. Only the third needs an ordering — and that is the one where you have to decide whether you are reordering the player's history or looking at a rearranged copy of it.

### Hint 2
"Latest" is a position, not a comparison, so no sorting and no `max()`: Python can index a list from the right-hand end. "Best" is one built-in applied to the whole list. For the top three, there are two ways to put a list in order and they differ in exactly the way that matters here: one returns a new list and leaves the original alone, the other rearranges the original in place and returns nothing. Take the first kind, flip it to descending with its keyword argument, and cut the front off it — a slice never complains that the list was shorter than the piece you asked for, so the "fewer than three scores" case needs no branch of its own.

### Hint 3
Different data, same shape — latency samples arriving in order, with the same "never disturb the history" rule:

```python
class Latencies:
    def __init__(self, samples):
        self.samples = samples          # arrival order, never re-sorted

    def slowest(self):
        return max(self.samples)

    def worst_three(self):
        ranked = sorted(self.samples, reverse=True)
        return ranked[:3]

readings = Latencies([12, 300, 45, 300, 7])
readings.worst_three()  # -> [300, 300, 45]
readings.samples        # -> [12, 300, 45, 300, 7]  (untouched)
readings.slowest()      # -> 300
```

`ranked` is a second list; `self.samples` never moves. Swap "latency" for "score" and the whole thing carries over.
