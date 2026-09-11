---
title: breadth-first search — the fewest hops between two services
difficulty: medium
tier: core
minutes: 15
prereqs: [60]
tags: [graphs, deque]
---
# breadth-first search — the fewest hops between two services

*Walk a graph one ring at a time and the first time you meet a node, you got there the short way.*

## Read first
- [`collections.deque`](https://devdocs.io/python~3.14/library/collections#collections.deque) — `append` on one end, `popleft` on the other, both cheap
- [Set types](https://devdocs.io/python~3.14/library/stdtypes#set) — `in` on a set does not scan it, which is what keeps this loop from re-walking the graph
- [Mapping types — dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — the adjacency table is a plain dict of lists

## Why
A request comes into the gateway and, four services later, something answers it. When latency goes up, the first question is how many services a call actually passes through, and the second is which ones. Nobody has that written down — what the team has is a call graph scraped from tracing, service by service. Counting the hops by eye works until the graph has forty services in it, and by then the short route and the route somebody drew on a whiteboard are not the same route.

## You get
- `calls` — a dictionary mapping each service name to the list of services it calls directly, like `{"gateway": ["auth", "billing"], "auth": ["ledger"], "ledger": [], "billing": []}`. Every name that appears anywhere is a key.
- `start` — the service the request arrives at.
- `target` — the service you want to reach.

## You return
the shortest chain of service names from `start` to `target`, including both ends, as a list. An empty list when no chain of calls gets there.

## Rules
- Calls go one way. `"gateway": ["billing"]` means the gateway calls billing, not the other way round.
- The chain has to be the shortest one there is. When two chains are equally short, either is accepted.
- `start` and `target` can be the same service, and then the answer is `[start]` — no hops needed to reach yourself.

```python
calls = {"gateway": ["auth", "billing"], "auth": ["ledger"], "ledger": ["billing"], "billing": []}
solve(calls, "gateway", "billing")   # -> ["gateway", "billing"]
solve(calls, "gateway", "ledger")    # -> ["gateway", "auth", "ledger"]
solve(calls, "billing", "gateway")   # -> []
```

> [!WARNING]
> Following the first call out of each service until you land on the target finds *a* chain, not the shortest one. In the example above that route is `gateway -> auth -> ledger -> billing`, four names for a call the gateway makes directly. The test compares the length of your chain, so a longer valid route fails.

> [!NOTE]
> Mark a service as seen when you put it on the queue, not when you take it off. Otherwise the same service goes on the queue once per neighbour that names it, and a graph with a hub in it does a lot of pointless work.

## Hints
### Hint 1
A queue is what makes this breadth-first. Take the front item, push everything it leads to onto the back, and the queue drains in order of distance from the start: everything one hop away, then everything two hops away, and so on. `deque` gives you `popleft` for the front and `append` for the back.
### Hint 2
The queue can hold whole chains instead of single names — start it with `[[start]]`, and each neighbour extends the chain you just took off. The last name in a chain is the service you are standing on.
### Hint 3
The same shape, over rooms instead of services:

```python
from collections import deque

def nearest_exit(doors, start):
    seen, queue = {start}, deque([[start]])
    while queue:
        path = queue.popleft()
        for room in doors[path[-1]]:
            if room == "outside":
                return [*path, room]
            if room not in seen:
                seen.add(room)
                queue.append([*path, room])
    return []
```

The `seen` set is what stops a cycle from looping forever, and the check on `room` is what stops the search the moment the answer is known.
