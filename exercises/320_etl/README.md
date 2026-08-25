---
title: etl — reshape the score table from one-to-many to one-to-one
minutes: 10
prereqs: [236]
tags: [exercism, dicts, data-structures]
source: exercism/python practice/etl (MIT, adapted)
---
# etl — reshape the score table from one-to-many to one-to-one

*etl — invert a "group → members" dict into a "member → group" dict.*

## Why
Configuration is written the way humans like to read it — grouped. "These ten letters are worth one point." "These four users have the admin role." "These three services live in eu-west-1." Code asks the opposite question, one item at a time: what is *this* letter worth, what role does *this* user have, where does *this* service live. Scanning every group on every question is how a fast program becomes a slow one. So you build the inverted lookup once, when the config is loaded, and every later question is a single dict access. That "read one shape, write the other" step is the T in ETL, and it is most of what data plumbing actually is.

## Introduction
You work for a company that makes an online multiplayer game called Lexiconia.

To play the game, each player is given 13 letters, which they must rearrange to create words.
Different letters have different point values, since it's easier to create words with some letters than others.

The game was originally launched in English, but it is very popular, and now the company wants to expand to other languages as well.

Different languages need to support different point values for letters.
The point values are determined by how often letters are used, compared to other letters in that language.

For example, the letter 'C' is quite common in English, and is only worth 3 points.
But in Norwegian it's a very rare letter, and is worth 10 points.

To make it easier to add new languages, your team needs to change the way letters and their point values are stored in the game.

## Instructions
Your task is to change the data format of letters and their point values in the game.

Currently, letters are stored in groups based on their score, in a one-to-many mapping.

- 1 point: "A", "E", "I", "O", "U", "L", "N", "R", "S", "T",
- 2 points: "D", "G",
- 3 points: "B", "C", "M", "P",
- 4 points: "F", "H", "V", "W", "Y",
- 5 points: "K",
- 8 points: "J", "X",
- 10 points: "Q", "Z",

This needs to be changed to store each individual letter with its score in a one-to-one mapping.

- "a" is worth 1 point.
- "b" is worth 3 points.
- "c" is worth 3 points.
- "d" is worth 2 points.
- etc.

As part of this change, the team has also decided to change the letters to be lower-case rather than upper-case.

> [!NOTE]
> If you want to look at how the data was previously structured and how it needs to change, take a look at the examples in the test suite.

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

## Read first
- [Mapping types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) — what a dict guarantees, and why the lookup is the point
- [Docs: dicts](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) — the tutorial section, including dict comprehensions
- [dict.items()](https://docs.python.org/3/library/stdtypes.html#dict.items) — walking keys and values together instead of keys then lookups
- [str.lower()](https://docs.python.org/3/library/stdtypes.html#str.lower) — the case fold, applied to each letter

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

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
