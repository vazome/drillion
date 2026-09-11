---
title: __init_subclass__ — a handler base that checks its subclasses as they are written
difficulty: hard
tier: advanced
minutes: 25
prereqs: [57, 203]
tags: [class-customization, class-inheritance]
---
# __init_subclass__ — a handler base that checks its subclasses as they are written

*`__init_subclass__` runs on the base class the moment a subclass finishes being defined, which is the earliest a mistake can be caught and the latest it is still cheap.*

## Read first
- [`__init_subclass__`](https://devdocs.io/python~3.14/reference/datamodel#object.__init_subclass__) — when it runs, what it gets, and why it needs no `@classmethod`
- [`type.__dict__`](https://devdocs.io/python~3.14/library/stdtypes#type.__dict__) — a class's own body, as opposed to what it inherited
- [`callable`](https://devdocs.io/python~3.14/library/functions#callable) — the cheapest way to ask whether something can be called

## Why
Events arrive from the queue tagged with a name, and something has to decide which piece of code deals with `image.uploaded`. Keeping that decision in one hand-written dictionary at the bottom of a module works until the day someone adds a handler and forgets the dictionary. Nothing breaks in review, nothing breaks in the tests they wrote, and the event goes unhandled in production for a fortnight.

Let the base class do the filing instead. Writing the handler is what registers it, so there is no second step to forget — and the same moment is the one where the base can insist the handler is actually usable: that it says which event it is for, that it has the method the dispatcher will call, and that it is not quietly stealing an event another handler already claimed. A class that fails those checks should not import, never mind run.

## You get
nothing to start — you return a class. The test builds subclasses of it itself, like

```python
Handler = solve()

class Resize(Handler):
    event = "image.uploaded"
    def handle(self, payload):
        return f"resizing {payload}"
```

## You return
the class `Handler`.

## Rules
- `Handler.registry` is a dict, empty to begin with, mapping an event name to the class that handles it. It lives on `Handler`, and every subclass shares the one dict.
- `__init_subclass__(cls, **kwargs)` runs for each subclass as its body finishes. Call `super().__init_subclass__(**kwargs)` first, then check, in any order, and raise `TypeError` on each failure:
  - the subclass's **own body** sets `event` to a non-empty `str`. Inheriting one from a parent does not count — a subclass of a handler is a different handler and has to say so.
  - the subclass has a callable `handle` attribute, whether it wrote one or inherited it.
  - no class is registered under that event already.
- A subclass that passes goes into the registry under its event.
- `Handler.dispatch(event, payload)` is a classmethod: build the registered class with no arguments and return `handle(payload)`. An unknown event raises `KeyError(event)`.

```python
Handler = solve()

class Resize(Handler):
    event = "image.uploaded"
    def handle(self, payload):
        return f"resizing {payload}"

Handler.registry            # -> {'image.uploaded': <class 'Resize'>}
Handler.dispatch("image.uploaded", "cat.png")   # -> 'resizing cat.png'
Handler.dispatch("nope", "x")                   # -> KeyError

class Broken(Handler):      # -> TypeError, at the class statement
    def handle(self, payload):
        return payload
```

> [!WARNING]
> Doing the checking in `__init__` passes any test that builds a handler and fails the one that matters: `Broken` above is never instantiated, so nothing ever raises, and the broken class ships. The test writes the class statement inside `pytest.raises` and creates no instance at all.

> [!NOTE]
> `__init_subclass__` is made a classmethod for you — writing `@classmethod` above it is not an error but it is not needed either, and its first argument is the *new* subclass, not `Handler`.

## Hints
### Hint 1
`Handler` itself never goes through `__init_subclass__`; the hook fires for subclasses only, which is why the registry starts empty and why the base does not need an `event` of its own.
### Hint 2
"Its own body" is `"event" in cls.__dict__` — `getattr(cls, "event", None)` finds the parent's and would let a grandchild register under an event it never named. `handle` is the opposite case: `getattr` is right there, because inheriting it is fine.
### Hint 3
Same shape, different rule:

```python
class Command:
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = cls.__dict__.get("name")
        if not isinstance(name, str) or not name:
            raise TypeError(f"{cls.__name__} must set its own name")
        cls.registry[name] = cls

class Deploy(Command):
    name = "deploy"

Command.registry     # -> {'deploy': <class 'Deploy'>}
```

The registry fills itself, and the class that forgets its name never finishes being defined.
