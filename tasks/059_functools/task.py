from collections.abc import Callable


def solve(fn: Callable[[int], int]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


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
