def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import math

from _lib import rng


def _gen(r):
    return (
        round(r.uniform(-50.0, 50.0), 2),
        round(r.uniform(-50.0, 50.0), 2),
        r.choice(["", ".2f", ".3e", "8.4f", ".1f", ".5e"]),
    )


def _reference():
    class Point:
        def __init__(self, x, y):
            self.x = float(x)
            self.y = float(y)

        def __repr__(self):
            return f"Point({self.x!r}, {self.y!r})"

        def __str__(self):
            return str((self.x, self.y))

        def __format__(self, spec=""):
            if spec.endswith("p"):
                spec = spec[:-1]
                coords = (math.hypot(self.x, self.y), math.atan2(self.y, self.x))
                outer = "<{}, {}>"
            else:
                coords = (self.x, self.y)
                outer = "({}, {})"
            return outer.format(*(format(c, spec) for c in coords))

    return Point


def test_solve():
    r = rng()
    point, want = solve(), _reference()

    for _ in range(8):
        x, y, spec = _gen(r)
        mine, theirs = point(x, y), want(x, y)
        assert repr(mine) == repr(theirs), f"repr for {(x, y)}"
        assert str(mine) == str(theirs), f"str for {(x, y)}"
        assert format(mine, spec) == format(theirs, spec), f"format {spec!r} for {(x, y)}"
        assert format(mine, spec + "p") == format(theirs, spec + "p"), f"polar {spec!r}"
        assert f"{mine:{spec}}" == f"{theirs:{spec}}", f"f-string {spec!r} for {(x, y)}"

    p = point(3, 4)

    # the spec applies to each number; rendering first and formatting the whole string does not
    assert format(p, ".2f") == "(3.00, 4.00)", "format the components, not the finished line"
    assert format(p, ".3e") == "(3.000e+00, 4.000e+00)", ".3e goes to each component"
    assert format(point(1, 1), ".3ep") == "<1.414e+00, 7.854e-01>", "polar with a spec"

    # falling back to __repr__ prints the debugging form where the readable one was asked for
    assert str(p) == "(3.0, 4.0)", "__str__ is the plain pair"
    assert repr(p) == "Point(3.0, 4.0)", "__repr__ names the class"
    assert str(p) != repr(p), "the two renderings are not the same string"
    assert format(p) == str(p), "an empty spec is the readable form"
