def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

import pytest
from _lib import rng


def _gen(r):
    return [f"T-{r.randrange(100, 999)}" for _ in range(r.randint(2, 8))]


def _reference():
    class Dispenser:
        def __init__(self, items):
            self._items = list(items)

        def pick(self):
            try:
                return self._items.pop(0)
            except IndexError:
                raise LookupError("dispenser is empty") from None

        __call__ = pick

        def __len__(self):
            return len(self._items)

        def __repr__(self):
            return f"Dispenser({len(self)} left)"

    return Dispenser


def test_solve():
    got = solve()

    # a factory that hands back a closure calls fine and can never be asked anything
    assert inspect.isclass(got), "solve() returns the class Dispenser, not a function"

    r = rng()
    want = _reference()
    for _ in range(6):
        tickets = _gen(r)
        original = list(tickets)
        mine, theirs = got(tickets), want(tickets)
        assert tickets == original, "the caller's list must not be emptied"
        assert len(mine) == len(theirs) == len(original), f"len for {original}"
        assert repr(mine) == repr(theirs), f"repr for {original}"
        assert callable(mine), "an instance must be callable"
        out = [mine() if i % 2 else mine.pick() for i in range(len(original))]
        assert out == original, f"first in, first out for {original}"
        assert len(mine) == 0, "nothing left after taking them all"

    desk = got(["T-01", "T-02"])
    assert desk() == "T-01" and len(desk) == 1, "calling takes one and the count follows"
    assert desk.pick() == "T-02", "pick and the call do the same thing"

    for take in (desk, desk.pick):
        with pytest.raises(LookupError) as caught:
            take()
        assert "dispenser is empty" in str(caught.value), "say what ran out"
