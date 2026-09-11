---
title: Dijkstra with heapq — the cheapest route when the legs have prices
difficulty: hard
tier: advanced
minutes: 22
prereqs: [174]
tags: [graphs, heapq]
source: TheAlgorithms/Python graphs/dijkstra.py (MIT, adapted)
---
# Dijkstra with heapq — the cheapest route when the legs have prices

*A heap hands you the cheapest place you have not settled yet, and the first time it hands you the destination, that price is the answer.*

## Read first
- [`heapq`](https://devdocs.io/python~3.14/library/heapq) — `heappush` and `heappop` keep the smallest item at the front for far less than re-sorting
- [Sequence types](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — tuples compare left to right, which is why `(cost, name)` on a heap orders by cost
- [Set types](https://devdocs.io/python~3.14/library/stdtypes#set) — the settled set, and why an item is checked when it comes off the heap

## Why
Freight moves between depots, and every leg has a price a carrier quoted. Sales wants to know what it costs to get a pallet from Hamburg to Turin, and the answer is not the leg that goes straight there — that one is expensive because it is direct. Two short legs through Porto often beat it. With eight depots you can add the routes up by hand; with the eighty the network actually has, and prices that change weekly, you cannot.

## You get
- `legs` — a dictionary mapping each depot to a list of `(depot, price)` tuples, the legs leaving it, like `{"hamburg": [("lyon", 10), ("porto", 1)], "porto": [("lyon", 1)], "lyon": []}`. Every depot named anywhere is a key.
- `start` — the depot the pallet is at.
- `target` — the depot it has to reach.

## You return
the total price of the cheapest route, as a number. `None` when no sequence of legs gets there.

## Rules
- Legs go one way, and every price is a positive whole number.
- The answer is the price, not the route.
- `start` and `target` can be the same depot, and then the price is `0`.

```python
legs = {
    "hamburg": [("lyon", 10), ("porto", 1)],
    "porto": [("lyon", 1)],
    "lyon": [("turin", 1)],
    "turin": [],
}
solve(legs, "hamburg", "lyon")    # -> 2, not 10
solve(legs, "hamburg", "turin")   # -> 3
solve(legs, "turin", "hamburg")   # -> None
```

> [!WARNING]
> The trap is *when* a depot counts as settled. Marking it the moment you push it onto the heap means the first price you happened to find for it is the price it keeps — and in the example above that answers `11` for Turin instead of `3`, because the ten-euro leg to Lyon was pushed before the cheap pair was found. A depot is settled when it comes **off** the heap, never when it goes on.

> [!NOTE]
> The same depot can sit on the heap several times at different prices, and that is fine. The dearer copies come off later, and by then the depot is already settled, so you skip them. Nothing has to be removed from the middle of a heap.

## Hints
### Hint 1
Push `(0, start)` and loop while the heap is not empty. Pop the cheapest pair. If that depot is already settled, ignore it and pop again. If it is the target, its price is the answer. Otherwise settle it and push `(cost + price, next_depot)` for each leg leaving it.
### Hint 2
Put the cost first in the tuple. A heap compares whole tuples, so `(3, "turin")` sorts before `(11, "lyon")` on price alone, and the depot name only ever breaks a tie.
### Hint 3
The same loop, over tasks that unlock each other with a delay:

```python
import heapq

def earliest(after, start, wanted):
    settled, heap = set(), [(0, start)]
    while heap:
        clock, task = heapq.heappop(heap)
        if task in settled:
            continue
        if task == wanted:
            return clock
        settled.add(task)
        for nxt, delay in after[task]:
            if nxt not in settled:
                heapq.heappush(heap, (clock + delay, nxt))
    return None
```

Falling out of the `while` means the heap emptied without ever reaching `wanted`, which is the unreachable case.

---
Adapted from TheAlgorithms/Python — MIT
