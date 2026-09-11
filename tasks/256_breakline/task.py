def solve(run: str, parts: list[str]) -> list[str]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_POOL = [
    "log",
    "logs",
    "serve",
    "server",
    "web",
    "webhook",
    "hook",
    "api",
    "apis",
    "cache",
    "cach",
    "queue",
    "node",
    "nodes",
    "key",
    "keys",
    "db",
]


def _gen(r):
    parts = r.sample(_POOL, r.randint(9, 13))
    run = "".join(r.choice(parts) for _ in range(r.randint(3, 6)))
    if r.random() < 0.25:
        run += "zz"  # nothing in the pool ends in z, so this one cannot be cut
    return run, parts


def _reference(run, parts):
    from functools import cache

    known = frozenset(parts)
    longest = max((len(part) for part in known), default=0)

    @cache
    def cut(i):
        if i == len(run):
            return ()
        for size in range(min(longest, len(run) - i), 0, -1):
            head = run[i : i + size]
            if head in known and (rest := cut(i + size)) is not None:
                return (head, *rest)
        return None

    found = cut(0)
    return [] if found is None else list(found)


def test_solve():
    r = rng()
    known = [
        ("deploy", [], []),
        ("deploy", ["stage"], []),
        ("applepenapple", ["apple", "pen"], ["apple", "pen", "apple"]),
        ("catsandog", ["cats", "dog", "sand", "and", "cat"], []),
        # the longest first part is 'logs', and it leaves 'erver' behind
        ("logserver", ["log", "logs", "server"], ["log", "server"]),
        # 'car' is longer than 'ca', and only 'ca' leaves something that cuts
        ("cars", ["car", "ca", "rs"], ["ca", "rs"]),
        ("apiapi", ["api", "apiapi"], ["apiapi"]),
    ]
    for run, parts, want in known:
        assert solve(run, list(parts)) == want, f"{run!r} over {parts} cuts into {want}"

    for _ in range(8):
        run, parts = _gen(r)
        got = solve(run, list(parts))
        assert got == _reference(run, parts), f"run={run!r} parts={parts}"
        assert "".join(got) in (run, ""), f"the parts have to join back to {run!r}"
