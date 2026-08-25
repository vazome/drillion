---
title: classes — __init__, __repr__, @property
minutes: 12
prereqs: []
tags: [core]
---
# classes — __init__, __repr__, @property

*A class bundles state with the things derived from it, and @property keeps them honest.*

## Why
Your cluster runs services, each with a name, a number of copies (replicas) and a CPU budget per copy. Capacity planning asks "how much CPU does each service use in total?", and that total changes whenever someone scales a service up or down. If you work it out once and store it, it goes stale; it has to be recomputed every time it is asked for. Bundling the facts and the derived figure together is what a class is for.

## You get
`name` — a service name like `"api-blue"`. `replicas` — a count like `3`. `cpu` — CPU per copy, like `250`. The test creates them and hands them to you; you never build them yourself.

## You return
one `Service` object built from those three values, with a readable printed form and a `total_cpu` figure that is always up to date.

## Rules
Define a class called `Service`, then return `Service(name, replicas, cpu)`.

Write the class wherever you like — top level of this file, or inside `solve`. It must have:

- `__init__(self, name, replicas, cpu)` storing all three under those same attribute names
- `__repr__` returning exactly `f"Service(name={self.name!r}, replicas={self.replicas}, cpu={self.cpu})"`, so `repr` looks like `Service(name='api-blue', replicas=3, cpu=250)`
- `total_cpu`, a property giving `replicas * cpu` — read as `s.total_cpu` with no parentheses, recomputed on every read

```python
s = solve("api-blue", 3, 250)
s.total_cpu     # -> 750
s.replicas = 4
s.total_cpu     # -> 1000
repr(s)         # -> "Service(name='api-blue', replicas=4, cpu=250)"
```

> [!WARNING]
> Do not compute `total_cpu` in `__init__` and store it. A stored copy goes stale the moment `replicas` changes, and that staleness is the entire reason `@property` exists. The test bumps `replicas` and looks again.

## Hints
### Hint 1
Three jobs that people mix up. `__init__` takes what the caller passed and parks it on `self` — it does not compute anything derived. `__repr__` is for you and your logs, and the convention is that it reads like the constructor call that would rebuild the object. A property is a method that lies about being a method: callers see an attribute, but code runs on every read, so it can never disagree with the fields it derives from.
### Hint 2
`class Service:` with `def __init__(self, name, replicas, cpu)` assigning `self.name` and friends. `def __repr__(self)` returning the f-string — note the `!r` on the name, which is what puts the quotes around it. Then `def total_cpu(self)` with `@property` on the line above and `return self.replicas * self.cpu` inside. Because it is a property you write no parentheses at the call site, and because you never defined a setter, assigning to it raises `AttributeError`, which the test checks.
### Hint 3
Different data — a disk with a derived free-space figure:

```python
class Disk:
    def __init__(self, path, size_gb, used_gb):
        self.path = path
        self.size_gb = size_gb
        self.used_gb = used_gb

    def __repr__(self):
        return f"Disk(path={self.path!r}, size_gb={self.size_gb})"

    @property
    def free_gb(self):
        return self.size_gb - self.used_gb

d = Disk('/var', 100, 60)
print(d.free_gb)      # 40      <- no parentheses
d.used_gb = 90
print(d.free_gb)      # 10      <- recomputed, never stale
print(d)              # Disk(path='/var', size_gb=100)
```

Same three pieces, different nouns.
