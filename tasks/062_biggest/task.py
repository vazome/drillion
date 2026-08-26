def solve(root, n):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    import tempfile
    from pathlib import Path
    root = Path(tempfile.mkdtemp(prefix="ex074_"))
    dirs = [root]
    for name in r.sample(["api", "web", "db", "cron", "cache", "auth"],
                         r.randint(2, 4)):
        logs = root / name / "logs"
        logs.mkdir(parents=True)
        dirs += [root / name, logs]
    sizes = [50, 120, 400, 900, 1500, 2400, 3300]
    for i in range(r.randint(4, 12)):
        d = r.choice(dirs)
        (d / f"f{i}.dat").write_text("x" * r.choice(sizes), encoding="utf-8")
    return str(root), r.randint(2, 5)


def _reference(root, n):
    from pathlib import Path
    root = Path(root)
    files = [(p.relative_to(root).as_posix(), p.stat().st_size)
             for p in root.rglob("*") if p.is_file()]
    files.sort(key=lambda t: (-t[1], t[0]))
    return files[:n]


def test_solve():
    import shutil
    r = rng()
    for _ in range(3):
        root, n = _gen(r)
        try:
            got = [tuple(row) for row in solve(root, n)]
            assert got == _reference(root, n)
        finally:
            shutil.rmtree(root, ignore_errors=True)
