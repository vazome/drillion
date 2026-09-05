def solve(hosts: dict[str, list[str]]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    pool = ["prod", "staging", "eu", "us", "db", "web", "canary"]
    hosts = {}
    for i in range(r.randint(3, 10)):
        tags = r.sample(pool, r.randint(0, 3))
        tags += r.sample(tags, r.randint(0, len(tags)))  # duplicates on purpose
        r.shuffle(tags)
        hosts[f"host-{i}"] = tags
    return hosts


def _reference(hosts):
    from collections import Counter
    return dict(Counter(frozenset(tags) for tags in hosts.values()))


def test_solve():
    r = rng()
    cases = [{"web-1": ["prod", "eu"], "web-2": ["eu", "prod"], "db-1": ["prod", "db", "prod"]},
             {}, {"bare": []}]
    for _ in range(6):
        cases.append(_gen(r))
    for hosts in cases:
        got = solve(hosts)
        assert got == _reference(hosts), f"hosts={hosts}"
        assert all(isinstance(k, frozenset) for k in got), "the keys must be frozensets"
