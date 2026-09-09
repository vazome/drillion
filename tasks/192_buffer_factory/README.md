---
title: closures — build independent bounded buffers
difficulty: medium
tier: advanced
minutes: 18
prereqs: [43, 44, 45]
tags: [closures, mutable-default, truthiness]
---
# closures — build independent bounded buffers

*Keep state between calls without leaking it between buffers or confusing zero with missing.*

## Read first
- [Python scopes and namespaces](https://devdocs.io/python~3.14/tutorial/classes#python-scopes-and-namespaces) — names retained by an enclosing function
- [Default argument values](https://devdocs.io/python~3.14/tutorial/controlflow#default-argument-values) — why a list must not be a default
- [Truth value testing](https://devdocs.io/python~3.14/library/stdtypes#truth-value-testing) — why `0` and `None` need different checks here

## Why
A callback can retain a short history without a class. The trap is putting that history in a mutable default, where every callback shares it, or treating `limit=0` as though no limit was supplied.

## You get
Nothing is passed to `solve`; the grader calls the factory you return with varied limits and initial values.

## You return
From `solve`, return a function `make_buffer(limit=None, initial=None)`. Calling it returns a `push(item)` closure.

## Rules
Each `make_buffer` call owns a fresh list. Copy `initial` when it is supplied; never mutate the caller's list. Each `push` appends its item, trims the retained values to the last `limit`, and returns a new list snapshot.

- `limit=None` keeps everything.
- `limit=0` keeps nothing.
- two buffers never share contents.

## Hints
### Hint 1
Create `items` inside `make_buffer`, then define `push` underneath it. That enclosing local is the state the closure remembers.
### Hint 2
Use `initial=None`, followed by `items = [] if initial is None else list(initial)`. The explicit `is None` preserves the separate meaning of zero.
### Hint 3
After appending, trim only when `limit is not None`. A zero limit needs an empty result; positive limits keep `items[-limit:]`. Return `list(items)` so callers cannot mutate the closure's state directly.
