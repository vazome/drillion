"""A decorator wraps a function in another function — the whole trick is that."""

from _lib import rng

META = {"topic": 12, "title": "decorators — record every call, pass everything through", "tier": 3,
        "minutes": 12, "prereqs": [8]}


def solve(calls):
    """WHY: An audit team asks: "every time one of our infrastructure tools
    changes something, we need a record of what was called, with what
    arguments, and what it returned." The tools are dozens of existing
    functions and nobody wants to edit each one. You need a single reusable
    wrapper that can be stuck on any function and quietly logs each call
    while leaving the function's behaviour exactly as it was.

    YOU GET: `calls` — an empty list like []. Your wrapper appends one record
    to it per call. The test creates it and hands it to you; you never build
    it yourself.

    YOU RETURN: a decorator: a thing that takes a function and gives back a
    replacement function that behaves the same but also appends
    (name, args, kwargs, result) to `calls` after each call.

    ─── exact rules ───
    Return a decorator that records every call into the list `calls`.

    solve(calls) gives you back a decorator. That decorator takes a function
    and returns a replacement for it. The replacement must:

      - accept any arguments at all and hand them to the original unchanged
      - return exactly what the original returned
      - append one entry to calls, in this shape:
            (fn.__name__, args, kwargs, result)
        args is the positional tuple, kwargs the keyword dict, result the
        value the original returned.

        calls = []
        record = solve(calls)

        @record
        def scale(host, replicas=1):
            return f"{host}:{replicas}"

        scale("api", replicas=3)   # -> "api:3", unchanged
        calls                      # [("scale", ("api",), {"replicas": 3}, "api:3")]

    The entry goes in after the call, not before — you need the result. Record
    args and kwargs as you received them; do not merge, sort or normalise them.
    """
    raise NotImplementedError


HINTS = [
    ("Three nested layers, and the confusion is always about which layer runs "
    "when. The outer call captures the list. The middle one runs once, at "
    "decoration time, and is handed the function. The inner one runs on every "
    "single call and is the thing callers actually reach. Sketch the three defs "
    "and what each one returns before filling in any bodies."),
    ("def solve(calls): def record(fn): def wrapper(*args, **kwargs): ... ; "
    "return wrapper ; return record. Inside wrapper: call fn(*args, **kwargs) "
    "and keep the value in a variable, append the tuple to calls, then return "
    "the variable. *args and **kwargs collect anything on the way in and "
    "re-spread it on the way out. fn.__name__ is the original's name, and "
    "wrapper can still see fn and calls because of closures."),
    ("Different data — a decorator that doubles whatever comes back:\n"
    "    def doubler(fn):\n"
    "        def wrapper(*args, **kwargs):\n"
    "            return fn(*args, **kwargs) * 2\n"
    "        return wrapper\n"
    "\n"
    "    @doubler\n"
    "    def add(a, b=0):\n"
    "        return a + b\n"
    "\n"
    "    print(add(3, b=4))     # 14 — @doubler means add = doubler(add)\n"
    "That one has two layers because it takes no configuration. Yours has "
    "three, because solve takes the list first and only then meets the "
    "function."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _make(name, k, base):
    """A plain function with a known name, so the log has something to record."""
    def fn(host, replicas=1, dry_run=False):
        return f"{host}:dry" if dry_run else f"{host}:{base + k * replicas}"

    fn.__name__ = name
    return fn


def _gen(r):
    """A few functions, each with the calls to replay against it."""
    plans = []
    for name in r.sample(["scale", "drain", "cordon", "restart", "resize", "tag"],
                         r.randint(2, 4)):
        fn = _make(name, r.randint(2, 9), r.randint(1, 20))
        calls = []
        for _ in range(r.randint(2, 4)):
            host = r.choice(["api", "db", "cache", "edge"]) + str(r.randint(1, 9))
            args = (host,) if r.random() < 0.5 else (host, r.randint(1, 4))
            kwargs = {}
            if len(args) == 1 and r.random() < 0.6:
                kwargs["replicas"] = r.randint(1, 4)
            if r.random() < 0.4:
                kwargs["dry_run"] = r.choice([True, False])
            calls.append((args, kwargs))
        plans.append((fn, calls))
    return plans


def _reference(calls):
    def record(fn):
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            calls.append((fn.__name__, args, kwargs, result))
            return result
        return wrapper
    return record


def test_solve():
    r = rng()
    for _ in range(4):
        plans = _gen(r)
        got_log, exp_log = [], []
        record, ref_record = solve(got_log), _reference(exp_log)

        for fn, planned in plans:
            wrapped, ref_wrapped = record(fn), ref_record(fn)
            for args, kwargs in planned:
                expected = fn(*args, **kwargs)
                assert wrapped(*args, **kwargs) == expected, "wrapper must return fn's result"
                assert ref_wrapped(*args, **kwargs) == expected

        assert got_log == exp_log
