"""Staging files in scratch space and tidying up afterwards is half of build tooling."""

import glob
import os
import shutil
import tempfile

from _lib import rng

META = {"topic": 40, "title": "shutil / tempfile / glob — stage files, then clean up",
        "tier": 3, "minutes": 18, "prereqs": []}


def solve(root):
    """`root` is a directory path as a STRING, holding a flat pile of files:
    some *.log, some *.tmp, some with other extensions. No subdirectories.

    Stage the interesting ones in scratch space and leave no mess behind:

      1. Make a scratch directory with tempfile — not a hardcoded /tmp/staging.
      2. COPY every *.log from root into it. The originals stay in root.
      3. MOVE every *.tmp from root into it. The originals leave root.
      4. Note what ended up in the scratch directory, then delete it.

    Return, with basenames only and never full paths:

        {"copied":  ["api.log", "web.log"],              # what you copied, sorted
         "moved":   ["build.tmp"],                       # what you moved, sorted
         "staged":  ["api.log", "build.tmp", "web.log"], # in scratch before you deleted it, sorted
         "left":    ["api.log", "notes.txt", "web.log"], # still in root at the end, sorted
         "cleaned": True}                                # the scratch directory is gone

    Match files with glob and a pattern, not by filtering os.listdir yourself.
    Copy with a shutil function that keeps the timestamps. os.path.basename
    turns a path into a bare filename.

    tempfile.TemporaryDirectory() used as a `with` block does step 1 and the
    delete in step 4 for you, including when something raises halfway through —
    which is the reason it exists.
    """
    raise NotImplementedError


HINTS = [
    "Three modules, one job each. tempfile invents a scratch path nobody else "
    "is using, so two runs of your script on the same box cannot collide. glob "
    "expands a shell-style pattern into real paths. shutil is the file "
    "operations you would otherwise shell out to cp, mv and rm -r. The one "
    "thing to be careful about: glob hands you full paths, and the answer wants "
    "bare filenames.",
    "glob.glob(os.path.join(root, '*.log')) lists the matches. shutil.copy2 "
    "copies a file into a directory and keeps its metadata; shutil.move moves "
    "one. os.listdir gives you the names already bare. Wrap the whole thing in "
    "`with tempfile.TemporaryDirectory() as stage:` and take your staged "
    "listing before the block ends — outside it the directory is gone, which "
    "is exactly how you check 'cleaned' with os.path.exists.",
    "Different tree, same moves:\n"
    "    import glob, os, shutil, tempfile\n"
    "    with tempfile.TemporaryDirectory() as stage:\n"
    "        for path in glob.glob('/var/backups/*.sql'):\n"
    "            shutil.copy2(path, stage)\n"
    "            print(os.path.basename(path))    # dump-2024.sql\n"
    "        print(sorted(os.listdir(stage)))     # ['dump-2024.sql']\n"
    "    print(os.path.exists(stage))             # False — the with block removed it\n"
    "Scratch space you did not name, and cleanup you cannot forget.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
