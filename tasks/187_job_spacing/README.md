---
title: heapq — space out a queue so no service is hit twice in a row
difficulty: hard
tier: core
minutes: 18
prereqs: [49, 174]
tags: [heapq, counter]
source: MBPP 39 (CC-BY-4.0, adapted)
---
# heapq — space out a queue so no service is hit twice in a row

*A heap is worth reaching for when "the biggest one left" changes after every step.*

## Read first
- [heapq](https://devdocs.io/python~3.14/library/heapq) — `heappush`, `heappop`, `heapify`, and the fact that the heap is a plain list
- [collections.Counter](https://devdocs.io/python~3.14/library/collections#collections.Counter) — how many of each

## Why
A batch runner holds a queue of jobs, each one calling a downstream service. Two jobs against the same service back to back trip its rate limiter, so the queue has to be reordered until no two neighbours share a service. The greedy move is obvious: always take whichever service still has the most jobs left, because that is the one that runs out of room first. What is not obvious is that "the most left" changes every single step, which is exactly the question a heap answers cheaply and a re-sort answers expensively.

## You get
`jobs` — a list of service names, one per job, in no particular order, like `["api", "db", "api"]`. The same name appears once per job it has. The test creates it and hands it to you; you never build it yourself.

## You return
a list holding the same job names in an order where no two neighbours are equal, or `[]` when no such order exists.

## Rules
Reorder `jobs` so that neighbours never share a service.

- The result holds exactly the same names, the same number of times.
- No two adjacent entries are equal.
- Return `[]` when that is impossible.
- Any valid order passes. The test checks the two rules, not one blessed answer.

```python
solve(["api", "api", "db"])          # -> ["api", "db", "api"]
solve(["api", "api"])                # -> []
solve([])                            # -> []
```

> [!WARNING]
> The trap is popping the most frequent service twice in a row. Once you have used a service, it is not allowed back until something else has run, so it has to sit **outside** the heap for exactly one step and be pushed back after the next pop. Leave it in the heap and it comes straight back out.

## Hints
### Hint 1
Count the jobs per service, then repeatedly take the service with the most left, append it, and put it back with one fewer. `heapq` is a min-heap, so store a count you want to be small when the real count is large. Hold the service you just used aside for one step instead of returning it immediately.
### Hint 2
`heap = [(-n, s) for s, n in Counter(jobs).items()]` then `heapq.heapify(heap)`. Loop while the heap is non-empty: pop, append the name, push back whatever you were holding, then hold `(count + 1, service)` if it still has jobs left. Negated counts move towards zero, so `count + 1` is one fewer job.
### Hint 3
Impossibility is the same loop telling you it got stuck: if the heap empties while jobs remain unplaced, the answer is `[]`. Different data, the same moves:

```python
import heapq
from collections import Counter

heap = [(-n, c) for c, n in Counter("aaabb").items()]
heapq.heapify(heap)
print(heap[0])                # (-3, 'a')  <- most frequent, first out
n, c = heapq.heappop(heap)
print(n, c, n + 1)            # -3 a -2    <- one 'a' used, two left
```

The arithmetic runs backwards because the counts are negative, which is the whole cost of using a min-heap as a max-heap.

Adapted from MBPP (Mostly Basic Python Problems) — CC-BY-4.0.
