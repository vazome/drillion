def solve(workloads: list[dict[str, int | str]]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    workloads = []
    for _ in range(r.randint(4, 9)):
        kind = r.choice(["io", "io", "cpu"])
        count = r.choice([1, 2, 8, r.randint(3, 98), 99, 100, 101,
                          r.randint(100, 20000), r.randint(1, 5000)])
        workloads.append({"kind": kind, "count": count})
    # the boundary always shows up, so an off-by-one cannot slip through a seed
    for edge in ({"kind": "io", "count": 100}, {"kind": "io", "count": 99},
                 {"kind": "cpu", "count": r.randint(200, 900)}):
        workloads.insert(r.randint(0, len(workloads)), edge)
    return workloads


def _reference(workloads):
    labels = []
    for w in workloads:
        if w["kind"] == "cpu":
            labels.append("processes")
        elif w["count"] >= 100:
            labels.append("async")
        else:
            labels.append("threads")
    return labels


def test_solve():
    r = rng()
    for _ in range(4):
        workloads = _gen(r)
        assert solve(workloads) == _reference(workloads)
