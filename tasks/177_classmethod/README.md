---
title: classmethod and staticmethod — a second way to build one
difficulty: medium
tier: core
minutes: 15
prereqs: [57]
tags: [classes, class-customization]
---
# classmethod and staticmethod — a second way to build one

*`@classmethod` gets the class and can return a new instance of it. `@staticmethod` gets nothing and just lives here.*

## Read first
- [classmethod()](https://devdocs.io/python~3.14/library/functions#classmethod) — a method whose first argument is the class, not the instance
- [staticmethod()](https://devdocs.io/python~3.14/library/functions#staticmethod) — a plain function that lives in the class's namespace because that is where it belongs
- [Class and Instance Variables](https://devdocs.io/python~3.14/tutorial/classes#class-and-instance-variables) — the difference the two decorators turn on

## Why
Your deploy records arrive two ways: built in code with the fields you already have, or parsed out of a line the CI system wrote. Writing a module-level `parse_deploy()` next to the class means the two halves drift apart and someone eventually parses into a dict instead. An alternative constructor keeps the parsing attached to the thing it builds, and reads at the call site as what it is: `Deploy.from_line(...)`.

## You get
nothing to start — you return the class. The test uses it like

```python
Deploy = solve()
Deploy.from_line("api 1.4.2 ok")
Deploy.is_semver("1.4.2")
```

## You return
the class `Deploy`.

## Rules
- `__init__(self, service, version, status)` stores all three under those names.
- `__repr__` returns exactly `f"Deploy({self.service}, {self.version}, {self.status})"`.
- `from_line(line)` is a **classmethod**: it splits a line like `"api 1.4.2 ok"` into three fields and returns a new instance built from them. It must build through the class it was called on, not by naming `Deploy` directly.
- `is_semver(version)` is a **staticmethod**: `True` when the string is three dot-separated runs of digits, e.g. `"1.4.2"`, `False` otherwise. It takes no `self` and no `cls`.

```python
Deploy = solve()
repr(Deploy.from_line("api 1.4.2 ok"))   # -> "Deploy(api, 1.4.2, ok)"
Deploy.is_semver("1.4")                  # -> False
Deploy.is_semver("2.0.11")               # -> True
```

> [!WARNING]
> The test subclasses your class and calls `from_line` on the subclass. A `from_line` that returns `Deploy(...)` by name gives back the wrong type; one that returns `cls(...)` gives back the subclass, which is the reason the decorator exists.

## Hints
### Hint 1
`@classmethod` above the definition, and `cls` as the first parameter instead of `self`. Inside, `cls(...)` calls whatever class the method was reached through.
### Hint 2
`@staticmethod` above the definition, and no first parameter at all. `is_semver` never touches an instance, so it takes only the version string.
### Hint 3
Different data, same shape:

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    @classmethod
    def from_text(cls, s):
        x, y = s.split(",")
        return cls(int(x), int(y))
    @staticmethod
    def is_pair(s):
        return s.count(",") == 1

class Point3(Point): pass
print(type(Point3.from_text("1,2")).__name__)   # Point3
```

`cls` is what makes the last line say `Point3` and not `Point`.
