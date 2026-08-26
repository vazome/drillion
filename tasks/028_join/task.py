def solve(line):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    words = r.sample(["api", "db", "cache", "queue", "auth", "cron", "web"],
                     r.randint(3, 6))
    pad = lambda w: " " * r.randint(0, 2) + w + " " * r.randint(0, 2)
    return ",".join(pad(w) for w in words)


def _reference(line):
    return " | ".join(p.strip() for p in line.split(","))


def test_solve():
    r = rng()
    for _ in range(4):
        line = _gen(r)
        assert solve(line) == _reference(line)
