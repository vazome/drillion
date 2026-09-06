---
title: loops — find the cells that win their row and lose their column
difficulty: medium
tier: core
minutes: 20
prereqs: [32]
tags: [loops]
source: exercism/python practice/saddle-points (MIT, adapted)
---
# loops — find the cells that win their row and lose their column

*saddle-points — two aggregates computed once, then one pass over the grid.*

## Read first
- [zip()](https://devdocs.io/python~3.14/library/functions#zip) — `zip(*matrix)` hands you the columns, which is how you get the column minima without a second nested loop
- [max() and min()](https://devdocs.io/python~3.14/library/functions#max) — one call per row and per column, computed once and reused
- [enumerate()](https://devdocs.io/python~3.14/library/functions#enumerate) — indexes alongside values, so the `+ 1` for one-based numbering happens in one place
- [any()](https://devdocs.io/python~3.14/library/functions#any) — the irregularity check is one `any` over the row lengths
- [Raising exceptions](https://devdocs.io/python~3.14/tutorial/errors#raising-exceptions) — the guard clauses at the top of the function

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A grid of numbers arrives — latency per host per hour, cost per team per month — and someone asks for the cells that are extreme in two directions at once. The obvious code recomputes the row maximum and the column minimum inside the innermost loop, which is why the report that was instant on the test fixture takes a minute on real data. Computing each aggregate once and then looking it up is the fix, and it is the same fix as caching a per-group total instead of re-querying it per row. The second half of the task is the other half of the job: refusing input that is not actually a rectangle, loudly, before you index into it.

## You get
`matrix` — a list of rows, each row a list of integers:

```python
[[9, 8, 7],
 [5, 3, 2],
 [6, 6, 7]]
```

It may be `[]`, it may be a single row or a single column, and it may be irregular — rows of different lengths — which is an error.

> [!NOTE]
> Exercism's stub is `def saddle_points(matrix)`. Here the function is `solve(matrix)`; nothing else about the task changes.

## You return
A `list` of `dict`, one per saddle point, each with exactly the keys `"row"` and `"column"`, counting from **1**:

```python
solve([[9, 8, 7], [5, 3, 2], [6, 6, 7]])  # -> [{"row": 2, "column": 1}]
solve([])                                 # -> []
```

The order of the list does not matter — the grader sorts both sides before comparing.

## Rules
- a cell is a saddle point when it is **the largest** value in its row **and the smallest** value in its column
- ties count: if a row's maximum appears three times, all three cells can qualify
- rows and columns are numbered from 1, not from 0
- an empty matrix gives `[]`, and so does a matrix with no saddle points
- if the rows are not all the same length, raise `ValueError("irregular matrix")` — check this before looking for points

```python
solve([[4, 5, 4], [3, 5, 5], [1, 5, 4]])
# -> [{"row": 1, "column": 2}, {"row": 2, "column": 2}, {"row": 3, "column": 2}]

solve([[2, 5, 3, 5]])          # -> [{"row": 1, "column": 2}, {"row": 1, "column": 4}]
solve([[2], [1], [4], [1]])    # -> [{"row": 2, "column": 1}, {"row": 4, "column": 1}]
solve([[1, 2, 3], [3, 1, 2], [2, 3, 1]])   # -> []
solve([[3, 2, 1], [0, 1], [2, 1, 0]])      # raises ValueError("irregular matrix")
```

> [!WARNING]
> The message is compared character for character: `irregular matrix`, lower case, no full stop. And `[]` is *not* irregular — an empty matrix is a valid input that returns `[]`, so the emptiness check has to come first or your indexing of `matrix[0]` will raise `IndexError` instead.

## Hints
### Hint 1
Write the two guards first — empty matrix, then irregular matrix — and get them out of the way, because everything after them can assume a rectangle. Then convince yourself of one thing before writing the search: how many times does a naive version compute `max(row)`? Once per cell in the row, when once per row would do.
### Hint 2
Build two small lists up front: the maximum of each row, and the minimum of each column. `zip(*matrix)` gives you the columns as tuples, so the second list is as short as the first. Then a cell at row `r`, column `c` is a saddle point exactly when the row maximum and the column minimum are the same number — you do not even have to look at the cell's own value to know that, because a value that equals both must be the cell's value. Collect `{"row": r + 1, "column": c + 1}` for every pair that matches.
### Hint 3
Different data, same "precompute the aggregates, then one pass" shape — flagging cells in a latency grid that are the worst hour for their host and the best host for their hour:

```python
grid = [[90, 120, 80],
        [70, 120, 60]]

worst_per_host = [max(row) for row in grid]        # -> [120, 120]
best_per_hour = [min(col) for col in zip(*grid)]   # -> [70, 120, 60]

flagged = [(host + 1, hour + 1)
           for host, _ in enumerate(grid)
           for hour, _ in enumerate(grid[0])
           if worst_per_host[host] == best_per_hour[hour]]
flagged   # -> [(1, 2), (2, 2)]
```

Two list comprehensions, two aggregates, then a single scan that only does comparisons. Swap `max`/`min` around and you have the "best hour for its host, worst host for its hour" report, with no change to the shape.
