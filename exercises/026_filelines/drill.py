def solve(path):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    import tempfile
    levels = ["INFO", "INFO", "WARN", "ERROR"]
    msgs = ["disk full", "sync done", "node down", "cert expiring",
            "pod evicted", "backup ok", "queue lagging", "restart requested"]
    with tempfile.NamedTemporaryFile("w", prefix="ex026_", suffix=".log",
                                     delete=False, encoding="utf-8") as f:
        for _ in range(r.randint(8, 25)):
            f.write(f"{r.choice(levels)} {r.choice(msgs)} "
                    f"on node-{r.randint(1, 9)}\n")
        return f.name


def _reference(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("ERROR "):
                out.append(line[len("ERROR "):])
    return out


def test_solve():
    import os
    r = rng()
    for _ in range(4):
        path = _gen(r)
        try:
            assert solve(path) == _reference(path)
        finally:
            os.unlink(path)
