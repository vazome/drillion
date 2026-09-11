---
title: depth-first search — which machines can still reach each other
difficulty: medium
tier: advanced
minutes: 15
prereqs: [51]
tags: [graphs, sets]
---
# depth-first search — which machines can still reach each other

*Walk out from one machine as far as the links go, and what you have visited is one island.*

## Read first
- [Set types](https://devdocs.io/python~3.14/library/stdtypes#set) — a `seen` set is the whole trick: it turns "have I been here" into one cheap check
- [More on lists](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists) — `append` and `pop` make a list a stack, which is all depth-first search needs
- [`sorted`](https://devdocs.io/python~3.14/library/functions#sorted) — sorting a list of lists compares them element by element

## Why
A network change went out and half the fleet went quiet. The peering table says which machines have a link to which, and what the team needs before it can page anybody is the shape of the damage: is this one big network still, or has it broken into islands that can no longer see each other? A machine that has ended up alone matters as much as a group of six, because it is the one still accepting writes nobody else will ever read.

## You get
`peers` — a dictionary mapping each machine name to the list of machines it has a link with, like `{"db-01": ["db-02"], "db-02": [], "web-01": []}`. Every machine in the fleet is a key, including the ones with no links at all.

## You return
the islands, as a list of lists. Each island is the sorted list of the machine names in it, and the islands themselves are in order of their first name.

## Rules
- A link works **both ways**, but the table records each one only once, from whichever side registered it. `{"db-02": [], "db-01": ["db-02"]}` is one island of two machines, not two islands of one.
- A machine with an empty list and nobody pointing at it is an island of one, and it belongs in the answer.
- An empty fleet has no islands: return `[]`.

```python
solve({"cache-b": [], "cache-a": ["cache-b"], "edge-1": []})
# -> [["cache-a", "cache-b"], ["edge-1"]]
```

> [!WARNING]
> Walking only the names in `peers[machine]` reads the table as one-way traffic. It happens to give the right answer when the walk starts on the side that registered the link, and the wrong one when it starts on the other side — so it passes the first case you try by luck. Build the two-way view first, then walk it.

## Hints
### Hint 1
Turn the table into a symmetric one before you walk anything: a dict from each machine to a **set** of its neighbours, filled in from both ends of every link. That is a handful of lines and every question after it becomes easy.
### Hint 2
Then it is one loop over the machines. If a machine is already in `seen`, skip it; otherwise push it on a stack and keep popping until the stack is empty, collecting every machine you reach. Everything collected in one drain of the stack is one island.
### Hint 3
The same walk, over folders that link to each other:

```python
def reachable(links, start):
    seen, stack, found = {start}, [start], []
    while stack:
        node = stack.pop()
        found.append(node)
        for nxt in links[node]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return found
```

Adding to `seen` at push time rather than at pop time is what keeps a node from being queued twice by two of its neighbours.
