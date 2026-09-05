---
title: enumerate + zip — pair and number
difficulty: easy
tier: core
minutes: 8
prereqs: [17]
tags: [enumerate-zip]
---
# enumerate + zip — pair and number

*enumerate and zip replace every clumsy `for i in range(len(...))`.*

## Why
You have two lists that belong together: server names and the IP addresses assigned to them, in matching order. A teammate asks for a numbered inventory they can paste into a ticket: "1. web 10.0.0.1", "2. db 10.0.0.2", and so on. Walking two lists side by side while numbering the lines is one of the most common small jobs in ops scripting.

## You get
`hosts` — a list of server names like `["web", "db"]`. `ips` — a list of IP address strings like `["10.0.0.1", "10.0.0.2"]`, the same length, in the same order. The test creates them and hands them to you; you never build them yourself.

## You return
a list of strings, one per server, numbered from 1.

## Rules
Pair each host with its ip and number the lines starting from 1. Return a list of strings shaped `"N. host ip"`:

```python
solve(["web", "db"], ["10.0.0.1", "10.0.0.2"])
# -> ["1. web 10.0.0.1", "2. db 10.0.0.2"]
```

The lists are always the same length.

> [!TIP]
> No manual counter and no `range(len(...))` — that avoidance is the whole task.

## Hints
### Hint 1
Two jobs at once: walking two lists in step, and counting from 1. Python has one builtin for each; used together they hand you everything the loop body needs.
### Hint 2
`zip(hosts, ips)` yields pairs. `enumerate(..., start=1)` wraps any iterable and yields `(number, item)` — here the item IS a pair, so the `for` line unpacks a number and a parenthesised pair.
### Hint 3
Different data, same shape:

```python
names = ['ada', 'linus']
langs = ['math', 'c']
for i, (n, lang) in enumerate(zip(names, langs), start=1):
    print(f'{i}: {n} likes {lang}')
# 1: ada likes math
# 2: linus likes c
```

Collect into a list instead of printing.
