def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    return (
        r.choice(["furnace-2", "chiller-a", "roof-intake", "pump-7", "duct-3"]),
        round(r.uniform(-15.0, 95.0), 1),
        r.choice(["C", "K", "F"]),
    )


def _reference():
    class Reading:
        __slots__ = ("celsius", "sensor")

        def __init__(self, sensor, celsius):
            self.sensor = sensor
            self.celsius = celsius

        def __repr__(self):
            return f"Reading({self.sensor!r}, {self.celsius!r})"

    class Tagged(Reading):
        __slots__ = ("unit",)

        def __init__(self, sensor, celsius, unit):
            super().__init__(sensor, celsius)
            self.unit = unit

    return Reading, Tagged


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert len(got) == 2, "return the two classes as (Reading, Tagged)"
    reading, tagged = got
    want_reading, want_tagged = want

    for _ in range(6):
        sensor, celsius, unit = _gen(r)
        mine, theirs = reading(sensor, celsius), want_reading(sensor, celsius)
        assert (mine.sensor, mine.celsius) == (theirs.sensor, theirs.celsius), f"reading {sensor!r}"
        assert repr(mine) == repr(theirs), f"repr for {(sensor, celsius)}"
        mine_tagged = tagged(sensor, celsius, unit)
        assert (mine_tagged.sensor, mine_tagged.celsius) == (sensor, celsius)
        assert mine_tagged.unit == want_tagged(sensor, celsius, unit).unit

    assert issubclass(tagged, reading), "Tagged must subclass Reading"

    # a class that merely never sets a third attribute still has the dict that lets one through
    item = reading("furnace-2", 21.5)
    assert not hasattr(item, "__dict__"), "Reading instances must have no __dict__"
    with pytest.raises(AttributeError):
        item.celcius = 22.0

    # the saving and the refusal are both lost the moment a subclass forgets its own __slots__
    sub = tagged("furnace-2", 21.5, "C")
    assert not hasattr(sub, "__dict__"), "Tagged must declare __slots__ too"
    with pytest.raises(AttributeError):
        sub.unti = "C"

    assert set(vars(reading)["__slots__"]) == {"celsius", "sensor"}, "declare both names"
    declared = vars(tagged)["__slots__"]
    declared = (declared,) if isinstance(declared, str) else tuple(declared)
    assert declared == ("unit",), "Tagged declares only the name it adds"
