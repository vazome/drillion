---
title: operator — itemgetter, attrgetter and methodcaller instead of three throwaway lambdas
difficulty: medium
tier: core
minutes: 15
prereqs: [12, 58]
tags: [sorted, stdlib-ops]
---
# operator — itemgetter, attrgetter and methodcaller instead of three throwaway lambdas

*Three functions that build the callable you were about to write by hand, and one of them sorts by several fields at once for free.*

## Read first
- [`operator.itemgetter`](https://devdocs.io/python~3.14/library/operator#operator.itemgetter) — index or key, and what several of them return
- [`operator.attrgetter`](https://devdocs.io/python~3.14/library/operator#operator.attrgetter) — the same for attributes, dotted names included
- [`operator.methodcaller`](https://devdocs.io/python~3.14/library/operator#operator.methodcaller) — call one named method, with the arguments baked in

## Why
A weekly report joins two feeds: objects from the deploy API and rows from a CSV export that nobody has got round to parsing properly. Sorting and plucking from both ends up as a scatter of `lambda x: x[1]` and `lambda r: r.region`, and a lambda is where a reader has to stop and work out which field is meant and whether the tie-break is the one intended. `operator` names the three shapes that cover almost all of it, and the multi-field version is the part worth having: `attrgetter("region", "service")` is one sort with a tie-break you can read, where two separate `sorted` calls or a single-field key is the bug that only shows up once two rows share a region.

## You get
- `runs`, a list of `Run` objects. `Run` is a frozen dataclass given to you above `solve`, with `service`, `region` and `seconds`.
- `rows`, a list of `(service, region, seconds)` tuples from the CSV export. Same kind of data, not yet objects, and not the same rows.

Service names all start with the prefix `svc-`.

## You return
a dict with exactly these four keys:

| key | value |
|---|---|
| `by_region` | every run's `service`, with the runs ordered by `region` then by `service` |
| `slowest` | the `service` of the run with the largest `seconds` |
| `short_names` | every run's `service` with the `svc-` prefix removed, in the order `runs` came in |
| `rows_sorted` | `rows`, ordered by `region` then by `seconds`, as a list of tuples |

## Rules
- `by_region` and `rows_sorted` are ordered by two fields, not one. Regions repeat, and so do durations — a key that names only the first field leaves the rest in whatever order the input happened to be, and that is not the order asked for.
- `slowest` breaks a tie by taking the first such run in `runs`.
- `short_names` strips the prefix and nothing else: a service called `svc-svc-api` becomes `svc-api`.
- `rows_sorted` holds the tuples you were given, unchanged, and `rows` itself is left in its original order.
- No `lambda`, and no helper function of your own. Each of the four values is one call with `itemgetter`, `attrgetter` or `methodcaller` doing the work.

```python
runs = [Run("svc-api", "eu", 9.0), Run("svc-db", "eu", 2.0), Run("svc-cdn", "us", 4.0)]
solve(runs, [("svc-api", "eu", 9.0), ("svc-db", "eu", 2.0)])
# -> {'by_region': ['svc-api', 'svc-db', 'svc-cdn'],
#     'slowest': 'svc-api',
#     'short_names': ['api', 'db', 'cdn'],
#     'rows_sorted': [('svc-db', 'eu', 2.0), ('svc-api', 'eu', 9.0)]}
```

> [!NOTE]
> `itemgetter(1)` returns one value and `itemgetter(1, 2)` returns a tuple of two, which is exactly what a multi-field sort key has to be. It is the same rule for `attrgetter`.

## Hints
### Hint 1
`sorted` takes one `key` callable, and a tuple key sorts by its first element, then its second where the first ties. The getters build that tuple for you when you pass them more than one field.
### Hint 2
`methodcaller("removeprefix", "svc-")` is a function of one argument that calls `.removeprefix("svc-")` on whatever you hand it, which makes it the function `map` wants.
### Hint 3
All three, on other data:

```python
from operator import attrgetter, itemgetter, methodcaller

pairs = [("b", 2), ("a", 2), ("c", 1)]
sorted(pairs, key=itemgetter(1, 0))            # -> [('c', 1), ('a', 2), ('b', 2)]
list(map(itemgetter(0), pairs))                # -> ['b', 'a', 'c']
max(pairs, key=itemgetter(1))                  # -> ('b', 2), the first of the two 2s

list(map(methodcaller("upper"), "ab"))          # -> ['A', 'B']
sorted(tzs, key=attrgetter("offset", "name"))  # attrgetter reaches attributes, itemgetter reaches items
```

`max` with a key returns the first maximum it meets, so the tie-break is already the one the task asks for.
