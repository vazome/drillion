---
title: minimum-cost path — the cheapest way across a cost map
difficulty: medium
tier: advanced
minutes: 20
prereqs: [188, 251]
tags: [dynamic-programming, lists]
---
# minimum-cost path — the cheapest way across a cost map

*Every cell knows the cheapest way to reach it, and it only has to ask the two cells that could have led there.*

## Read first
- [Nested lists](https://devdocs.io/python~3.14/tutorial/datastructures#nested-list-comprehensions) — a grid is a list of rows, and `grid[i][j]` is row `i`, column `j`
- [`min()`](https://devdocs.io/python~3.14/library/functions#min) — the cheaper of the two ways in
- [`range()`](https://devdocs.io/python~3.14/library/functions#func-range) — walking the rows and columns in the one order that has the answers you need ready
- [`list()`](https://devdocs.io/python~3.14/library/stdtypes#list) — a copy of a row, for when you must not write into the caller's

## Why
A picker in a warehouse starts at the near corner of the floor and has to reach the far one. The aisles are one-way — the conveyor runs in one direction and the racking blocks the other — so from any bay the only moves are one bay further along the aisle or one aisle across. Each bay costs a number of seconds to pass through, because some are wide and empty and some are stacked to the ceiling with a ladder in the way. The floor plan is a grid of those numbers, and the question the shift planner asks every morning is the cheapest total. The instinct is to step towards whichever neighbour is cheaper right now, which is how you end up in a cheap lane that dead-ends into the most expensive bay on the floor.

## You get
`bays` — the floor plan, a list of rows; each row is a list of positive `int` seconds, one per bay. Every row is the same length. There is at least one row and one column. The test creates it and hands it to you; you never build it yourself.

## You return
the smallest total number of seconds, as a whole number.

## Rules
You start at `bays[0][0]` and finish at `bays[-1][-1]`, and both of those bays count towards the total.

- From `bays[i][j]` the only moves are to `bays[i][j + 1]` and `bays[i + 1][j]`. Never back, never up, never diagonally.
- The cost of a path is the sum of every bay it passes through, the first and the last included.
- A single bay is its own answer: `[[7]]` is `7`.

```python
solve([[2, 1], [3, 1], [4, 2]])              # -> 6
solve([[2, 1, 4], [2, 1, 3], [3, 2, 1]])     # -> 7
solve([[1, 2, 3], [1, 100, 3], [50, 50, 1]]) # -> 10
```

> [!WARNING]
> Stepping to whichever neighbour is cheaper right now is not this. On the third example it takes the `1` below it, then the `50` below that, and pays `103` for a floor you can cross for `10`. The test carries that grid, and the generated floors each have one cheap lane and one wall, so a greedy walk fails on the first case it sees.

> [!NOTE]
> `bays` belongs to the caller. Adding running totals straight into it is the shortest way to write this and it hands back a floor plan that is no longer a floor plan — the test compares the grid before and after your call.

## Hints
### Hint 1
Ask a smaller question: what is the cheapest way to reach `bays[i][j]` at all? The only two bays that can lead there are the one to the left and the one above, so the answer is `bays[i][j]` plus the cheaper of those two answers. The top-left bay has neither, the rest of the top row only has a left, and the rest of the first column only has an above.
### Hint 2
Walk the rows top to bottom and each row left to right, and by the time you reach a bay both of the answers it needs are already worked out. You only ever need the row you are on and the row above it, so one list of running totals, updated left to right, is enough — as long as it is a copy and not the caller's row.
### Hint 3
The same shape in one dimension, where each step comes from one of the two steps behind it:

```python
def cheapest_climb(costs):
    a = b = 0
    for cost in costs:
        a, b = b, cost + min(a, b)
    return min(a, b)

cheapest_climb([10, 15, 20])         # 15
cheapest_climb([1, 100, 1, 1, 100])  # 3
```

Two rolling numbers instead of a whole table, because a step only ever asks about the two before it. The grid version is the same trick with a rolling *row*.
