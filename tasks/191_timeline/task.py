def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng


def _reference():
    from bisect import bisect_left, insort

    class Event:
        def __init__(self, when, name):
            self.when = when
            self.name = name

        def __lt__(self, other):
            return (self.when, self.name) < (other.when, other.name)

    class Timeline:
        event_type = Event

        def __init__(self):
            self.events = []

        def add(self, when, name):
            insort(self.events, Event(when, name))

        def from_time(self, when):
            start = bisect_left(self.events, Event(when, ""))
            return self.events[start:]

    return Timeline


def _view(events):
    return [(event.when, event.name) for event in events]


def test_solve():
    Timeline = solve()
    assert inspect.isclass(Timeline), "solve() must return a class"
    canonical = Timeline()
    assert Timeline.event_type(10, "a") < Timeline.event_type(20, "a")
    assert Timeline.event_type(10, "a") < Timeline.event_type(10, "b")
    for event in [(30, "deploy"), (10, "backup"), (30, "audit")]:
        canonical.add(*event)
    assert _view(canonical.events) == [(10, "backup"), (30, "audit"), (30, "deploy")]
    assert _view(canonical.from_time(30)) == [(30, "audit"), (30, "deploy")]
    assert canonical.events and all(type(event) is Timeline.event_type for event in canonical.events)

    r = rng()
    Reference = _reference()
    for _ in range(5):
        events = [(r.randint(0, 50), name) for name in r.sample(
            ["backup", "deploy", "audit", "rotate", "snapshot", "restart"], r.randint(3, 6))]
        mine, theirs = Timeline(), Reference()
        for event in events:
            mine.add(*event)
            theirs.add(*event)
        assert _view(mine.events) == _view(theirs.events)
        point = r.randint(0, 50)
        assert _view(mine.from_time(point)) == _view(theirs.from_time(point))
