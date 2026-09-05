---
title: slicing — combine start, stop, step
difficulty: easy
tier: core
minutes: 10
prereqs: [17]
tags: [slicing]
---
# slicing — combine start, stop, step

*Slicing — the fastest way to grab exactly the part of a list you mean.*

## Read first
- [Common Sequence Operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — `s[i:j:k]`, and what a negative step really does

## Why
You keep a list of the last few health-check readings for a server, oldest first. The on-call engineer keeps asking for different cuts of it: "drop the warm-up and cool-down readings", "show me only every second sample", "show it newest-first", "just the last three". Pulling out exactly the part of a list you mean, without writing a loop each time, is the skill behind every one of those requests.

## You get
`xs` — a list of numbers like

```python
[10, 11, 12, 13, 14, 15]
```

always at least 5 long. The test creates it and hands it to you; you never build it yourself.

## You return
a dict with five keys (`"trim"`, `"odds"`, `"rev"`, `"inner"`, `"last3"`), each holding a list that is one cut of `xs`. `xs` itself must be left exactly as it was.

## Rules
Return a dict with five slices of `xs`. Do not modify `xs`.

| key | the cut |
| --- | --- |
| `"trim"` | everything except the first and last item |
| `"odds"` | every 2nd item, starting from index 1 |
| `"rev"` | the whole list backwards |
| `"inner"` | every 2nd item of the trimmed list — one slice, all three of start, stop and step |
| `"last3"` | the last three items |

```python
solve([10, 11, 12, 13, 14, 15])
# -> {"trim": [11, 12, 13, 14], "odds": [11, 13, 15],
#     "rev": [15, 14, 13, 12, 11, 10], "inner": [11, 13],
#     "last3": [13, 14, 15]}
```

`xs` always has at least 5 items. No loops needed anywhere.

## Hints
### Hint 1
The full form is `[start:stop:step]`; every part is optional and negatives count from the end. `stop` is exclusive. Work out which of the three parts each key actually needs — only one key needs all of them.
### Hint 2
`trim` is a start of 1 with a stop of -1. `odds` is a start of 1 with a step of 2. `rev` is a step of -1 on its own. `inner` is trim's start and stop with odds' step, in one slice. `last3` is a negative start with no stop.
### Hint 3
Different data, same moves:

```python
s = 'abcdefg'
print(s[1:-1])    # 'bcdef'
print(s[1::2])    # 'bdf'
print(s[::-1])    # 'gfedcba'
print(s[2:-2:2])  # 'ce'
```

Strings and lists slice identically.
