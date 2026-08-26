def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng


def _gen(r):
    hour = r.choice([r.randint(0, 23), r.randint(-120, 120), r.randint(24, 300)])
    minute = r.choice([r.randint(0, 59), r.randint(-6000, 6000), r.randrange(-180, 181, 60)])
    return hour, minute


def _reference():
    class Clock:
        def __init__(self, hour, minute):
            self.hour, self.minute = divmod(hour * 60 + minute, 60)
            self.hour %= 24

        def __repr__(self):
            return f"Clock({self.hour}, {self.minute})"

        def __str__(self):
            return f"{self.hour:02d}:{self.minute:02d}"

        def __eq__(self, other):
            return (self.hour, self.minute) == (other.hour, other.minute)

        def __add__(self, minutes):
            return Clock(self.hour, self.minute + minutes)

        def __sub__(self, minutes):
            return Clock(self.hour, self.minute - minutes)

    return Clock


def test_solve():
    r = rng()
    Clock = solve()
    assert inspect.isclass(Clock), "solve() must return a class"
    Reference = _reference()
    for _ in range(6):
        hour, minute = _gen(r)
        mine, theirs = Clock(hour, minute), Reference(hour, minute)
        assert str(mine) == str(theirs), f"str of Clock({hour}, {minute})"
        assert repr(mine) == repr(theirs), f"repr of Clock({hour}, {minute})"
        shift = r.randint(-3000, 3000)
        assert str(mine + shift) == str(theirs + shift), f"Clock({hour}, {minute}) + {shift}"
        assert str(mine) == str(theirs), f"+ must not change Clock({hour}, {minute}) itself"
        assert str(mine - shift) == str(theirs - shift), f"Clock({hour}, {minute}) - {shift}"
        assert str(mine) == str(theirs), f"- must not change Clock({hour}, {minute}) itself"
        assert mine == Clock(hour + 24, minute), f"Clock({hour}, {minute}) == the same time a day later"
        assert mine != Clock(hour, minute + 1), f"Clock({hour}, {minute}) != one minute later"

    # canonical cases (exercism/python practice/clock)
    assert repr(Clock(6, 45)) == "Clock(6, 45)"
    assert str(Clock(0, 1723)) == "04:43"
    assert str(Clock(-25, -160)) == "20:20"
    assert str(Clock(0, 45) + 160) == "03:25"
    assert str(Clock(6, 15) - 160) == "03:35"
    assert Clock(10, 37) == Clock(34, 37)
