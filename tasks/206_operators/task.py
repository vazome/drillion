def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import itertools
import math

import pytest
from _lib import rng


def _gen(r):
    n = r.randint(2, 4)
    return (
        tuple(round(r.uniform(-20.0, 20.0), 2) for _ in range(n)),
        tuple(round(r.uniform(-20.0, 20.0), 2) for _ in range(r.randint(1, 5))),
        round(r.uniform(-6.0, 6.0), 2),
    )


def _reference():
    class Move:
        def __init__(self, components):
            self.components = tuple(float(c) for c in components)

        def __iter__(self):
            return iter(self.components)

        def __repr__(self):
            return f"Move({', '.join(repr(c) for c in self.components)})"

        def __abs__(self):
            return math.hypot(*self.components)

        def __eq__(self, other):
            if isinstance(other, Move):
                return self.components == other.components
            return NotImplemented

        def __add__(self, other):
            try:
                pairs = itertools.zip_longest(self.components, other, fillvalue=0.0)
                return Move(a + b for a, b in pairs)
            except TypeError:
                return NotImplemented

        def __radd__(self, other):
            return self + other

        def __mul__(self, scalar):
            if isinstance(scalar, (int, float)):
                return Move(c * scalar for c in self.components)
            return NotImplemented

    return Move


def test_solve():
    r = rng()
    move, want = solve(), _reference()

    for _ in range(8):
        a, b, k = _gen(r)
        assert move(a).components == want(a).components, f"components for {a}"
        assert repr(move(a)) == repr(want(a)), f"repr for {a}"
        assert abs(move(a)) == abs(want(a)), f"abs of {a}"
        assert (move(a) + move(b)).components == (want(a) + want(b)).components, f"{a} + {b}"
        assert (move(a) + list(b)).components == (want(a) + list(b)).components, f"{a} + {b} list"
        assert (move(a) * k).components == (want(a) * k).components, f"{a} * {k}"
        assert move(a) == move(list(a)), f"equal moves for {a}"
        assert move(a) != move(a + (1.0,)), f"different lengths are not equal: {a}"

    # the reflected side only ever runs because the left operand declined instead of raising
    a = (3.0, 4.0)
    assert ((10, 20) + move(a)).components == (13.0, 24.0), "(10, 20) + Move must work"

    # declining is a returned value, not an exception; raising here kills the reflected fallback
    assert move(a).__add__(7) is NotImplemented, "__add__ returns NotImplemented, never raises"
    assert move(a).__add__("nope") is NotImplemented, "an iterable of the wrong kind declines too"
    assert move(a).__mul__("nope") is NotImplemented, "__mul__ returns NotImplemented for non-numbers"
    assert move(a).__eq__((3.0, 4.0)) is NotImplemented, "__eq__ declines foreign types"

    assert (move(a) == (3.0, 4.0)) is False, "a Move never equals a plain tuple"
    with pytest.raises(TypeError):
        move(a) + 7
    with pytest.raises(TypeError):
        move(a) * "nope"
