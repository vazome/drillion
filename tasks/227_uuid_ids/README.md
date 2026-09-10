---
title: uuid — one id that never changes, one that never repeats
difficulty: easy
tier: core
minutes: 12
prereqs: [76]
tags: [stdlib-ops]
---
# uuid — one id that never changes, one that never repeats

*`uuid4()` invents an id out of randomness; `uuid5()` derives one from a name, so the same name always produces the same id.*

## Read first
- [`uuid`](https://devdocs.io/python~3.14/library/uuid) — the module, and the five versions it can make
- [`uuid.uuid5`](https://devdocs.io/python~3.14/library/uuid#uuid.uuid5) — a name plus a namespace, hashed into an id
- [`uuid.UUID`](https://devdocs.io/python~3.14/library/uuid#uuid.UUID) — the object, and its `version` attribute

## Why
The asset service has two id problems and only one of them is solved by a random number. Every asset needs a permanent id that four different services can work out on their own from the asset's name, without asking a database and without agreeing on a counter — import it twice and it has to land on the same row, not a duplicate. Every upload *attempt* needs an id too, but that one must never collide with anything, ever, including the retry of the same upload thirty seconds later. Reach for the random id in the first case and re-importing the catalogue quietly doubles it. Reach for the derived id in the second and two retries of the same upload overwrite each other's logs.

## You get
`names`, a list of asset names as strings, and `ASSET_NS`, the URL prefix an asset name hangs off, already defined for you.

## You return
a tuple `(stable, session)` of two dicts, each keyed by the same names.

- `stable[name]` is the derived id: a version 5 UUID in the URL namespace, built from `ASSET_NS + name`, as a string.
- `session[name]` is a fresh random version 4 UUID, as a string.

## Rules
- Both dicts hold `str`, not `UUID` objects. `str(u)` is the dashed form.
- The namespace for the derived id is `uuid.NAMESPACE_URL`, and the name fed to it is the whole URL — the prefix concatenated with the asset name, not the asset name alone.
- Call `solve` twice with the same list and every entry in `stable` must come back identical. That is the entire point of it.
- Call `solve` twice and no entry in `session` may repeat, either within one call or across the two.

```python
ASSET_NS = "https://drillion.example/asset/"
stable, session = solve(["hero-banner", "hero-banner-2x"])
stable["hero-banner"]   # -> the same string on every machine, forever
session["hero-banner"]  # -> a different string every single call
```

> [!WARNING]
> A random id looks correct in every test you write by hand, because you only ever look at one run. The failure only appears the second time the importer runs, in production, as duplicated rows nobody ordered.

## Hints
### Hint 1
`uuid.uuid4()` takes no arguments and asks the operating system for randomness. `uuid.uuid5(namespace, name)` takes two and does no guessing at all: it hashes them, so the answer is a pure function of what you passed in.
### Hint 2
The namespace constants live on the module itself — `uuid.NAMESPACE_URL`, `uuid.NAMESPACE_DNS` and two more. They exist so that the same name in two different namespaces cannot collide.
### Hint 3
Every `UUID` object knows which version made it:

```python
import uuid

u = uuid.uuid5(uuid.NAMESPACE_DNS, "python.org")
u.version           # -> 5
str(u)              # -> '886313e1-3b8a-5372-9b90-0c9aee199e5d'
uuid.uuid4().version # -> 4
```

Two dict comprehensions over `names` is the whole solution.
