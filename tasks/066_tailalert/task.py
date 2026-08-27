from collections.abc import Iterator


def solve(stream: Iterator[str], pattern: str, window: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    style = r.choice(["plain", "logfmt"])
    codes = ["E500", "E503", "E404", "E429"]
    msgs = ["upstream timeout", "disk full", "conn reset", "slow query",
            "cache miss"]
    rate = r.choice([0.15, 0.3, 0.5])
    lines = []
    for i in range(r.randint(12, 30)):
        msg = r.choice(msgs)
        if r.random() < rate:
            code = r.choice(codes)
            lines.append(f"10:{i:02d} ERROR {code} {msg}\n" if style == "plain"
                         else f't=10:{i:02d} level=error code={code} msg="{msg}"\n')
        else:
            level = r.choice(["INFO", "WARN"])
            lines.append(f"10:{i:02d} {level} {msg}\n" if style == "plain"
                         else f't=10:{i:02d} level={level.lower()} msg="{msg}"\n')
    pattern = (r"ERROR (?P<code>E\d+)" if style == "plain"
               else r"level=error code=(?P<code>E\d+)")
    return lines, pattern, r.randint(2, 4)


def _reference(stream, pattern, window):
    import re
    from collections import deque
    rx = re.compile(pattern)
    history = deque(maxlen=window)
    alerts = []
    for line_no, raw in enumerate(stream, start=1):
        line = raw.rstrip("\n")
        m = rx.search(line)
        if m:
            alerts.append({"line_no": line_no, "code": m.group("code"),
                           "before": list(history)})
        history.append(line)
    return alerts


def test_solve():
    r = rng()
    for _ in range(4):
        lines, pattern, window = _gen(r)
        assert (solve(iter(lines), pattern, window)
                == _reference(iter(lines), pattern, window))
