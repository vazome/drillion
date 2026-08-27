def solve(text: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    hosts = [f"{r.choice(['web', 'db', 'cache'])}-{r.randint(1, 9)}" for _ in range(3)]
    msgs = ["disk full on /var", "connection reset by peer", "cert expires in 3 days",
            "OOM killed worker 4", "replica lag high", "retry budget exhausted"]
    noise = ["    at worker.py:88 in flush()",
             "Traceback (most recent call last):",
             "    retrying in 5s..."]
    lines = []
    for _ in range(r.randint(5, 10)):
        ts = (f"2026-08-{r.randint(10, 28):02d}T"
              f"{r.randint(0, 23):02d}:{r.randint(0, 59):02d}:{r.randint(0, 59):02d}")
        lines.append(f'{ts} level={r.choice(["INFO", "WARN", "ERROR"])} '
                     f'host={r.choice(hosts)} msg="{r.choice(msgs)}" '
                     f'trace="{r.randint(0, 16**6 - 1):06x}"')
        if r.random() < 0.4:
            lines.append(r.choice(noise))
    return "\n".join(lines)


def _reference(text):
    import re
    pat = re.compile(r'level=(?P<level>[A-Z]+) host=(?P<host>[\w-]+) msg="(?P<msg>.*?)"')
    return [m.groupdict() for m in pat.finditer(text)]


def test_solve():
    r = rng()
    for _ in range(4):
        text = _gen(r)
        assert solve(text) == _reference(text)
