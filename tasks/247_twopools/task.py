from collections import deque


def solve(conflicts):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_JOBS = ["backup", "reindex", "vacuum", "rollup", "purge", "export", "sync", "warmup"]


def _gen(r):
    names = _JOBS[: r.randint(6, 8)]
    r.shuffle(names)
    cut = r.randint(2, len(names) - 2)
    left, right = names[:cut], names[cut:]
    conflicts = {name: set() for name in names}

    def clash(one, other):
        conflicts[one].add(other)
        conflicts[other].add(one)

    for i, name in enumerate(right):
        clash(name, left[r.randrange(len(left))])
        if i:
            clash(name, right[i - 1] if r.random() < 0.5 else left[r.randrange(len(left))])
    for name in left[1:]:
        clash(name, right[r.randrange(len(right))])
    if r.random() < 0.5:
        # both ends already sit on the same side, so this edge closes an odd loop
        side = left if r.random() < 0.5 else right
        clash(side[0], side[r.randrange(1, len(side))])
    return {name: sorted(conflicts[name]) for name in sorted(names)}


def _reference(conflicts):
    pools = {}
    for root in sorted(conflicts):
        if root in pools:
            continue
        pools[root] = 0
        queue = deque([root])
        while queue:
            job = queue.popleft()
            for other in conflicts[job]:
                if other not in pools:
                    pools[other] = 1 - pools[job]
                    queue.append(other)
                elif pools[other] == pools[job]:
                    return None
    return (
        sorted(job for job, pool in pools.items() if pool == 0),
        sorted(job for job, pool in pools.items() if pool == 1),
    )


def test_solve():
    r = rng()
    for _ in range(12):
        conflicts = _gen(r)
        got, want = solve(conflicts), _reference(conflicts)
        assert got == want, f"expected {want}, got {got!r}, for {conflicts}"

    # three jobs that all clash: whichever two share a pool, they clash
    triangle = {
        "backup": ["purge", "sync"],
        "purge": ["backup", "sync"],
        "sync": ["backup", "purge"],
    }
    assert solve(triangle) is None, "a three-way clash cannot be split over two pools"

    split = {
        "backup": ["purge"],
        "purge": ["backup"],
        "sync": ["export"],
        "export": ["sync"],
        "idle": [],
    }
    assert solve(split) == (["backup", "export", "idle"], ["purge", "sync"]), (
        "every job lands in a pool, the smallest name of each group first"
    )
    assert solve({}) == ([], [])
