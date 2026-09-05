---
title: topological sort — start-up order, or the cycle that blocks it
difficulty: hard
tier: core
minutes: 35
prereqs: [11, 24]
tags: [topological-sort]
---
# topological sort — start-up order, or the cycle that blocks it

*Whole-task task: what order do these services start in, and is it even possible.*

Combines topics 18 (dict lookups), 20 (defaultdict grouping), 22 (sets).

## Why
A platform has many services, and some cannot start until others are already running: the API needs the database, the cache needs the database, and so on. After a full outage someone has to bring everything back up in an order that works. If two services each wait for the other, nothing can start at all, and the team needs to know that before they try.

## You get
`graph` — a dictionary where each key is a service name and its value is a list of the services it needs running first, like `{"api": ["db", "cache"], "cache": ["db"], "db": []}`. The test builds it and hands it to you.

## You return
a dictionary with two keys: `"cycle"` (`True` when services wait on each other in a loop, otherwise `False`) and `"order"` (a list of service names in a start-up order that works, or an empty list when there is a cycle).

## Rules
`graph` maps a service to the services it depends on. Everything a service depends on has to be running before it starts. Return an order that respects that:

```python
solve({"api": ["db", "cache"], "cache": ["db"], "db": []})
# -> {"cycle": False, "order": ["db", "cache", "api"]}
```

Any order that satisfies the dependencies is accepted — the test checks the constraints, not one fixed list.

If the dependencies loop, nothing can start at all:

```python
solve({"a": ["b"], "b": ["a"]})
# -> {"cycle": True, "order": []}
```

Guarantees: every name used as a dependency is also a key, no duplicates in a dependency list, and a service with nothing to wait for has `[]`.

> [!TIP]
> This is a topological sort, but do not lead with the term. Describe what you are doing — repeatedly start whatever is unblocked — and say where the cycle shows up. Out loud.

## Hints
### Hint 1
One algorithm answers both questions. Repeatedly take any service whose dependencies are all started already, mark it started, and see what that unblocks. If you run out of unblocked services with some still left over, the leftovers are waiting on each other — that is the cycle, and you get it for free. No separate cycle hunt.
### Hint 2
Kahn's algorithm. Two structures: unmet[svc] = how many dependencies it is still waiting on, and a reverse map unblocks = defaultdict(list) where unblocks[dep] lists the services that were waiting on dep. Seed a queue with every service at zero, pop one, append it to the order, decrement each of its dependents, push the ones that hit zero. At the end, len(order) != len(graph) means a cycle.
### Hint 3
Different data, whole shape:

```python
from collections import defaultdict, deque
needs = {'cake': ['eggs', 'flour'], 'eggs': [], 'flour': []}
unmet = {k: len(v) for k, v in needs.items()}
unblocks = defaultdict(list)
for item, parts in needs.items():
    for p in parts:
        unblocks[p].append(item)
ready = deque(k for k, n in unmet.items() if n == 0)
order = []
while ready:
    item = ready.popleft()
    order.append(item)
    for nxt in unblocks[item]:
        unmet[nxt] -= 1
        if unmet[nxt] == 0:
            ready.append(nxt)
print(order)      # ['eggs', 'flour', 'cake']
```

Add the leftover check and the two return shapes and you are done.
