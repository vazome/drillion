def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import operator

import pytest
from _lib import rng


def _gen(r):
    n = r.randint(4, 12)
    return (
        tuple(round(r.uniform(-40.0, 90.0), 2) for _ in range(n)),
        slice(r.randint(-n, n), r.randint(-n, n), r.choice([None, 1, 2, -1])),
        r.randrange(-n, n),
    )


def _reference():
    class Series:
        def __init__(self, values):
            self.values = tuple(float(v) for v in values)

        def __repr__(self):
            return f"Series({', '.join(repr(v) for v in self.values)})"

        def __len__(self):
            return len(self.values)

        def __getitem__(self, key):
            if isinstance(key, slice):
                return type(self)(self.values[key])
            return self.values[operator.index(key)]

    return Series


def test_solve():
    r = rng()
    series, want = solve(), _reference()

    for _ in range(8):
        values, window, i = _gen(r)
        mine, theirs = series(values), want(values)
        assert len(mine) == len(theirs), f"len for {values}"
        assert repr(mine) == repr(theirs), f"repr for {values}"
        assert mine[i] == theirs[i], f"index {i} of {values}"
        cut = mine[window]
        assert type(cut) is series, f"slice {window} gave {type(cut).__name__}, not a Series"
        assert cut.values == theirs[window].values, f"slice {window} of {values}"
        assert list(mine) == list(theirs), f"iteration over {values}"
        assert (values[0] in mine) == (values[0] in theirs), f"membership in {values}"

    s = series([10, 20, 30, 40, 50])

    # a slice that comes back as a plain list has lost every method the class had
    assert type(s[1:4]) is series, "slicing a Series gives a Series"
    assert s[1:4].values == (20.0, 30.0, 40.0), "slice values"
    assert s[:].values == s.values, "a full slice is a copy of the same class"

    # naming the class outright instead of type(self) breaks the moment someone subclasses it
    class Smoothed(series):
        pass

    assert type(Smoothed([1, 2, 3, 4])[1:3]) is Smoothed, "slice with type(self), not the name"

    assert s[0] == 10.0 and s[-1] == 50.0, "negative indices count from the end"
    assert list(reversed(s)) == [50.0, 40.0, 30.0, 20.0, 10.0], "reversed() comes free"
    with pytest.raises(IndexError):
        s[99]
    with pytest.raises(TypeError):
        s["first"]
