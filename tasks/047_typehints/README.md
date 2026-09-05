---
title: type hints — read a signature with get_type_hints
difficulty: medium
tier: core
minutes: 22
prereqs: [12]
tags: [type-hints]
---
# type hints — read a signature with get_type_hints

*Most of the type hints you meet are ones you read, not ones you wrote.*

## Read first
- [Python Type Checking (Guide)](https://realpython.com/python-type-checking/) — why annotations are worth writing, and what a checker does with them
- [typing — support for type hints](https://devdocs.io/python~3.14/library/typing) — reference, only for lookup
- [Dictionaries (Python tutorial)](https://devdocs.io/python~3.14/tutorial/datastructures#dictionaries) — dicts: read, add, remove, loop over
- [Dictionaries in Python](https://realpython.com/python-dicts/) — same, longer; 'Building a Dictionary Incrementally' and 'Dictionary Methods' (`.items()`, `.pop()`) are the 70% of this task
- [typing.get_type_hints](https://devdocs.io/python~3.14/library/typing#typing.get_type_hints) — the one call that reads the hints
- [typing.get_args](https://devdocs.io/python~3.14/library/typing#typing.get_args) — split `str | None` into its parts

## Why
You inherit a library of infrastructure functions written by someone who left. Before calling one at 3am you want to know what it expects: the names of its inputs, which ones might be empty (None), and what comes back. The answers are written in the function's own signature as type hints, but stored as plain text. You need to read that text back into something you can check in code, an automated form of reading the docs.

## You get
`fn` — a function object with type hints, like

```python
def scale(replicas: int, zone: str | None) -> dict: ...
```

You must not call it. The test creates it and hands it to you; you never build it yourself.

## You return
a triple `(params, nullable, ret)`: a dict of input names to their types, a sorted list of the input names that may be `None`, and the return type.

## Rules
Report three facts about an annotated function's signature.

`fn` is a function you must not call. Its annotations are stored as plain strings, because the file it came from starts with `from __future__ import annotations` — check `fn.__annotations__` and you get `{"replicas": "int", ...}`, the source text, not types. Turning those strings into real type objects is a one-call job in the `typing` module.

Return the tuple `(params, nullable, ret)`:

- `params` — dict of parameter name → resolved annotation, in declaration order, with no `"return"` key
- `nullable` — sorted list of the PARAMETER names whose annotation admits `None`
- `ret` — the resolved annotation of the return value

```python
def scale(replicas: int, zone: str | None, tags: list[str]) -> dict[str, int]: ...

solve(scale)
# -> ({"replicas": int, "zone": str | None, "tags": list[str]},
#     ["zone"],
#     dict[str, int])
```

> [!WARNING]
> The return annotation can itself be nullable. It never belongs in the `nullable` list — that list is parameters only. The test also checks that `params` keeps declaration order.

`str | None` is the modern spelling of `Optional[str]`: this value is a `str` or it is missing. Spotting those is the practical payoff of reading hints, since they are the ones that will hand you a `None` at 3am.

## Hints
### Hint 1
Two separate problems. One: annotations arrive as strings and you need objects, so something has to evaluate them in the namespace of the module that defined the function. Two: once you have the objects, you need to ask of each one 'could this be None' — and a compound type like `str | None` has parts you can pull apart, while a plain `int` has none.
### Hint 2
`typing.get_type_hints(fn)` does the resolving and returns one dict holding the parameters AND the return, keyed `'return'`. Pop that key off first: it gives you `ret` and leaves `params` clean, in declaration order. Then `typing.get_args(t)` returns the pieces of a union — `(str, NoneType)` for `str | None` — and an empty tuple for anything that is not compound. So a parameter is nullable when `type(None)` is in `get_args` of its annotation. `sorted()` the names at the end.
### Hint 3
Different data — a two-parameter function:

```python
import typing

def f(host: str, port: int | None) -> bool: ...

print(f.__annotations__)          # under `from __future__ import
                                  # annotations`: {'host': 'str', ...}
hints = typing.get_type_hints(f)  # {'host': <class 'str'>,
                                  #  'port': int | None,
                                  #  'return': <class 'bool'>}
print(hints.pop('return'))        # <class 'bool'>, and hints is now
                                  # parameters only
print(typing.get_args(hints['port']))   # (<class 'int'>, <class 'NoneType'>)
print(typing.get_args(hints['host']))   # ()
```

Yours does the same over however many parameters it is handed.
