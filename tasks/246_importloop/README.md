---
title: cycle detection — find the import loop, and say which modules are in it
difficulty: hard
tier: advanced
minutes: 22
prereqs: [143]
tags: [graphs, recursion]
---
# cycle detection — find the import loop, and say which modules are in it

*Two sets tell a loop from a diamond: one for everything you have ever visited, one for what is on the path you are standing on right now.*

## Read first
- [Set types](https://devdocs.io/python~3.14/library/stdtypes#set) — two sets that mean different things is the whole idea here
- [More on lists](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists) — `append`, `pop` and `index`, the three list methods the path needs
- [Defining functions](https://devdocs.io/python~3.14/tutorial/controlflow#defining-functions) — an inner function that closes over the sets, so they are not passed around

## Why
A refactor lands and the test suite dies on `ImportError: cannot import name ... (most likely due to a circular import)`. Python names one module in that message, which is almost never the one to change. What the person fixing it needs is the whole loop — `api` imports `auth`, `auth` imports `models`, `models` imports `api` — because that is what tells you which of the three arrows is the one that should never have been drawn.

## You get
`imports` — a dictionary mapping each module name to the list of modules it imports, like `{"api": ["auth"], "auth": ["models"], "models": ["api"], "utils": []}`. Every module named anywhere is a key.

## You return
one loop, as a list of module names where the first name appears again at the end: `["api", "auth", "models", "api"]`. An empty list when nothing loops.

## Rules
- Imports go one way. `"api": ["auth"]` means api imports auth.
- More than one loop can exist. Report the first one you meet when you visit the modules in **sorted** order and follow each module's imports in the order they are listed. Any implementation that walks in that order finds the same loop.
- A module that imports itself is a loop of one: `{"api": ["api"]}` gives `["api", "api"]`.
- Nothing loops is the common case, and it returns `[]`.

```python
solve({"api": ["auth"], "auth": ["models"], "models": ["api"], "utils": []})
# -> ["api", "auth", "models", "api"]
solve({"app": ["db", "cache"], "cache": ["core"], "db": ["core"], "core": []})
# -> []
```

> [!WARNING]
> "I have seen this module before" is not "this module is a loop". In the second example above, `core` is reached down two different branches and there is no loop anywhere — a single `visited` set calls that a circular import and sends somebody to rewrite a file that was fine. What makes it a loop is meeting a module that is on the path you are **currently standing on**.

> [!NOTE]
> That means a module leaves the current path when you finish with it. Whatever you use to remember the path — a list, a set, both — has to shrink again on the way back out, or the second branch inherits the first branch's path.

## Hints
### Hint 1
Keep two things: `seen`, which a module joins the first time you ever visit it and never leaves, and the current path, which a module joins on the way down and leaves on the way back up. A neighbour already on the current path is the loop. A neighbour in `seen` but not on the path is a module you have finished with, and there is nothing to do.
### Hint 2
Keep the path as a list, so you can also *report* it: when the neighbour `nxt` is on the path, the loop is the tail of that list from `nxt` onwards, with `nxt` written once more at the end. `list.index` finds where to cut.
### Hint 3
The same two-set walk, deciding whether a set of spreadsheet formulas can be evaluated at all:

```python
def loops(refers_to):
    seen, path = set(), []

    def walk(cell):
        seen.add(cell)
        path.append(cell)
        for nxt in refers_to[cell]:
            if nxt in path or (nxt not in seen and walk(nxt)):
                return True
        path.pop()
        return False

    return any(walk(cell) for cell in sorted(refers_to) if cell not in seen)
```

`path.pop()` runs only when the cell is finished, which is exactly what keeps a diamond from reading as a loop. (`nxt in path` on a list is a scan; a set alongside it is the version that stays fast.)
