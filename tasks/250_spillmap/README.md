---
title: flood fill — the area a spill actually reaches on a floor plan
difficulty: medium
tier: core
minutes: 18
prereqs: [243]
tags: [graphs, deque]
---
# flood fill — the area a spill actually reaches on a floor plan

*The same breadth-first walk as a graph, except the neighbours are the four cells around you and the edge of the grid is a wall you have to write yourself.*

## Read first
- [`collections.deque`](https://devdocs.io/python~3.14/library/collections#collections.deque) — the queue of cells still to look at
- [Lists](https://devdocs.io/python~3.14/tutorial/introduction#lists) — and negative indexing, which is exactly what makes an unchecked `col - 1` dangerous here
- [`str.join`](https://devdocs.io/python~3.14/library/stdtypes#str.join) — strings cannot be edited in place, so the working copy is a list of lists

## Why
A drum has split on the warehouse floor. The floor plan is a grid: open floor, and racking that liquid will not cross. Before anyone is sent in with absorbent, the shift lead wants the plan back with the affected area shaded, because that is what decides how many bags to fetch and which aisles to close. It is the same question a paint bucket tool answers, and the same one a map answers about which land a flood reaches.

## You get
- `floor` — the plan, as a list of equal-length strings. `.` is open floor and `#` is racking, like `["..#.", "####"]`.
- `start` — a `(row, col)` tuple, where the drum split.

## You return
a new list of strings: the same plan with every cell the spill reaches written as `~`.

## Rules
- The spill spreads up, down, left and right. Not diagonally — a corner touching a corner is not a way through.
- It never crosses a `#`, and it never leaves the plan.
- Leave `floor` exactly as you were given it and return a new list.
- When `start` is on racking, nothing spreads: return the plan unchanged.

```python
solve(["...", ".#.", "..."], (0, 0))   # -> ["~~~", "~#~", "~~~"]
solve([".#", "#."], (0, 0))            # -> ["~#", "#."]
```

> [!WARNING]
> `floor[row][col - 1]` when `col` is `0` reads `floor[row][-1]`, the far end of the same row, and Python raises nothing. A spill against the left wall quietly appears on the right wall, and the same happens up the top edge into the bottom row. Check both bounds yourself, before you index anything.

> [!NOTE]
> Strings do not support item assignment. Take a working copy with `[list(line) for line in floor]`, mark cells in that, and join the rows back into strings at the end — which also means the plan you were handed is never touched.

## Hints
### Hint 1
Mark the start cell, put it on a queue, and then keep taking a cell off and looking at its four neighbours. A neighbour that is inside the grid and still `.` gets marked and queued.
### Hint 2
Mark a cell the moment you queue it, not when you take it off. The mark is what stops the same cell being queued by each of its neighbours in turn, so no separate "seen" structure is needed at all.
### Hint 3
The same walk, counting the cells of one lake on a terrain grid:

```python
from collections import deque

def lake_size(grid, start):
    cells = [list(line) for line in grid]
    height, width = len(cells), len(cells[0])
    row, col = start
    if cells[row][col] != "~":
        return 0
    cells[row][col] = "x"
    queue, size = deque([(row, col)]), 1
    while queue:
        row, col = queue.popleft()
        for r, c in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
            if 0 <= r < height and 0 <= c < width and cells[r][c] == "~":
                cells[r][c] = "x"
                queue.append((r, c))
                size += 1
    return size
```

The four-tuple of neighbours is the only line that would change for a diagonal spread, and `0 <= r < height` is the line that keeps the walk on the map.
