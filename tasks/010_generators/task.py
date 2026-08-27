from collections.abc import Iterator


def solve(lines: Iterator[str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    """A short log with at least one ERROR line, somewhere unpredictable."""
    services = ["api", "auth", "billing", "cron", "db", "edge"]
    n = r.randint(6, 14)
    lines = []
    for _ in range(n):
        rid = "".join(r.choice("0123456789abcdef") for _ in range(4))
        lines.append(f"{r.choice(services)} {r.choice(['INFO', 'WARN', 'DEBUG'])} req={rid}")
    for i in r.sample(range(n), r.randint(1, max(1, n // 3))):
        svc, _, req = lines[i].split()
        lines[i] = f"{svc} ERROR {req}"
    return lines


def _reference(lines):
    for line in lines:
        _service, level, req = line.split()
        if level == "ERROR":
            yield req.split("=", 1)[1]


def _counting(lines, pulled):
    """Hands out lines one at a time, noting each one it was asked for."""
    for line in lines:
        pulled.append(line)
        yield line


def test_solve():
    import inspect

    r = rng()
    for _ in range(4):
        lines = _gen(r)
        expected = list(_reference(lines))

        got = solve(iter(lines))
        assert inspect.isgenerator(got), "solve must return a generator"
        assert list(got) == expected

        # laziness: reading one id must not drag the whole stream through
        pulled = []
        stream = solve(_counting(lines, pulled))
        assert pulled == [], "no lines should be read before the first next()"
        assert next(stream) == expected[0]
        stop = 1 + next(i for i, ln in enumerate(lines) if ln.split()[1] == "ERROR")
        assert len(pulled) == stop, "read past the first ERROR line — not lazy"
