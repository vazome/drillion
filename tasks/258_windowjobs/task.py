def solve(jobs: list[tuple[int, int, int]]) -> int:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    jobs = []
    for _ in range(r.randint(10, 14)):
        start = r.randrange(0, 20)
        length = r.randint(1, 6)
        jobs.append((start, start + length, r.randint(1, 20)))
    return jobs


def _reference(jobs):
    from bisect import bisect_right

    ordered = sorted(jobs, key=lambda job: job[1])
    ends = [end for _start, end, _value in ordered]
    best = [0]
    for start, _end, value in ordered:
        # how many of the ordered jobs finish at or before this one starts
        room = bisect_right(ends, start)
        best.append(max(best[-1], best[room] + value))
    return best[-1]


def test_solve():
    r = rng()
    known = [
        ([], 0),
        ([(0, 4, 9)], 9),
        # touching is not overlapping: one ends at 5, the next starts at 5
        ([(0, 5, 10), (5, 9, 7)], 17),
        ([(0, 5, 10), (4, 9, 7)], 10),
        # the fattest job blocks the whole window; three lean ones beat it
        ([(0, 10, 10), (0, 3, 6), (3, 6, 6), (6, 10, 6)], 18),
        # finishing earliest is not the same as being worth taking
        ([(0, 3, 1), (1, 10, 50)], 50),
    ]
    for jobs, want in known:
        assert solve(list(jobs)) == want, f"{jobs} is worth {want}"

    for _ in range(6):
        jobs = _gen(r)
        assert solve(list(jobs)) == _reference(jobs), f"jobs={jobs}"
