---
title: dicts — reshape the score table from one-to-many to one-to-one
difficulty: easy
tier: core
minutes: 10
prereqs: [25]
tags: [dicts]
source: exercism/python practice/etl (MIT, adapted)
---
# dicts — reshape the score table from one-to-many to one-to-one

*etl — invert a "group → members" dict into a "member → group" dict.*

## Read first
- [Mapping types: dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — what a dict guarantees, and why the lookup is the point
- [Docs: dicts](https://devdocs.io/python~3.14/tutorial/datastructures#dictionaries) — the tutorial section, including dict comprehensions
- [dict.items()](https://devdocs.io/python~3.14/library/stdtypes#dict.items) — walking keys and values together instead of keys then lookups
- [str.lower()](https://devdocs.io/python~3.14/library/stdtypes#str.lower) — the case fold, applied to each letter

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Configuration is written the way humans like to read it — grouped. "These ten letters are worth one point." "These four users have the admin role." "These three services live in eu-west-1." Code asks the opposite question, one item at a time: what is *this* letter worth, what role does *this* user have, where does *this* service live. Scanning every group on every question is how a fast program becomes a slow one. So you build the inverted lookup once, when the config is loaded, and every later question is a single dict access. That "read one shape, write the other" step is the T in ETL, and it is most of what data plumbing actually is.

## You get
`legacy_data` — a dict whose keys are point values (`int`) and whose values are lists of upper-case letters (`str`):

```python
{1: ["A", "E"], 2: ["D", "G"]}
```

The scores are whatever the language in question uses; do not assume the English set of 1, 2, 3, 4, 5, 8, 10.

> [!NOTE]
> Exercism's stub is `def transform(legacy_data)`. Here the function is `solve(legacy_data)`; nothing else about the task changes.

## You return
A new `dict` mapping each letter, lower-cased (`str`), to its point value (`int`). Order does not matter — dicts compare by content.

## Rules
- every letter in every list becomes one key of the result
- the value is the score its list was filed under
- the input is upper case, the output is lower case
- leave `legacy_data` itself untouched; build and return a new dict

```python
solve({1: ["A"]})                      # -> {"a": 1}
solve({1: ["A", "E"], 2: ["D", "G"]})  # -> {"a": 1, "e": 1, "d": 2, "g": 2}
solve({4: ["F", "H", "V", "W", "Y"]})  # -> {"f": 4, "h": 4, "v": 4, "w": 4, "y": 4}
```

## Hints
### Hint 1
Count the keys before and after. The input has one key per *score*; the output has one key per *letter*. That tells you the result is bigger than the input and that you cannot build it with a single pass over `legacy_data`'s keys alone — you have to get inside each list as well.

### Hint 2
Two loops, one inside the other. The outer one walks the pairs of the input dict, so you are holding a score and the list of letters filed under it at the same time; `.items()` gives you both without a second lookup. The inner one walks that list, and for each letter you write one entry into a result dict you started as `{}`. Once that works, notice a comprehension can carry two `for` clauses in exactly the same order the loops appear, which collapses the whole thing to one expression — but get the loops right first.

### Hint 3
Different data, same inversion — a deployment map that is written region-first and has to be queried service-first:

```python
by_region = {"eu-west-1": ["api", "web"], "us-east-1": ["db"]}

by_service = {}
for region, services in by_region.items():
    for service in services:
        by_service[service] = region

by_service   # -> {'api': 'eu-west-1', 'web': 'eu-west-1', 'db': 'us-east-1'}
```

The outer loop hands you the group, the inner loop hands you the member, and the assignment flips which one is the key.
