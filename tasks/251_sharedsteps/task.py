def solve(old: list[str], new: list[str]) -> list[str]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_POOL = [
    "checkout",
    "restore-cache",
    "lint",
    "build",
    "unit-test",
    "integration-test",
    "package",
    "sign",
    "stage",
    "smoke-test",
    "migrate",
    "deploy",
    "warm-cache",
    "notify",
]


def _gen(r):
    old = r.sample(_POOL, r.randint(8, 12))
    new = [step for step in old if r.random() < 0.7]
    for _ in range(r.randint(1, 3)):
        new.insert(r.randrange(len(new) + 1), r.choice(_POOL))
    return old, new


def _reference(old, new):
    from functools import cache

    @cache
    def best(i, j):
        if i == len(old) or j == len(new):
            return ()
        if old[i] == new[j]:
            return (old[i], *best(i + 1, j + 1))
        skip_old, skip_new = best(i + 1, j), best(i, j + 1)
        # `>=` is the disclosed tie rule: an equally long answer means skip from `old`
        return skip_old if len(skip_old) >= len(skip_new) else skip_new

    return list(best(0, 0))


def test_solve():
    r = rng()
    known = [
        ([], [], []),
        (["build"], [], []),
        (["a", "b", "c"], ["x", "y"], []),
        (
            ["checkout", "build", "test", "deploy"],
            ["checkout", "lint", "build", "deploy"],
            ["checkout", "build", "deploy"],
        ),
        # order is the question: every name is shared, only one of them survives in order
        (["a", "b", "c"], ["c", "b", "a"], ["c"]),
        (["a", "b", "c", "d"], ["d", "c", "b", "a"], ["d"]),
    ]
    for old, new, want in known:
        assert solve(list(old), list(new)) == want, f"{old} against {new} shares {want}"

    for _ in range(6):
        old, new = _gen(r)
        assert solve(list(old), list(new)) == _reference(old, new), f"old={old} new={new}"
