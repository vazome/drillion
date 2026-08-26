def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng

_EARTH_YEAR = 31557600
_PERIODS = {"mercury": 0.2408467, "venus": 0.61519726, "earth": 1.0, "mars": 1.8808158,
            "jupiter": 11.862615, "saturn": 29.447498, "uranus": 84.016846,
            "neptune": 164.79132}


def _gen(r):
    scale = r.choice([10 ** 7, 10 ** 8, 10 ** 9, 10 ** 10])
    return r.randrange(scale, scale * 9)


def _on(planet):
    def method(self):
        return round(self.seconds / (_EARTH_YEAR * _PERIODS[planet]), 2)
    return method


def _reference():
    class SpaceAge:
        on_mercury = _on("mercury")
        on_venus = _on("venus")
        on_earth = _on("earth")
        on_mars = _on("mars")
        on_jupiter = _on("jupiter")
        on_saturn = _on("saturn")
        on_uranus = _on("uranus")
        on_neptune = _on("neptune")

        def __init__(self, seconds):
            self.seconds = seconds

    return SpaceAge


def test_solve():
    r = rng()
    SpaceAge = solve()
    assert inspect.isclass(SpaceAge), "solve() must return a class"
    Reference = _reference()
    for _ in range(6):
        seconds = _gen(r)
        mine, theirs = SpaceAge(seconds), Reference(seconds)
        assert mine.seconds == seconds, f"seconds {seconds} must be kept unchanged"
        for planet in _PERIODS:
            name = f"on_{planet}"
            assert getattr(mine, name)() == getattr(theirs, name)(), f"{name} {seconds}"

    # canonical cases (exercism/python practice/space-age)
    assert SpaceAge(1000000000).on_earth() == 31.69
    assert SpaceAge(2134835688).on_mercury() == 280.88
    assert SpaceAge(189839836).on_venus() == 9.78
    assert SpaceAge(2129871239).on_mars() == 35.88
    assert SpaceAge(901876382).on_jupiter() == 2.41
    assert SpaceAge(2000000000).on_saturn() == 2.15
    assert SpaceAge(1210123456).on_uranus() == 0.46
    assert SpaceAge(1821023456).on_neptune() == 0.35
