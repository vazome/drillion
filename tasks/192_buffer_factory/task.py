def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng


def _reference():
    def make_buffer(limit=None, initial=None):
        items = [] if initial is None else list(initial)

        def push(item):
            items.append(item)
            if limit == 0:
                items.clear()
            elif limit is not None:
                del items[:-limit]
            return list(items)

        return push

    return make_buffer


def test_solve():
    make_buffer = solve()
    assert callable(make_buffer)
    assert list(inspect.signature(make_buffer).parameters) == ["limit", "initial"]
    assert [p.default for p in inspect.signature(make_buffer).parameters.values()] == [None, None]

    left, right = make_buffer(2), make_buffer(2)
    assert inspect.isfunction(left) and left.__closure__, "each buffer must be a closure"
    assert left("a") == ["a"]
    assert left("b") == ["a", "b"]
    assert left("c") == ["b", "c"]
    assert right("z") == ["z"], "separate buffers must not share a default list"
    initial = ["old"]
    seeded = make_buffer(2, initial)
    assert seeded("new") == ["old", "new"]
    assert initial == ["old"], "a buffer must copy the caller's initial list"
    empty = make_buffer(0, ["old"])
    assert empty("new") == [], "limit=0 is different from no limit"

    r = rng()
    reference = _reference()
    for _ in range(5):
        limit = r.choice([None, 0, 1, 3])
        initial = r.choice([None, [], r.sample(list("abcdef"), r.randint(1, 3))])
        mine, theirs = make_buffer(limit, initial), reference(limit, initial)
        for item in r.sample(list("uvwxyz"), r.randint(2, 5)):
            assert mine(item) == theirs(item)
