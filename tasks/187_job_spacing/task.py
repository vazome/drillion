def solve(jobs: list[str]) -> list[str]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from collections import Counter
from itertools import pairwise

from _lib import rng


def _gen(r):
    services = r.sample(
        ["api", "auth", "billing", "cache", "cron", "db", "mail", "web"], r.randint(2, 5)
    )
    jobs = []
    for service in services:
        jobs += [service] * r.randint(1, 6)
    r.shuffle(jobs)
    return jobs


def _reference(jobs):
    import heapq

    heap = [(-count, service) for service, count in Counter(jobs).items()]
    heapq.heapify(heap)
    out, held = [], None
    while heap:
        count, service = heapq.heappop(heap)
        out.append(service)
        if held:
            heapq.heappush(heap, held)
        held = (count + 1, service) if count + 1 else None
    return out if len(out) == len(jobs) else []


def _check(jobs, order):
    """The order is not unique, so grade the two rules it has to obey."""
    assert Counter(order) == Counter(jobs), f"{order} is not a reordering of {jobs}"
    assert all(a != b for a, b in pairwise(order)), f"{order} repeats a service"


def test_solve():
    r = rng()
    known = [
        ([], []),
        (["api"], ["api"]),
        (["api", "api"], []),
        (["api", "api", "api", "db"], []),
    ]
    for jobs, want in known:
        assert solve(list(jobs)) == want, f"{jobs} is {want}"

    for jobs in [["api", "api", "db"], ["api", "db", "api", "db"]] + [
        _gen(r) for _ in range(30)
    ]:
        mine, reference = solve(list(jobs)), _reference(list(jobs))
        if not reference:
            assert mine == [], f"{jobs} cannot be spaced out, so the answer is []"
        else:
            _check(jobs, mine)
