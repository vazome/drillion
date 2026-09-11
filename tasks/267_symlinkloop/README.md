---
title: tortoise and hare — where a symlink chain starts looping, in two variables
difficulty: hard
tier: advanced
minutes: 22
prereqs: [48, 246]
tags: [dicts, loops]
---
# tortoise and hare — where a symlink chain starts looping, in two variables

*Two walkers at different speeds prove a loop exists; then one restart proves where it begins.*

## Read first
- [`dict.get`](https://devdocs.io/python~3.14/library/stdtypes#dict.get) — the end of the chain is a key that is not there, and `get` says so without raising
- [`while`](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — three loops, and each one stops for a different reason
- [Mapping types](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — every path has at most one target, which is the property the whole method rests on
- [`None`](https://devdocs.io/python~3.14/library/constants#None) — what a chain that terminates returns

## Why
A deploy script resolves a config path and the kernel hands back `OSError: [Errno 40] Too many levels of symbolic links`. That message is the kernel giving up after a fixed number of hops; it does not say which link is the cycle. Somebody now has to find it in a tree where `current` points at `release-42`, which points at `stable`, which points back at `current`, and the three were added by three different deploys.

What fixes the tree is knowing two things: which path the loop **starts** at — that is the link to repoint, and it is usually not the one you started resolving — and how long the loop is, which tells you how many links are in the ring. Remembering every path you have visited answers both, and costs memory that grows with the chain; on a chain of a hundred thousand generated links, inside a resolver that runs per file, that is the part you notice.

Floyd's method needs two variables. Walk one step at a time and two steps at a time from the same start: if the chain ends, the fast walker runs off the end and there is no loop. If it loops, the fast walker laps the slow one and they land on the same path. Where they land is not the start of the loop — but it is exactly the right distance from it, and one more walk turns that into the answer.

## You get
- `links` — a `dict` mapping a path to the single path its symlink points at, e.g. `{"/app/current": "/app/r42", "/app/r42": "/app/stable", "/app/stable": "/app/current"}`. A path that is **not a key** is a real file: the chain ends there. Every value is a `str`, and may or may not be a key.
- `start` — a `str`, the path to start resolving from. It may not be a key either.

## You return
- `None` when following the chain from `start` reaches a path that is not a key — the chain terminates and there is no loop
- otherwise a tuple `(entry, length)`: `entry` is the first path on the chain that is part of the loop, and `length` is an `int`, how many links the loop contains

## Rules
- one hop is one dictionary lookup. `links[p]` is where `p` points, and `p` not being a key is the end of the chain
- `entry` is the path where the loop **begins** as reached from `start`, not wherever your two walkers happened to meet. The tail leading into the loop may be any length, including zero
- a path that points at itself is a loop of length 1: `{"/tmp/a": "/tmp/a"}` from `/tmp/a` is `("/tmp/a", 1)`
- `start` not being a key is `None`, immediately
- `length` counts paths in the loop, which is also the number of hops to get back to where you started: a three-link ring is `3`, not `2` and not `4`
- two walkers, two variables. A `set` of everywhere you have been gives the same answer and is the thing this task exists to replace
- `links` comes back untouched

```python
links = {"/a": "/b", "/b": "/c", "/c": "/d", "/d": "/e", "/e": "/c"}
solve(links, "/a")     # -> ("/c", 3)
solve(links, "/c")     # -> ("/c", 3)
solve({"/a": "/b", "/b": "/real"}, "/a")   # -> None
solve({"/t": "/t"}, "/t")                  # -> ("/t", 1)
solve({}, "/anything")                     # -> None
```

> [!WARNING]
> The path where the two walkers meet is inside the loop but is almost never the path the loop starts at. In the first example above they meet at `/d`, and `/d` is not the link to repoint — `/c` is. Returning the meeting point gives a plausible path with the right loop length beside it, which is why it survives a quick eyeball and is the one wrong answer this task is built to catch.

> [!NOTE]
> The fix is one short walk and no arithmetic: put one walker back at `start`, leave the other at the meeting point, and move **both** one step at a time. They meet at the entry. It is worth stepping through the example by hand once before believing it.

## Hints
### Hint 1
Phase one, is there a loop at all. Both walkers start at `start`; each round the slow one takes one hop and the fast one takes two. Every hop is a `dict.get`, and the moment any of them comes back `None` the chain has ended — return `None`. When the two walkers hold the same path, there is a loop and you are standing somewhere inside it.

Watch the start condition: if the loop is `while slow != fast`, it never runs, because both begin at `start`. Hop first, compare after.

### Hint 2
Phase two, where does it begin. Move one walker back to `start` and leave the other where they met, then advance both one hop at a time until they are equal again; that path is `entry`. Phase three is the easy one: from `entry`, hop until you are back at `entry`, counting the hops.

### Hint 3
Same two walkers, different chain — the cycle a fixed-width hash chain falls into, which is what makes a short digest unsafe as a long-term identifier:

```python
def chain_cycle(step, start):
    slow = fast = start
    while True:
        slow = step(slow)
        fast = step(step(fast))
        if slow == fast:
            break
    entry = start
    while entry != slow:
        entry, slow = step(entry), step(slow)
    length, node = 1, step(entry)
    while node != entry:
        node, length = step(node), length + 1
    return entry, length

chain_cycle(lambda n: (n * n + 1) % 255, 3)   # -> (101, 6)
```

Here nothing can ever end, because `step` is defined everywhere — so the `None` checks vanish and the loop is guaranteed. Comparing the two shapes is the useful bit: in a `dict` of symlinks the chain can stop, and that is the only reason phase one needs a way out other than meeting.
