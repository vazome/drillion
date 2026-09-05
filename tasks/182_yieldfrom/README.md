---
title: yield from — let a generator delegate to itself
difficulty: medium
tier: advanced
minutes: 15
prereqs: [7]
tags: [generators, recursion]
---
# yield from — let a generator delegate to itself

*`yield from` hands the floor to another generator and gives it back when that one is done.*

## Read first
- [The yield statement](https://devdocs.io/python~3.14/reference/simple_stmts#the-yield-statement) — `yield from iterable` yields every item of it, one at a time
- [Generators](https://devdocs.io/python~3.14/tutorial/classes#generators) — the `yield` refresher this builds on
- [Recursion](https://devdocs.io/python~3.14/glossary#term-recursion) — a function that calls itself, which is how nesting of unknown depth gets walked

## Why
Configuration files include other configuration files, which include more. Flattening that into the exact order a reader would see, without knowing the depth in advance, is a recursive walk. The recursive part is easy; the awkward part is that each level produces many lines, so a `return` will not do, and writing `for line in walk(child): yield line` at every level is a loop whose only job is to pass items upward. `yield from` is that loop, in two words.

## You get
`configs` — a dict from a config name to its entries, e.g.

```python
{"main":  ["log_level=info", ("include", "db"), "port=80"],
 "db":    ["db_host=localhost", ("include", "creds")],
 "creds": ["db_user=app"]}
```

An entry is either a settings line (a string) or an include (the pair `("include", other_name)`). `start` — the name to begin from, e.g. `"main"`.

## You return
a **generator** of the settings lines, in the order a reader expanding the includes in place would meet them.

## Rules
- Walk the entries of `start` in order. A string is a line to yield. An include is replaced by the whole expansion of the config it names, in that position.
- Includes nest to any depth. The example above yields `["log_level=info", "db_host=localhost", "db_user=app", "port=80"]`.
- An include naming a config that is not in `configs` yields nothing and is not an error.
- Return a generator, not a list: the test checks that nothing runs until the first item is asked for.

```python
list(solve(configs, "main"))
# -> ["log_level=info", "db_host=localhost", "db_user=app", "port=80"]
```

> [!NOTE]
> `port=80` comes last even though it sits above two levels of includes in the file, because the include is expanded where it appears. That ordering is the reason this is a walk and not a merge.

## Hints
### Hint 1
Write a generator function that takes a config name. For each entry: a string gets yielded, an include needs every line of the named config yielded here, in place. That second half is the same function again.
### Hint 2
`yield from expand(name)` runs the inner generator to exhaustion, passing each item up to your caller. It is the whole of `for line in expand(name): yield line`, and it also keeps the laziness: nothing is built into a list on the way up.
### Hint 3
Different data, same shape:

```python
def flatten(x):
    for item in x:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

print(list(flatten([1, [2, [3, 4]], 5])))   # [1, 2, 3, 4, 5]
```

Your `isinstance` test is "is this entry a tuple", and the recursive call takes a name rather than a list.
