---
title: two-colouring — can these jobs be split across two pools
difficulty: medium
tier: advanced
minutes: 18
prereqs: [243]
tags: [graphs, deque]
---
# two-colouring — can these jobs be split across two pools

*Give the first job a pool, give every job it clashes with the other pool, and keep going until either everything is placed or two neighbours end up together.*

## Read first
- [`collections.deque`](https://devdocs.io/python~3.14/library/collections#collections.deque) — the queue the colouring spreads along
- [Mapping types — dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — one dict does double duty: which pool a job is in, and whether it has been placed at all
- [`sorted`](https://devdocs.io/python~3.14/library/functions#sorted) — the answer is two sorted lists

## Why
Nightly batch jobs run on two worker pools, and some pairs cannot run at the same time — the backup and the vacuum both want the same table lock, the reindex and the purge fight over disk. Ops keeps a list of which pairs clash. The question before every schedule change is whether the jobs can be dealt into the two pools at all, and it has a real answer: sometimes three jobs all clash with each other and no split exists, and the honest reply is to buy a third pool rather than to keep shuffling.

## You get
`conflicts` — a dictionary mapping each job name to the sorted list of jobs it must not share a pool with, like `{"backup": ["purge"], "purge": ["backup"], "sync": []}`. Every job is a key, and every clash is listed from **both** sides.

## You return
a tuple of two lists, `(pool_a, pool_b)`, each sorted, together holding every job exactly once. `None` when no split works.

## Rules
- A job with no clashes still has to land in a pool.
- The clashes can describe several separate groups of jobs, and a group that never touches another one is placed independently of it.
- Which pool is which would otherwise be arbitrary, so fix it: walk the jobs in **sorted** order, and the first job of each group that is still unplaced goes in `pool_a`.
- An empty schedule returns `([], [])`, not `None`.

```python
solve({"backup": ["purge"], "purge": ["backup"], "sync": ["export"], "export": ["sync"], "idle": []})
# -> (["backup", "export", "idle"], ["purge", "sync"])

solve({"backup": ["purge", "sync"], "purge": ["backup", "sync"], "sync": ["backup", "purge"]})
# -> None
```

> [!WARNING]
> Placing every unplaced neighbour in the opposite pool is only half the job. The half that catches the impossible schedules is checking the neighbours that are **already placed**: if one of them sits in the same pool as the job you are standing on, there is no split and the answer is `None`. Leave that check out and the three-way clash above comes back as a tidy pair of pools that would deadlock on the first night.

## Hints
### Hint 1
One dict, `pools`, maps a job to `0` or `1`. A job missing from it has not been placed yet, so you do not need a second "visited" structure.
### Hint 2
For each job in sorted order that is not yet placed, put it in pool `0` and spread out from it with a queue. For each neighbour: if it is unplaced, place it in `1 - pools[job]` and queue it; if it is already placed in the *same* pool as `job`, give up and return `None`.
### Hint 3
The same two-colouring, deciding whether a set of people can be seated at two tables:

```python
from collections import deque

def split(dislikes):
    tables = {}
    for first in sorted(dislikes):
        if first in tables:
            continue
        tables[first] = 0
        queue = deque([first])
        while queue:
            person = queue.popleft()
            for other in dislikes[person]:
                if other not in tables:
                    tables[other] = 1 - tables[person]
                    queue.append(other)
                elif tables[other] == tables[person]:
                    return None
    return tables
```

The outer loop is what handles a room where two groups of friends have never met: each one starts its own colouring.
