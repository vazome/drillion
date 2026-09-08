---
title: match — score a throw of dice against twelve categories
difficulty: medium
tier: core
minutes: 15
prereqs: [49, 172]
tags: [match, counter]
source: exercism/python practice/yacht (MIT, adapted)
---
# match — score a throw of dice against twelve categories

*Twelve rules, twelve `case` lines, and the counting is the same three calls for most of them.*

## Read first
- [match statements](https://devdocs.io/python~3.14/tutorial/controlflow#match-statements) — matching a plain value is the first thing the tutorial shows, and it is all this task needs
- [collections.Counter](https://devdocs.io/python~3.14/library/collections#collections.Counter) — `most_common` answers "how many of the commonest" in one call

## Why
Scoring is dispatch: one input, a fixed set of named rules, one number out. You have written this shape before as a chain of `if category == ...`, and it is where the repeated `category ==` starts to hide the rule that actually differs. A scoring table is the cleanest version of the problem, because the rules are genuinely unrelated to each other, so nothing can be factored out and the only thing left to get right is the dispatch. Task 172 matched on the shape of a dict; this one matches on a plain value, which is the other half of `match`.

## You get
`dice` — five whole numbers from 1 to 6, in any order, like `[3, 3, 5, 3, 3]`.
`category` — one of the twelve names below, as an uppercase string.

The test creates them and hands them to you; you never build them yourself.

## You return
the score, a whole number. `0` is a real score, not an error.

## Rules
Score the five dice for the named category.

| category | score |
| --- | --- |
| `"YACHT"` | `50` when all five dice are the same, otherwise `0` |
| `"ONES"` | the number of dice showing 1 |
| `"TWOS"` | twice the number of dice showing 2 |
| `"THREES"` | three times the number showing 3 |
| `"FOURS"` | four times the number showing 4 |
| `"FIVES"` | five times the number showing 5 |
| `"SIXES"` | six times the number showing 6 |
| `"FULL_HOUSE"` | the sum of all five dice when they are three of one number and two of another, otherwise `0` |
| `"FOUR_OF_A_KIND"` | four times that number when at least four dice are the same, otherwise `0` |
| `"LITTLE_STRAIGHT"` | `30` when the dice are 1-2-3-4-5 in any order, otherwise `0` |
| `"BIG_STRAIGHT"` | `30` when the dice are 2-3-4-5-6 in any order, otherwise `0` |
| `"CHOICE"` | the sum of all five dice |

```python
solve([5, 5, 5, 5, 5], "YACHT")           # -> 50
solve([1, 1, 1, 3, 5], "ONES")            # -> 3
solve([2, 2, 4, 4, 4], "FULL_HOUSE")      # -> 16
solve([6, 6, 6, 6, 3], "FOUR_OF_A_KIND")  # -> 24
solve([3, 3, 3, 3, 3], "FULL_HOUSE")      # -> 0
```

> [!WARNING]
> Five of a kind is **not** a full house: three of one number and two of *another*. But five of a kind **is** four of a kind, and scores four times that number, not five.

## Hints
### Hint 1
One `match category:` with twelve `case` lines. Each `case` is a plain string literal, which matches when the value is equal, and several of them can share one body by writing them as one pattern separated by `|`. The six number categories are the same rule with a different digit, so they are the one place worth collapsing.
### Hint 2
`Counter(dice)` turns the throw into number-to-how-many, and `counts.most_common(1)[0]` gives the commonest number and its count as a pair. Yacht is "the commonest count is 5", four of a kind is "the commonest count is at least 4", full house is "the sorted counts are exactly `[2, 3]`", and both straights are `sorted(dice) == [1, 2, 3, 4, 5]` or `[2, 3, 4, 5, 6]`.
### Hint 3
Different data — a shipping-rate table with the same dispatch shape:

```python
from collections import Counter

def rate(parcels, service):
    counts = Counter(p["size"] for p in parcels)
    match service:
        case "STANDARD" | "ECONOMY":
            return len(parcels) * 3
        case "BULK":
            return sum(n for size, n in counts.items() if size == "L")
        case "SAME_DAY":
            top, how_many = counts.most_common(1)[0]
            return 40 if how_many >= 4 else 0
        case _:
            return 0

print(Counter([3, 3, 5, 3, 3]).most_common(1))   # [(3, 4)]
print(sorted(Counter([2, 2, 4, 4, 4]).values()))  # [2, 3]  <- a full house
```

`case _:` at the end is not needed here, because the test only ever passes one of the twelve names. Leaving it out is fine; adding it costs nothing.
