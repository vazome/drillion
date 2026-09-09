---
title: type hints — return an annotated row indexer
difficulty: medium
tier: core
minutes: 15
prereqs: [17, 47]
tags: [enumerate-zip, type-hints]
---
# type hints — return an annotated row indexer

*Write the signature another tool can inspect, then number and pair the data.*

## Read first
- [Annotations](https://devdocs.io/python~3.14/tutorial/controlflow#function-annotations) — metadata on parameters and returns
- [enumerate](https://devdocs.io/python~3.14/library/functions#enumerate) — pair each row with a one-based number
- [zip](https://devdocs.io/python~3.14/library/functions#zip) — pair headers with cells

## Why
A CSV-like importer needs numbered dictionaries and an exact callable type for a plugin registry. The annotations are part of the interface: the registry reads them at runtime before accepting the function.

## You get
Nothing is passed to `solve`; the grader calls the annotated function you return with headers and rows.

## You return
From `solve`, return a function named however you like with this annotated shape:

```python
def index_rows(
    headers: list[str], rows: list[list[str]]
) -> list[tuple[int, dict[str, str]]]:
    ...
```

## Rules
For each row, use `zip(headers, row)` to build its dictionary and `enumerate(rows, start=1)` for its number. Return `(number, dictionary)` pairs in input order. The grader checks both behavior and `typing.get_type_hints`.

## Hints
### Hint 1
Annotations go on the returned inner function, because that is the callable the registry receives.
### Hint 2
`dict(zip(headers, row))` turns the two aligned lists into one record.
### Hint 3
Return a list comprehension over `enumerate(rows, start=1)`, then return the inner function itself from `solve` without calling it.
