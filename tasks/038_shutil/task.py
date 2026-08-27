def solve(root: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import glob
import os
import shutil
import tempfile

from _lib import rng


def _gen(r):
    """A list of filenames. Built twice so solve and the reference each get
    their own identical tree — solve moves files, so they cannot share one."""
    services = r.sample(["api", "web", "db", "cache", "worker", "auth"],
                        r.randint(2, 4))
    names = [f"{s}.log" for s in services[: r.randint(1, len(services))]]
    for s in services:
        if r.random() < 0.6:
            names.append(f"{s}-{r.randint(1, 9)}.tmp")
    names += r.sample(["notes.txt", "README.md", "config.yaml", "data.json",
                       "Makefile", "chart.tgz"], r.randint(1, 3))
    r.shuffle(names)
    return names


def _build(names):
    root = tempfile.mkdtemp(prefix="ex040_")
    for name in names:
        with open(os.path.join(root, name), "w", encoding="utf-8") as f:
            f.write(f"contents of {name}\n")
    return root


def _reference(root):
    copied, moved = [], []
    with tempfile.TemporaryDirectory() as stage:
        for path in sorted(glob.glob(os.path.join(root, "*.log"))):
            shutil.copy2(path, stage)
            copied.append(os.path.basename(path))
        for path in sorted(glob.glob(os.path.join(root, "*.tmp"))):
            shutil.move(path, stage)
            moved.append(os.path.basename(path))
        staged = sorted(os.listdir(stage))
    return {"copied": copied, "moved": moved, "staged": staged,
            "left": sorted(os.listdir(root)), "cleaned": not os.path.exists(stage)}


def test_solve():
    r = rng()
    for _ in range(3):
        names = _gen(r)
        mine, ref = _build(names), _build(names)
        try:
            assert solve(mine) == _reference(ref)
        finally:
            shutil.rmtree(mine, ignore_errors=True)
            shutil.rmtree(ref, ignore_errors=True)
