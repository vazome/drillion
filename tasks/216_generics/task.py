def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from typing import Generic, TypeVar

import pytest
from _lib import rng


def _gen(r):
    pool = ["parcel", "refund", "alert", "invoice", "ticket", "recall"]
    return [f"{r.choice(pool)}-{r.randint(100, 999)}" for _ in range(r.randint(0, 6))]


def _reference():
    from collections.abc import Iterable

    T = TypeVar("T")

    class Drawer(Generic[T]):
        def __init__(self, items: Iterable[T]) -> None:
            self._items = list(items)

        def load(self, items: Iterable[T]) -> None:
            self._items.extend(items)

        def take(self) -> T:
            if not self._items:
                raise LookupError("take from an empty Drawer")
            return self._items.pop(0)

        def remaining(self) -> tuple[T, ...]:
            return tuple(self._items)

    return Drawer


def test_solve():
    r = rng()
    drawer, want_drawer = solve(), _reference()

    for _ in range(6):
        start, more = _gen(r), _gen(r)
        mine, theirs = drawer(start), want_drawer(start)
        mine.load(more)
        theirs.load(more)
        assert mine.remaining() == theirs.remaining(), f"after loading {start} then {more}"
        while theirs.remaining():
            assert mine.take() == theirs.take(), f"take order for {start} then {more}"
        assert mine.remaining() == (), f"emptied drawer for {start} then {more}"

    queue = drawer(["ada", "grace"])
    queue.load(["alan"])
    assert queue.take() == "ada", "take hands back the item that waited longest"
    assert queue.remaining() == ("grace", "alan"), "remaining is a tuple, front first"
    assert queue.load(["edsger"]) is None, "load returns nothing"

    given = ["ada"]
    kept = drawer(given)
    given.append("grace")
    assert kept.remaining() == ("ada",), "the drawer keeps its own list, not the caller's"

    with pytest.raises(LookupError):
        drawer([]).take()

    # an ordinary class passes everything above; this is the line it cannot survive
    params = getattr(drawer, "__parameters__", ())
    assert len(params) == 1, "Drawer must inherit from Generic[T], with exactly one TypeVar"
    typed = drawer[str](["ada"])
    assert typed.take() == "ada", "Drawer[str] must build a working drawer"
