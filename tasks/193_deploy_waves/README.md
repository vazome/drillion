---
title: topological sort — group deploys into parallel waves
difficulty: medium
tier: core
minutes: 24
prereqs: [50, 103, 162]
tags: [collections, defaultdict-list, topological-sort]
---
# topological sort — group deploys into parallel waves

*Turn dependency order into the batches that can start together.*

## Read first
- [defaultdict](https://devdocs.io/python~3.14/library/collections#collections.defaultdict) — collect every service a dependency unlocks
- [deque](https://devdocs.io/python~3.14/library/collections#collections.deque) — consume the current ready wave
- [Topological sorting](https://en.wikipedia.org/wiki/Topological_sorting) — remove nodes whose incoming edges are cleared

## Why
A legal startup order is useful, but a deployment system also needs to know what can run at the same time. Every service with no unmet dependency belongs in one wave; clearing that whole wave reveals the next.

## You get
`graph`, mapping each service to the services it depends on. Every dependency also appears as a key.

## You return
A list of alphabetically sorted waves. Return `[]` when a cycle prevents all services from being scheduled.

```python
solve({"db": [], "api": ["db"], "web": ["api"], "jobs": ["db"]})
# -> [["db"], ["api", "jobs"], ["web"]]
```

## Rules
Use `defaultdict(list)` for the reverse edges and a `deque` for ready services. Process the whole deque as one wave before adding newly ready services. Sort each next wave so output is deterministic. If the number emitted is smaller than the graph, a cycle remains.

## Hints
### Hint 1
Keep two views: `waiting[service]` is its unmet count; `unlocks[dependency]` lists the services whose count drops when that dependency finishes.
### Hint 2
Start the deque with every zero-count service. Copy it to a wave, clear it, and only then walk the wave to build the next one.
### Hint 3
For each finished service, decrement every name in `unlocks[service]`. Append a name to the next wave exactly when its count reaches zero. Compare the total emitted names with `len(graph)` at the end.
