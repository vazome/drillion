def solve(port, name):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    ports = [None, 0, r.randint(1024, 65535)]
    names = [None, "", r.choice(["api", "db", "cache", "cron", "sync"])]
    cases = [(p, n) for p in ports for n in names]
    r.shuffle(cases)
    return cases


def _reference(port, name):
    port = port if port is not None else 8080
    name = name if name is not None else "worker"
    return (port, name)


def test_solve():
    r = rng()
    for _ in range(4):
        for port, name in _gen(r):
            assert solve(port, name) == _reference(port, name)
