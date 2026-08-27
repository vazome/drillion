def solve(lines, n: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    n = r.randint(3, 6)
    total = r.randint(10, 30)
    err_rate = r.choice([0.15, 0.3, 0.6])
    msgs = ["disk full", "timeout upstream", "restarted", "cache miss",
            "slow query", "conn reset"]
    lines = []
    for i in range(total):
        level = "ERROR" if r.random() < err_rate else r.choice(["INFO", "WARN"])
        lines.append(f"10:{i:02d} {level} {r.choice(msgs)}")
    return lines, n


def _reference(lines, n):
    from collections import deque
    tail = deque(maxlen=n)
    for line in lines:
        if "ERROR" in line:
            tail.append(line)
    return list(tail)


def test_solve():
    r = rng()
    for _ in range(4):
        lines, n = _gen(r)
        assert solve(iter(lines), n) == _reference(iter(lines), n)
