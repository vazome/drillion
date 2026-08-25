---
title: decorators — record every call, pass everything through
minutes: 12
prereqs: [8]
tags: [core, rsample]
---
# decorators — record every call, pass everything through

*A decorator wraps a function in another function — the whole trick is that.*

## Why
An audit team asks: "every time one of our infrastructure tools changes something, we need a record of what was called, with what arguments, and what it returned." The tools are dozens of existing functions and nobody wants to edit each one. You need a single reusable wrapper that can be stuck on any function and quietly logs each call while leaving the function's behaviour exactly as it was.

## You get
`calls` — an empty list like `[]`. Your wrapper appends one record to it per call. The test creates it and hands it to you; you never build it yourself.

## You return
a decorator: a thing that takes a function and gives back a replacement function that behaves the same but also appends `(name, args, kwargs, result)` to `calls` after each call.

## Rules
Return a decorator that records every call into the list `calls`.

`solve(calls)` gives you back a decorator. That decorator takes a function and returns a replacement for it. The replacement must:

- accept any arguments at all and hand them to the original unchanged
- return exactly what the original returned
- append one entry to `calls`, in this shape: `(fn.__name__, args, kwargs, result)` — `args` is the positional tuple, `kwargs` the keyword dict, `result` the value the original returned

```python
calls = []
record = solve(calls)

@record
def scale(host, replicas=1):
    return f"{host}:{replicas}"

scale("api", replicas=3)   # -> "api:3", unchanged
calls                      # -> [("scale", ("api",), {"replicas": 3}, "api:3")]
```

The entry goes in after the call, not before — you need the result. Record `args` and `kwargs` as you received them; do not merge, sort or normalise them.

## Read first
- [Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/) — `@app.get(...)` and `@pytest.fixture` are decorators; this is how they work
- [decorator — Python glossary](https://docs.python.org/3/glossary.html#term-decorator) — the one-sentence definition to quote back in an interview

> [!NOTE]
> **Take-home:** `@app.get("/search")`, `@pytest.fixture`

## Hints
### Hint 1
Three nested layers, and the confusion is always about which layer runs when. The outer call captures the list. The middle one runs once, at decoration time, and is handed the function. The inner one runs on every single call and is the thing callers actually reach. Sketch the three `def`s and what each one returns before filling in any bodies.
### Hint 2
`def solve(calls):` → `def record(fn):` → `def wrapper(*args, **kwargs): ...` ; `return wrapper` ; `return record`. Inside `wrapper`: call `fn(*args, **kwargs)` and keep the value in a variable, append the tuple to `calls`, then return the variable. `*args` and `**kwargs` collect anything on the way in and re-spread it on the way out. `fn.__name__` is the original's name, and `wrapper` can still see `fn` and `calls` because of closures.
### Hint 3
Different data — a decorator that doubles whatever comes back:

```python
def doubler(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs) * 2
    return wrapper

@doubler
def add(a, b=0):
    return a + b

print(add(3, b=4))     # 14 — @doubler means add = doubler(add)
```

That one has two layers because it takes no configuration. Yours has three, because `solve` takes the list first and only then meets the function.
