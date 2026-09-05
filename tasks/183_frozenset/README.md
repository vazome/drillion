---
title: frozenset — a set you can use as a key
difficulty: medium
tier: core
minutes: 12
prereqs: [12]
tags: [sets, dicts]
---
# frozenset — a set you can use as a key

*A `set` can change, so it cannot be a dict key. A `frozenset` cannot change, so it can.*

## Read first
- [frozenset()](https://devdocs.io/python~3.14/library/stdtypes#frozenset) — the immutable set: same operators, no `add`, and hashable
- [Mapping types — dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — the rule underneath: keys must be hashable
- [hashable](https://devdocs.io/python~3.14/glossary#term-hashable) — the one-paragraph definition of what a dict needs from a key

## Why
Every host in the fleet carries a set of tags, and the platform team wants to know which exact combinations are in use and how common each one is, so the rare one-off combinations can be cleaned up. Tag order is meaningless and duplicates are noise, so the natural key is a set. Python refuses: a set is mutable, so it has no stable hash, and a dict cannot look up a key that might change after it was filed. The frozen version exists for exactly this.

## You get
`hosts` — a dict from host name to its list of tags, e.g.

```python
{"web-1": ["prod", "eu"], "web-2": ["eu", "prod"], "db-1": ["prod", "db", "prod"]}
```

Tags repeat within a list and come in any order.

## You return
a dict from the exact tag combination, as a `frozenset`, to how many hosts have it.

## Rules
- Two hosts share a combination when their tags are the same ignoring order and repeats, so `["prod", "eu"]` and `["eu", "prod"]` are one combination.
- The keys of your result are `frozenset` objects; the values are counts.
- A host with no tags counts too, under the empty combination.

```python
solve({"web-1": ["prod", "eu"], "web-2": ["eu", "prod"], "db-1": ["prod", "db", "prod"]})
# -> {frozenset({"prod", "eu"}): 2, frozenset({"prod", "db"}): 1}
```

> [!WARNING]
> `counts[set(tags)] += 1` raises `TypeError: unhashable type: 'set'`. That error is the whole lesson: reach for `frozenset(tags)` and the same line works.

## Hints
### Hint 1
One pass over the hosts. For each, turn its tag list into something that ignores order and repeats AND can be a dict key, then add one to that key's count.
### Hint 2
`frozenset(tags)` does the deduplicating and the ordering-away in one call, and unlike `set(tags)` it can be filed in a dict. `collections.Counter` will count them for you once the keys are hashable.
### Hint 3
Different data, same shape:

```python
from collections import Counter
orders = [["milk", "eggs"], ["eggs", "milk"], ["milk"]]
print(Counter(frozenset(o) for o in orders))
# Counter({frozenset({'eggs', 'milk'}): 2, frozenset({'milk'}): 1})
```

A plain `dict` with `.get(key, 0) + 1` works just as well; the frozen key is the part that is not optional.
