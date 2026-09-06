---
title: inheritance — one base class, two specialised alerts
difficulty: medium
tier: core
minutes: 20
prereqs: [57]
tags: [classes, class-inheritance]
---
# inheritance — one base class, two specialised alerts

*`super()` calls the version you are replacing, so a subclass adds to the base instead of copying it.*

## Read first
- [Inheritance](https://devdocs.io/python~3.14/tutorial/classes#inheritance) — `class Child(Parent):`, and what a subclass inherits without writing anything
- [super()](https://devdocs.io/python~3.14/library/functions#super) — how a method reaches the version it just overrode, including inside `__init__`
- [isinstance()](https://devdocs.io/python~3.14/library/functions#isinstance) — why a real subclass passes a check that a look-alike class fails

## Why
Every alert your platform sends has the same skeleton: which service it came from, and what happened. The pager adds a shout at the front so a woken engineer sees it first, and email adds a recipient at the end. Copying the skeleton into three classes means a change to the common part has to be made three times, and the day one copy is missed the pager renders differently from email for no reason anybody can explain. One base class holds the shared shape, and each subclass says only what it adds.

## You get
nothing to start — you return classes. The test builds them itself, like

```python
Alert, PagerAlert, EmailAlert = solve()
PagerAlert("api", "disk full").render()
```

## You return
a tuple of the three classes, in the order `(Alert, PagerAlert, EmailAlert)`.

## Rules
`Alert` is the base:

- `__init__(self, service, text)` stores both under those names.
- `prefix(self)` returns `f"[{self.service}]"`.
- `render(self)` returns `f"{self.prefix()} {self.text}"`.

`PagerAlert(Alert)` changes the prefix and nothing else:

- `prefix(self)` returns `"PAGE "` followed by whatever the base's `prefix` returned.
- It must NOT define its own `render`. Inheriting it is the point: changing `prefix` is what changes the rendered line.

`EmailAlert(Alert)` adds a recipient:

- `__init__(self, service, text, to)` stores `to` as well, and lets the base store the other two rather than assigning them again.
- `render(self)` returns the base's rendered line, then `" -> "`, then the recipient.

```python
Alert, PagerAlert, EmailAlert = solve()
Alert("api", "disk full").render()                  # -> "[api] disk full"
PagerAlert("api", "disk full").render()             # -> "PAGE [api] disk full"
EmailAlert("api", "disk full", "ops@x.io").render() # -> "[api] disk full -> ops@x.io"
```

> [!WARNING]
> Three classes that merely produce the right strings are not enough. The test checks `isinstance(PagerAlert("a", "b"), Alert)` and that `PagerAlert` did not define `render` of its own, so a copy-paste of the base fails even when every line comes out right.

## Hints
### Hint 1
`class PagerAlert(Alert):` is the whole of "inherits from". Anything you do not write inside it, it gets from `Alert` — which is why `PagerAlert` needs no `render` and no `__init__` at all.
### Hint 2
Inside an overriding method, `super()` is the base's version of the object. `super().prefix()` runs `Alert.prefix` on the same instance, so `return "PAGE " + super().prefix()` builds on it. In `EmailAlert.__init__`, call `super().__init__(service, text)` first, then store `self.to = to`.
### Hint 3
Different data, same shape:

```python
class Box:
    def __init__(self, size):
        self.size = size
    def label(self):
        return f"box({self.size})"

class Fragile(Box):
    def label(self):
        return "FRAGILE " + super().label()

print(Fragile(3).label())          # FRAGILE box(3)
print(isinstance(Fragile(3), Box)) # True
```

`Fragile` never repeats `__init__` or the `box(...)` text, and both come from the base.
