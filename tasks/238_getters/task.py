from dataclasses import dataclass
from operator import attrgetter, itemgetter, methodcaller


@dataclass(frozen=True)
class Run:
    service: str
    region: str
    seconds: float


def solve(runs, rows):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_SERVICES = ["svc-api", "svc-db", "svc-cdn", "svc-auth", "svc-queue", "svc-svc-api"]
_REGIONS = ["eu", "us", "ap"]


def _gen(r):
    def row():
        # two regions only, so regions repeat and the second sort field matters
        return (r.choice(_SERVICES), r.choice(_REGIONS[:2]), float(r.randrange(1, 9)))

    runs = [Run(*row()) for _ in range(r.randint(4, 8))]
    return runs, [row() for _ in range(r.randint(3, 7))]


def _reference(runs, rows):
    return {
        "by_region": list(map(attrgetter("service"), sorted(runs, key=attrgetter("region", "service")))),
        "slowest": max(runs, key=attrgetter("seconds")).service,
        "short_names": list(map(methodcaller("removeprefix", "svc-"), map(attrgetter("service"), runs))),
        "rows_sorted": sorted(rows, key=itemgetter(1, 2)),
    }


def test_solve():
    r = rng()
    for _ in range(20):
        runs, rows = _gen(r)
        before = list(rows)
        got, want = solve(runs, rows), _reference(runs, rows)
        assert got == want, f"for runs={runs} rows={rows}: got {got}"
        assert set(got) == {"by_region", "slowest", "short_names", "rows_sorted"}, sorted(got)
        assert rows == before, "leave the caller's rows in the order they arrived"

    # a single-field key leaves the ties in input order; these two share a region and a duration
    tied = [Run("svc-db", "eu", 5.0), Run("svc-api", "eu", 5.0), Run("svc-cdn", "ap", 1.0)]
    rows = [("svc-db", "eu", 5.0), ("svc-api", "eu", 2.0), ("svc-cdn", "ap", 9.0)]
    canonical = solve(tied, rows)
    assert canonical["by_region"] == ["svc-cdn", "svc-api", "svc-db"], canonical["by_region"]
    assert canonical["rows_sorted"] == [
        ("svc-cdn", "ap", 9.0),
        ("svc-api", "eu", 2.0),
        ("svc-db", "eu", 5.0),
    ], canonical["rows_sorted"]
    assert canonical["slowest"] == "svc-db", "a tie on seconds goes to the first such run"
    assert canonical["short_names"] == ["db", "api", "cdn"], canonical["short_names"]

    doubled = solve([Run("svc-svc-api", "eu", 1.0)], [])
    assert doubled["short_names"] == ["svc-api"], "strip the prefix once, not every time it appears"
