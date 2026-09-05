---
title: functools — lru_cache proven by counting, wraps keeps the name
difficulty: medium
tier: advanced
minutes: 12
prereqs: [20]
tags: [functools]
---
# functools — lru_cache proven by counting, wraps keeps the name

*lru_cache is the cheapest speedup in Python; wraps is why your wrapper keeps its name.*

## Why
A pricing function is slow, and a billing report calls it thousands of times with only a handful of different inputs. The same answer is recomputed over and over. You want to remember each answer the first time and reuse it after that. At the same time, wrapping the function must not change its name or description, or the logs and error messages will start naming a function that does not exist.

## You get
`fn` — a function that takes one value and always gives the same answer for the same input, like `cost(3)`. The test creates it and hands it to you; you never build it yourself.

## You return
a wrapped version of `fn` that gives the same answers, runs the real `fn` only once per distinct input, and still reports the original name and docstring.

## Rules
Return a memoised version of `fn` that still looks like `fn`.

`fn` takes one hashable argument and is pure: same input, same output. Return a wrapper where:

- `wrapper(x)` gives the same answer `fn(x)` would
- `fn` itself runs at most once per distinct `x`, no matter how many times the wrapper is called with it
- `wrapper.__name__ == fn.__name__` and `wrapper.__doc__ == fn.__doc__`

```python
cost = solve(cost)
cost(3), cost(3), cost(7), cost(3)   # the real cost ran twice: 3 and 7
cost.__name__                        # -> "cost", not "wrapper"
```

> [!WARNING]
> That last rule is not decoration. A hand-written wrapper replaces the name and docstring of whatever it wraps, so tracebacks, logs and `help()` all start naming a function nobody wrote. `functools` has a decorator that copies those attributes across, and the caching one applies it for you.

There are only a handful of distinct inputs here. Cache all of them, evict nothing.

## Hints
### Hint 1
Memoising is a dict from arguments to results, and you have written that before by hand. The point of this task is that you should not: `functools` has it, one line, thread-safe, with a hit/miss counter attached. The second half of the task is the tax every wrapper pays — the wrapper is a different function object from the one it replaced, so it arrives with the wrong identity unless you fix it.
### Hint 2
`from functools import lru_cache`. `lru_cache(maxsize=None)(fn)` returns the cached wrapper — that is the decorator applied as a plain call, which is all `@lru_cache(maxsize=None)` means. `functools.cache` is the same thing under a shorter name. Either one calls `functools.wraps` for you, so `__name__` and `__doc__` survive without extra work. If you would rather hand-roll the dict, you must put `@wraps(fn)` on your inner function yourself or the name check fails.
### Hint 3
Different data — squaring, with the real calls logged:

```python
from functools import lru_cache, wraps

hits = []

@lru_cache(maxsize=None)
def square(n):
    hits.append(n)
    return n * n

print(square(4), square(4), square(5))   # 16 16 25
print(hits)                              # [4, 5]  <- the 4 ran once
print(square.__name__)                   # 'square'
print(square.cache_info())               # hits=1, misses=2

def loud(f):                  # the hand-rolled shape, for contrast
    @wraps(f)                 # delete this line and inner.__name__
    def inner(*a, **kw):      # becomes 'inner' — the name is gone
        return f(*a, **kw)
    return inner
```

Only cache pure functions. Cache something that reads a file or a clock and you have built a bug that only shows up in production.
