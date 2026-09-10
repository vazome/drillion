---
title: abstract base classes — a plugin base that refuses to be half-built
difficulty: medium
tier: advanced
minutes: 20
prereqs: [173]
tags: [class-inheritance, class-customization]
source: fluentpython/example-code-2e 13-protocol-abc (MIT, adapted)
---
# abstract base classes — a plugin base that refuses to be half-built

*An abstract base class names what every subclass must supply, and Python refuses to build one that did not.*

## Read first
- [`abc`](https://devdocs.io/python~3.14/library/abc) — `ABC`, `@abstractmethod`, and what makes a class abstract
- [`abstractmethod`](https://devdocs.io/python~3.14/library/abc#abc.abstractmethod) — why a subclass that skips one cannot be instantiated
- [`property`](https://devdocs.io/python~3.14/library/functions#property) — stacking it with `@abstractmethod` to require an attribute rather than a call

## Why
Your alerting has several backends, and each one has to do two things: hand a finished line to whatever actually sends it, and say what it is called so the log names it. Everything else — how a service and a message become one line, how the description reads — is the same for all of them and belongs in one place. The failure worth designing against is the backend somebody adds in a hurry and half-finishes. Without a base that enforces the contract, that class imports cleanly, registers cleanly, and raises `AttributeError` the first time an alert fires, which is by definition the worst moment. An abstract base moves that failure to the line that tries to build it.

## You get
nothing to start — you return classes. The test builds them itself, and it builds its own subclasses of yours, like

```python
Backend, Pager = solve()
Pager().notify("api", "disk full")
```

## You return
a tuple of the two classes, in the order `(Backend, Pager)`.

## Rules
`Backend` is the abstract base:

- It inherits from `abc.ABC`.
- `deliver(self, text)` is abstract: every backend supplies it, and it returns the line it sent.
- `name` is an abstract **property**: every backend supplies it, and it is read as an attribute rather than called.
- `notify(self, service, text)` is concrete, and every subclass inherits it. It calls `self.deliver` with `f"[{service}] {text}"` and returns the result.
- `describe(self)` is concrete too, and returns `self.name` followed by `" backend"`.

`Pager(Backend)` is one real backend:

- `name` is `"pager"`. A plain class attribute satisfies an abstract property.
- `deliver(self, text)` returns `"PAGE "` followed by the text.
- It defines nothing else. Inheriting `notify` and `describe` is the point.

```python
Backend, Pager = solve()
Pager().notify("api", "disk full")  # -> "PAGE [api] disk full"
Pager().describe()                  # -> "pager backend"
Backend()                           # -> TypeError
```

> [!WARNING]
> The test writes its own subclass of your `Backend` that supplies `deliver` and forgets `name`, and expects `TypeError` when it is built. A base that only documents the contract in a docstring, or raises `NotImplementedError` from the body, passes neither that check nor the `Backend()` one.

## Hints
### Hint 1
`class Backend(abc.ABC):` is what makes the machinery run at all. `@abc.abstractmethod` on a method inside it is what records the requirement, and Python refuses to instantiate any class that still has an unmet one.
### Hint 2
For an abstract attribute rather than an abstract method, stack the decorators with `@property` on the outside:

```python
@property
@abc.abstractmethod
def name(self): ...
```

A subclass can satisfy it with `name = "pager"`, because what is checked is that the name is defined, not how.
### Hint 3
Same shape, different contract:

```python
import abc

class Exporter(abc.ABC):
    @abc.abstractmethod
    def render(self, rows): ...

    def save(self, rows):
        return f"wrote {len(self.render(rows))} chars"

class Csv(Exporter):
    def render(self, rows):
        return "\n".join(",".join(r) for r in rows)

Csv().save([["a", "b"]])   # 'wrote 3 chars'
Exporter()                 # TypeError: Can't instantiate abstract class
```

`Csv` never writes `save`, and `Exporter` can never be built on its own.

---
Adapted from fluentpython/example-code-2e — MIT
