---
title: function arguments — *args, **kwargs and keyword-only
difficulty: medium
tier: core
minutes: 15
prereqs: [20]
tags: [function-arguments, functions]
---
# function arguments — *args, **kwargs and keyword-only

*A bare `*` in a signature draws a line: everything after it can only be passed by name.*

## Read first
- [Arbitrary Argument Lists](https://devdocs.io/python~3.14/tutorial/controlflow#arbitrary-argument-lists) — `*args` collects the positional arguments nobody named
- [Keyword Arguments](https://devdocs.io/python~3.14/tutorial/controlflow#keyword-arguments) — `**kwargs` collects the named ones, as a dict
- [Special parameters](https://devdocs.io/python~3.14/tutorial/controlflow#special-parameters) — the bare `*` marker, and why a parameter after it cannot be passed by position

## Why
Your tooling wraps other people's commands, so it cannot know in advance how many arguments a caller will pass or what flags they will invent. It does have settings of its own, like a timeout, and those must never be filled in by accident: a caller writing one extra positional argument should get that argument added to the command, not silently reassign the timeout to `5`. Python has a marker for exactly that boundary, and it is one character wide.

## You get
nothing to start — you return a function. The test calls it like

```python
describe = solve()
describe("deploy", "api", "--force", timeout=60, region="eu", dry_run=True)
```

## You return
the function `describe`, which returns one line of text.

## Rules
`describe(cmd, *args, timeout=30, **flags)`, and the line it returns is built in this order:

1. `cmd`, then each of `args`, separated by single spaces.
2. then each flag as `--name=value`, **sorted by name**, with underscores in the name turned into dashes.
3. then ` (timeout=N)` at the end, always.

```python
describe("deploy", "api", "--force", timeout=60, region="eu", dry_run=True)
# -> "deploy api --force --dry-run=True --region=eu (timeout=60)"

describe("status")
# -> "status (timeout=30)"
```

> [!WARNING]
> `timeout` sits after the `*args`, which already makes it keyword-only, and the test relies on it: `describe("deploy", "api", 5)` must put `5` into the command as a third word and leave the timeout at 30. A signature written `describe(cmd, timeout=30, *args, **flags)` passes the simple cases and fails that one.

## Hints
### Hint 1
Three collecting parameters in one signature, in the only order Python allows: the plain one, then `*args`, then anything keyword-only, then `**flags`. `args` arrives as a tuple, `flags` as a dict.
### Hint 2
Build the pieces as a list of strings and join once at the end. For the flags, `sorted(flags.items())` gives you name order, and `name.replace("_", "-")` fixes the names Python forced you to spell with underscores.
### Hint 3
Different data, same shape:

```python
def line(head, *rest, sep=" ", **extra):
    return sep.join([head, *rest]) + str(sorted(extra.items()))

print(line("a", "b", "c", sep="-", x=1))   # a-b-c[('x', 1)]
```

`sep` could not have been passed positionally there, and that is the property this task tests.
