---
title: unpacking — star, swap, loop
difficulty: medium
tier: core
minutes: 12
prereqs: []
tags: [unpacking]
---
# unpacking — star, swap, loop

*Star-unpacking and tuple assignment — Python's way of naming the parts.*

## Why
A deploy pipeline hands you a list of build numbers and a list of tag settings. The release manager needs the pieces named: which build is the first, which is the latest, everything in between, and the tags written as "key=value" lines for a config file. Pulling a list apart into named parts without fiddling with index numbers is a daily Python habit, and interviewers watch for it.

## You get
`xs` — a list of at least 3 numbers like `[5, 6, 7]`. `pairs` — a list of two-word pairs like

```python
[("env", "prod"), ("region", "eu")]
```

The test creates them and hands them to you; you never build them yourself.

## You return
a dict with six keys (`"first"`, `"rest"`, `"body"`, `"last"`, `"swapped"`, `"lines"`) holding the named parts of `xs` and the `"key=value"` lines built from `pairs`.

## Rules
`xs` is a list of numbers (at least 3 long). `pairs` is a list of `(key, value)` tuples of strings. Return a dict:

| key | value |
| --- | --- |
| `"first"` | first item of `xs` |
| `"rest"` | everything after the first, as a list |
| `"body"` | everything before the last, as a list |
| `"last"` | last item |
| `"swapped"` | a copy of `xs` with first and last items exchanged |
| `"lines"` | one `"key=value"` string per pair |

```python
solve([5, 6, 7], [("env", "prod"), ("region", "eu")])
# -> {"first": 5, "rest": [6, 7], "body": [5, 6], "last": 7,
#     "swapped": [7, 6, 5], "lines": ["env=prod", "region=eu"]}
```

> [!TIP]
> Slicing would pass the test — do it with star-unpacking anyway (`a, *rest = ...`), one tuple swap with no temp variable, and unpack each pair right in the `for` line. That is what is being drilled.

## Hints
### Hint 1
One starred name on the LEFT of an assignment soaks up 'whatever is left over' as a list, and it can sit at either end. Swapping needs no temp variable because Python builds the whole right-hand side before assigning anything.
### Hint 2
Four moves: star-assign with the star last to split off the first item; star first to split off the last; on a copy of `xs`, assign a pair to a pair to swap the ends; and in the loop header give each pair's two slots their own names.
### Hint 3
Different data, same moves:

```python
q = ['mon', 'tue', 'wed', 'thu']
head, *tail = q            # 'mon', ['tue', 'wed', 'thu']
*early, final = q          # ['mon', 'tue', 'wed'], 'thu'
a, b = 1, 2
a, b = b, a                # a=2, b=1
for k, v in [('cpu', '90'), ('mem', '40')]:
    print(k + '=' + v)     # cpu=90  mem=40
```

Same shapes, collected into your dict.
