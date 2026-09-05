---
title: str — split, transform, join back
difficulty: easy
tier: core
minutes: 8
prereqs: [5]
tags: [files-text]
---
# str — split, transform, join back

*split / join — the two directions of every parsing task.*

## Why
A colleague pastes a list of service names into a ticket, separated by commas but with random spaces around each name. Your deploy tool needs the names clean, and the status page wants them shown separated by a vertical bar. This tidy-then-reformat step is the first line of nearly every script that takes text typed by a human.

## You get
`line` — one string of comma-separated names with messy spacing, like `" api, db ,cache "`. The test creates it and hands it to you; you never build it yourself.

## You return
one string with the names trimmed and joined by `" | "`, like `"api | db | cache"`.

## Rules
Given a comma-separated line with untidy spacing, return the fields trimmed and rejoined with `" | "`.

```python
solve("  api,  db ,cache ")   # -> "api | db | cache"
```

Empty fields never occur.

## Hints
### Hint 1
Three moves: break the line into pieces, clean each piece, glue them back with a different separator. You know all three by name.
### Hint 2
`split(',')` gives the pieces. A string method removes whitespace from both ends of each piece. Then the separator you want does the gluing — and remember the separator owns that method, not the list.
### Hint 3
Different data, same shape:

```python
line = ' a; b ;c '
parts = [p.strip() for p in line.split(';')]
print(' - '.join(parts))    # 'a - b - c'
```

`join` builds the gaps for you — never append separators by hand.
