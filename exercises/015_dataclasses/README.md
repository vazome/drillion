---
title: dataclasses — defaults, frozen=True, sort by a field
minutes: 12
prereqs: []
tags: [core]
---
# dataclasses — defaults, frozen=True, sort by a field

*@dataclass writes the boilerplate; frozen=True makes a record you cannot corrupt.*

## Why
An inventory script reads server records from a short-hand list
where people leave out the fields that have sensible defaults: most
servers get 100 CPU and live in the main zone unless said otherwise. The
records get passed around many scripts, so nobody should be able to
change one by accident after it is made. Capacity planning then wants
the list ordered smallest-CPU first.

## You get
`specs` — a list of tuples of 1, 2 or 3 items like [("db",
400), ("api",), ("edge", 200, "eu-west-1b")]: name, then optional cpu,
then optional zone. The test creates it and hands it to you; you never
build it yourself.

## You return
a list of Node records (one per spec, defaults filled in,
locked against later edits), sorted by cpu from smallest to largest.

## Rules
Build frozen Node records from short specs and sort them by cpu.

Define a dataclass called Node with exactly these three fields, in this
order, with these defaults:

```
name: str
cpu: int = 100
zone: str = "us-east-1a"
```

It must be frozen, so no attribute can be reassigned after construction.

specs is a list of tuples of length 1, 2 or 3 — the leading fields only,
with whatever is missing left to the defaults. Return the list of Node
instances sorted by cpu, ascending.

```python
[("db", 400), ("api",), ("edge", 200, "eu-west-1b")]
->  [Node(name='api',  cpu=100, zone='us-east-1a'),
     Node(name='edge', cpu=200, zone='eu-west-1b'),
     Node(name='db',   cpu=400, zone='us-east-1a')]
```

Node(*spec) spreads a short tuple straight into the constructor, which is
where the defaults do their work — no need to pad the tuples yourself.
Sort with sorted and a key.

## Hints
### Hint 1
Two halves. First, describe the record: a class body that is nothing but field names with their types, plus one decorator that turns that into a real class with a constructor, a repr and equality. Second, the frozen part — the decorator takes an argument that makes assignment raise instead of silently rewriting a record someone else is holding. Then it is just a sort.
### Hint 2
from dataclasses import dataclass, then @dataclass(frozen=True) above class Node. Inside the class write the three annotated fields, giving the last two their default values; fields with defaults must come after ones without. Build with Node(*spec) for each spec, and return sorted(nodes, key=lambda n: n.cpu).
### Hint 3
Different data — release records:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Release:
    tag: str
    build: int = 0

rs = [Release(*s) for s in [('v2', 7), ('v1',)]]
print(rs)                                  # [Release(tag='v2', build=7), 
                                           #  Release(tag='v1', build=0)]
print(sorted(rs, key=lambda x: x.build))   # v1 first
rs[0].build = 9                            # dataclasses.FrozenInstanceError
```

The repr and the __init__ came free — that is the whole point of the decorator.
