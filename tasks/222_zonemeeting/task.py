from datetime import datetime
from zoneinfo import ZoneInfo


def solve(stamps: list[str], from_zone: str, to_zone: str) -> list[str]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

# pairs whose clocks move on different dates, so the gap between them is not a constant
_PAIRS = [("Europe/Berlin", "America/New_York"), ("America/New_York", "Europe/London"),
          ("Europe/London", "Australia/Sydney"), ("America/Chicago", "Europe/Berlin")]


def _gen(r):
    from_zone, to_zone = r.choice(_PAIRS)
    # spread across the northern spring and autumn changeovers, both hemispheres
    days = ["2026-02-20", "2026-03-09", "2026-03-20", "2026-04-10", "2026-10-20",
            "2026-11-05", "2026-12-01"]
    stamps = [f"{day} {r.randrange(8, 18):02d}:{r.choice(['00', '15', '30', '45'])}"
              for day in r.sample(days, 5)]
    return stamps, from_zone, to_zone


def _reference(stamps, from_zone, to_zone):
    source, target = ZoneInfo(from_zone), ZoneInfo(to_zone)
    return [datetime.fromisoformat(s).replace(tzinfo=source).astimezone(target).isoformat()
            for s in stamps]


def test_solve():
    assert solve(["2026-03-07 09:00", "2026-03-15 09:00"], "Europe/Berlin", "America/New_York") == [
        "2026-03-07T03:00:00-05:00",
        "2026-03-15T04:00:00-04:00",
    ], "six hours back before the US clock change, five hours back after it"

    r = rng()
    for _ in range(8):
        stamps, from_zone, to_zone = _gen(r)
        mine = solve(list(stamps), from_zone, to_zone)
        theirs = _reference(stamps, from_zone, to_zone)
        assert len(mine) == len(theirs), f"one string back per stamp, got {len(mine)}"
        # per stamp rather than list-to-list: one offset worked out once and reused agrees
        # on the dates either side of a clock change and is an hour out in between
        for stamp, got, want in zip(stamps, mine, theirs):
            assert got == want, f"{stamp} in {from_zone} is {want} in {to_zone}, got {got}"
