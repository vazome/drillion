---
title: f-strings — aligned report columns
difficulty: easy
tier: core
minutes: 10
prereqs: [2, 16]
tags: [f-strings]
---
# f-strings — aligned report columns

*f-string format specs — every ops report and CLI table uses them.*

## Why
You run the servers for a company. Every month finance asks "how much did each service cost?" and wants it as a neat table they can read at a glance — numbers lined up under each other, commas in the thousands, always two decimals. Ragged numbers get misread; aligned ones don't. Your job is to turn a plain list of (service, cost) into that table.

## You get
`rows` — a list of pairs like

```python
[("api", 1234.5), ("db", 7.25)]
```

The test creates it and hands it to you; you never build it yourself.

## You return
one string with one line per pair: the name on the left, the cost padded on the right so all costs line up when printed.

## Rules
Each row is `(name, value)`; value is a float. Return ONE string, lines joined with `"\n"`, no trailing newline. Per line:

- name left-aligned in a 14-wide column
- value right-aligned in a 12-wide column, with a thousands separator and exactly 2 decimals

```python
solve([("api", 1234.5), ("db", 7.25)])
# -> 'api               1,234.50\ndb                    7.25'
```

which prints as:

```text
api               1,234.50
db                    7.25
```

Names are always shorter than 14 chars, values under a million.

## Hints
### Hint 1
Everything after the colon inside the braces is a format spec. You need three effects: pad-and-left-align the name, pad-and-right-align the number, and give the number commas plus fixed decimals. Then join the lines.
### Hint 2
The pieces: `<` left-aligns, `>` right-aligns, a number is the width, a comma turns on thousands separators, `.2f` fixes two decimals. They stack in one spec, in that order. Build one f-string per row, then `'\n'.join` the lot.
### Hint 3
Different data, same shape:

```python
for city, pop in [('oslo', 709037), ('york', 202821)]:
    print(f'{city:<8}{pop:>12,}')
# oslo         709,037
# york         202,821
```

For floats, add `.2f` right after the comma: `{v:>12,.2f}`.
