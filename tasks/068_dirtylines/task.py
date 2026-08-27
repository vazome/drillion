LEVELS = {"DEBUG", "INFO", "WARN", "ERROR"}


def solve(lines: list[str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    services = ["checkout", "cart", "auth", "search", "billing", "cdn"]
    lines = []
    for _ in range(r.randint(8, 20)):
        ts = f"2026-08-{r.randint(1, 28):02d}T{r.randint(0, 23):02d}:{r.randint(0, 59):02d}:{r.randint(0, 59):02d}Z"
        level = r.choice(sorted(LEVELS))
        svc = r.choice(services)
        ms = r.randint(1, 4000)
        if r.random() < 0.65:
            lines.append(f"{ts} {level} {svc} {ms}")
            continue
        # corrupt it, one of several distinct ways
        kind = r.choice(["truncated", "blank", "bad-level", "bad-ms", "extra", "padded"])
        if kind == "truncated":
            lines.append(r.choice([f"{ts} {level} {svc}", f"{ts} {level}", ts]))
        elif kind == "blank":
            lines.append(r.choice(["", "   ", "\t"]))
        elif kind == "bad-level":
            lines.append(f"{ts} {r.choice(['info', 'TRACE', 'ERR', 'notice'])} {svc} {ms}")
        elif kind == "bad-ms":
            lines.append(f"{ts} {level} {svc} {r.choice(['N/A', '-', f'{ms}ms', '1.5'])}")
        elif kind == "extra":
            lines.append(f"{ts} {level} {svc} {ms} trace_id={r.randrange(16 ** 6):06x}")
        else:
            lines.append(f"   {ts} {level} {svc} {ms}   ")   # valid once stripped
    return lines


def _reference(lines):
    records = []
    skipped = 0
    for line in lines:
        line = line.strip()
        if not line:
            skipped += 1
            continue
        parts = line.split()
        if len(parts) != 4 or parts[1] not in LEVELS:
            skipped += 1
            continue
        try:
            ms = int(parts[3])
        except ValueError:
            skipped += 1
            continue
        records.append({"ts": parts[0], "level": parts[1],
                        "service": parts[2], "ms": ms})
    return records, skipped


def test_solve():
    r = rng()
    for _ in range(4):
        lines = _gen(r)
        assert solve(lines) == _reference(lines)
