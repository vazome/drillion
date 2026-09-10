def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng


def _gen(r):
    fields = ["level", "service", "msg", "trace", "user", "region"]
    return " ".join(r.sample(fields, r.randint(3, 6)))


def _reference():
    class Fields:
        def __init__(self, line):
            self.parts = line.split()

        def __iter__(self):
            return FieldIterator(self.parts)

    class FieldIterator:
        def __init__(self, parts):
            self.parts = parts
            self.at = 0

        def __next__(self):
            if self.at >= len(self.parts):
                raise StopIteration
            value = self.parts[self.at]
            self.at += 1
            return value

        def __iter__(self):
            return self

    return Fields, FieldIterator


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert len(got) == 2, "return the two classes as (Fields, FieldIterator)"
    fields, field_iterator = got
    want_fields, _ = want

    for _ in range(6):
        line = _gen(r)
        assert list(fields(line)) == list(want_fields(line)), f"line {line!r}"

    line = "level service msg"
    holder = fields(line)
    assert list(holder) == list(holder), "iterating twice must give the same fields both times"

    walker = iter(holder)
    assert isinstance(walker, field_iterator), "__iter__ must return a FieldIterator"
    assert iter(holder) is not iter(holder), "each pass gets its own iterator"
    assert iter(walker) is walker, "an iterator is its own iterable"

    assert next(walker) == "level" and next(walker) == "service" and next(walker) == "msg"
    for _ in range(2):
        try:
            next(walker)
        except StopIteration:
            pass
        else:
            raise AssertionError("an exhausted iterator must keep raising StopIteration")

    # the protocol written out, not handed to a generator
    assert not inspect.isgeneratorfunction(fields.__iter__), "write __iter__ as a plain return"
    assert "__next__" in vars(field_iterator), "FieldIterator must define __next__ itself"
    assert list(fields("")) == []
