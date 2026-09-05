---
title: comprehension — transform + filter
difficulty: easy
tier: core
minutes: 8
prereqs: []
tags: [comprehension]
---
# comprehension — transform + filter

*Comprehension with a filter — transform some, skip the rest.*

## Read first
- [List Comprehensions](https://devdocs.io/python~3.14/tutorial/datastructures#list-comprehensions) — the form, and when a loop reads better
- [Nested List Comprehensions](https://devdocs.io/python~3.14/tutorial/datastructures#nested-list-comprehensions) — two `for` clauses, and which order they run in

## Why
After a compliance quiz, HR sends you a list of people with their scores and asks for the names of everyone who passed (50 or more), in capital letters for the badge printer. Picking some items out of a list and reshaping them in a single step is the bread and butter of every ops script.

## You get
`records` — a list of two-item lists like

```python
[["ana", 80], ["bo", 12]]
```

each holding a name and a score. The test creates it and hands it to you; you never build it yourself.

## You return
a list of uppercase names, only those whose score is 50 or more, in the order they appeared.

## Rules
Each record is `[name, score]`. Return the NAMES of everyone whose score is 50 or more, uppercased, in the order they appear.

```python
solve([["ana", 80], ["bo", 12], ["cy", 50]])   # -> ["ANA", "CY"]
```

Write it as a single list comprehension.

## Hints
### Hint 1
Two jobs in one line: throw away the low scorers (a filter), and change what survives into an uppercase name (a transform).
### Hint 2
Skeleton, fill the three slots:

```text
[ ???? for r in records if ???? ]
```

Remember `r` is one whole `[name, score]` pair — index into it.
### Hint 3
Different data, same shape:

```python
pairs = [['ny', 8], ['berlin', 3], ['tokyo', 14]]
big = [p[0].upper() for p in pairs if p[1] > 5]
print(big)      # ['NY', 'TOKYO']
```
