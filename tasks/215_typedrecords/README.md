---
title: NamedTuple and TypedDict — the record you hold and the shape you send
difficulty: medium
tier: advanced
minutes: 20
prereqs: [57, 58]
tags: [type-hints, tuples, dicts]
---
# NamedTuple and TypedDict — the record you hold and the shape you send

*A `NamedTuple` is a real object with named fields. A `TypedDict` is a plain dict that a type checker knows the keys of. They look similar and they are for opposite ends of the same trip.*

## Read first
- [`typing.NamedTuple`](https://devdocs.io/python~3.14/library/typing#typing.NamedTuple) — fields, defaults, and everything it inherits from `tuple`
- [`typing.TypedDict`](https://devdocs.io/python~3.14/library/typing#typing.TypedDict) — annotating the keys of a dictionary
- [`json.dumps`](https://devdocs.io/python~3.14/library/json#json.dumps) — what the wire will and will not accept

## Why
A weather station reading lives two lives. Inside the program it is a thing: you pass it around, compare it, sort it, and nobody should be able to move a station 200 miles by assigning to a field. Over the wire it is a JSON object, because that is what the collector on the other end parses, and JSON has no records — only dicts, lists, numbers and strings.

Reach for one type for both jobs and you get the worst of each. A dict everywhere means `reading["lattitude"]` typos that surface in production as `None`. A record everywhere means somebody eventually serialises a tuple and the collector receives `["Kew", 51.48]` with the names gone. Two declarations, one at each end, and the function between them is the only place the translation happens.

## You get
nothing to start — you return two classes and a function. The test builds them itself, like

```python
Station, Payload, to_payload = solve()
to_payload(Station("Kew", 51.48, -0.29))
```

## You return
a tuple of `(Station, Payload, to_payload)`.

## Rules
- `Station` is a `typing.NamedTuple` with four fields, in this order: `name: str`, `lat: float`, `lon: float`, `reference: str` defaulting to `"WGS84"`.
- `Payload` is a `typing.TypedDict` with two keys: `station: str` and `coords: list[float]`.
- `to_payload(station)` returns a `Payload` built from a `Station`: `station` is the name, and `coords` is a two-item list, latitude then longitude. The reference does not travel.

```python
Station, Payload, to_payload = solve()

kew = Station("Kew", 51.48, -0.29)
kew.lat                  # -> 51.48
kew.reference            # -> 'WGS84'
kew == ("Kew", 51.48, -0.29, "WGS84")   # -> True, it is a tuple
name, lat, lon, ref = kew               # unpacks like one too

to_payload(kew)          # -> {'station': 'Kew', 'coords': [51.48, -0.29]}
```

> [!WARNING]
> A `@dataclass` gives you named fields and a nice `repr`, and it passes every example above except the two that matter: it is not a `tuple`, so it will not unpack and it will not compare equal to one. The test checks both.

> [!NOTE]
> `Payload(station="Kew", coords=[51.48, -0.29])` returns an ordinary `dict` — `TypedDict` creates no class of its own at run time and checks nothing when you call it. The checking is a type checker's job. A plain dict literal is just as correct here; the declaration is what documents the keys.

## Hints
### Hint 1
Both are written as a class body of annotations and nothing else. `class Station(NamedTuple):` then one `name: type` line per field; the one with a default is written `reference: str = "WGS84"` and, like any default, has to come last.
### Hint 2
`to_payload` is one `return` of a dict with two keys. Build the list yourself — `[station.lat, station.lon]` — because the order is part of the contract and a tuple is not JSON.
### Hint 3
Same shape, different rule:

```python
from typing import NamedTuple, TypedDict

class Job(NamedTuple):
    name: str
    attempts: int
    queue: str = "default"

class JobEvent(TypedDict):
    job: str
    attempts: int

def to_event(job: Job) -> JobEvent:
    return {"job": job.name, "attempts": job.attempts}

to_event(Job("resize", 2))   # -> {'job': 'resize', 'attempts': 2}
```

The record keeps the queue, because the scheduler needs it. The event drops it, because the dashboard does not.
