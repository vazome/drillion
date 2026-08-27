def solve(root: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    import tempfile
    from pathlib import Path
    root = Path(tempfile.mkdtemp(prefix="ex027_"))
    services = r.sample(["api", "auth", "billing", "cron", "web", "worker"],
                        r.randint(2, 4))
    for svc in services:
        logs = root / svc / "logs"
        logs.mkdir(parents=True)
        for i in range(r.randint(1, 3)):
            (logs / f"{svc}-{i}.log").write_text(f"line {i}\n", encoding="utf-8")
        if r.random() < 0.7:
            conf = root / svc / "conf"
            conf.mkdir()
            (conf / f"{svc}.conf").write_text("k: v\n", encoding="utf-8")
    (root / services[0] / "notes.txt").write_text("scratch\n", encoding="utf-8")
    if r.random() < 0.5:
        (root / "README.md").write_text("readme\n", encoding="utf-8")
    return str(root)


def _reference(root):
    from pathlib import Path
    root = Path(root)
    return {"logs": sorted(p.name for p in root.rglob("*.log")),
            "conf_stems": sorted(p.stem for p in root.rglob("*.conf")),
            "has_readme": (root / "README.md").exists()}


def test_solve():
    import shutil
    r = rng()
    for _ in range(3):
        root = _gen(r)
        try:
            assert solve(root) == _reference(root)
        finally:
            shutil.rmtree(root, ignore_errors=True)
