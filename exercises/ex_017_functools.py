"""lru_cache is the cheapest speedup in Python; wraps is why your wrapper keeps its name."""

from _lib import rng

META = {"topic": 17, "title": "functools — lru_cache proven by counting, wraps keeps the name", "tier": 3,
        "minutes": 12, "prereqs": [12]}


def solve(fn):
    """Return a memoised version of fn that still looks like fn.

    fn takes one hashable argument and is pure: same input, same output. Return
    a wrapper where:

      - wrapper(x) gives the same answer fn(x) would
      - fn itself runs at most once per distinct x, no matter how many times
        the wrapper is called with it
      - wrapper.__name__ == fn.__name__ and wrapper.__doc__ == fn.__doc__

        cost = solve(cost)
        cost(3), cost(3), cost(7), cost(3)   # the real cost ran twice: 3 and 7
        cost.__name__                        # still "cost", not "wrapper"

    That last rule is not decoration. A hand-written wrapper replaces the name
    and docstring of whatever it wraps, so tracebacks, logs and help() all start
    naming a function nobody wrote. functools has a decorator that copies those
    attributes across, and the caching one applies it for you.

    There are only a handful of distinct inputs here. Cache all of them, evict
    nothing.
    """
    raise NotImplementedError


HINTS = [
    "Memoising is a dict from arguments to results, and you have written that "
    "before by hand. The point of this drill is that you should not: functools "
    "has it, one line, thread-safe, with a hit/miss counter attached. The "
    "second half of the drill is the tax every wrapper pays — the wrapper is a "
    "different function object from the one it replaced, so it arrives with the "
    "wrong identity unless you fix it.",
    "from functools import lru_cache. lru_cache(maxsize=None)(fn) returns the "
    "cached wrapper — that is the decorator applied as a plain call, which is "
    "all @lru_cache(maxsize=None) means. functools.cache is the same thing "
    "under a shorter name. Either one calls functools.wraps for you, so "
    "__name__ and __doc__ survive without extra work. If you would rather "
    "hand-roll the dict, you must put @wraps(fn) on your inner function "
    "yourself or the name check fails.",
    "Different data — squaring, with the real calls logged:\n"
    "    from functools import lru_cache, wraps\n"
    "\n"
    "    hits = []\n"
    "\n"
    "    @lru_cache(maxsize=None)\n"
    "    def square(n):\n"
    "        hits.append(n)\n"
    "        return n * n\n"
    "\n"
    "    print(square(4), square(4), square(5))   # 16 16 25\n"
    "    print(hits)                              # [4, 5]  <- the 4 ran once\n"
    "    print(square.__name__)                   # 'square'\n"
    "    print(square.cache_info())               # hits=1, misses=2\n"
    "\n"
    "    def loud(f):                  # the hand-rolled shape, for contrast\n"
    "        @wraps(f)                 # delete this line and inner.__name__\n"
    "        def inner(*a, **kw):      # becomes 'inner' — the name is gone\n"
    "            return f(*a, **kw)\n"
    "        return inner\n"
    "Only cache pure functions. Cache something that reads a file or a clock "
    "and you have built a bug that only shows up in production.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    """Parameters for one pure function, plus the call sequence to replay."""
    k, b = r.randint(2, 9), r.randint(1, 50)
    name = r.choice(["cost", "lookup", "resolve", "weight", "price", "score"])
    doc = f"{name}: {r.choice(['linear', 'flat', 'tiered'])} model, k={k}."
    distinct = r.sample(range(1, 40), r.randint(3, 6))
    args = [r.choice(distinct) for _ in range(r.randint(8, 16))]
    return k, b, name, doc, args


def _pure(k, b, name, doc):
    """The function under test, plus the log of calls that really reached it."""
    calls = []

    def f(x):
        calls.append(x)
        return x * k + b

    f.__name__ = name
    f.__doc__ = doc
    return f, calls


def _reference(fn):
    from functools import lru_cache

    return lru_cache(maxsize=None)(fn)


def test_solve():
    r = rng()
    for _ in range(4):
        k, b, name, doc, args = _gen(r)

        fn, calls = _pure(k, b, name, doc)
        ref_fn, ref_calls = _pure(k, b, name, doc)
        wrapped, reference = solve(fn), _reference(ref_fn)

        assert [wrapped(a) for a in args] == [reference(a) for a in args]
        assert calls == ref_calls
        assert calls == list(dict.fromkeys(args)), "fn must run once per distinct argument"
        assert wrapped.__name__ == name, "wrapper lost __name__ — functools.wraps"
        assert wrapped.__doc__ == doc, "wrapper lost __doc__ — functools.wraps"
