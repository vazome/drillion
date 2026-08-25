def solve(lines):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    hosts = [f"{p}-{r.randint(1, 4)}" for p in r.sample(["web", "db", "cache", "worker", "proxy"], r.randint(2, 4))]
    msgs = ["disk full", "slow query on users", "restarted", "cert expires soon",
            "conn reset by peer", "high load", "OOM killed worker"]
    levels = ["INFO", "WARN", "ERROR"]
    return [f"{r.choice(hosts)} {r.choice(levels)} {r.choice(msgs)}"
            for _ in range(r.randint(8, 16))]


def _reference(lines):
    from collections import defaultdict
    groups = defaultdict(list)
    for line in lines:
        host, _level, msg = line.split(" ", 2)
        groups[host].append(msg)
    return dict(groups)


def test_solve():
    r = rng()
    for _ in range(4):
        lines = _gen(r)
        assert solve(list(lines)) == _reference(lines)
