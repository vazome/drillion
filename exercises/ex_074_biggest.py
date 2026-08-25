"""Whole-task drill: the disk is full and someone wants the top offenders now.

Combines topics 27 (pathlib), 9 (sort key), 40 (tempfile).
"""

from _lib import rng

META = {"topic": 74, "title": "DRILL: N largest files under a directory tree",
        "tier": 4, "minutes": 25, "prereqs": [27],
        "practices": [27, 9, 40]}


def solve(root, n):
    """WHY: A server's disk is almost full and the on-call engineer needs to
    know, right now, which files are eating the space so they can delete or
    move the biggest ones. "Show me the five largest files under /var" is
    the question. A list sorted biggest-first is what they act on.

    YOU GET: `root` — a folder path as text, like "/tmp/ex074_abc". The test
    creates a small temporary folder tree with files of different sizes and
    hands you the path; you never build it yourself.

    `n` — a whole number, like 3: how many of the biggest files to report.

    YOU RETURN: a list of pairs, biggest file first. Each pair is (the
    file's path relative to root, its size in bytes), like
    [("api/logs/app.log", 900), ("web/index.html", 400)].

    ─── exact rules ───
    A disk is filling up. Find the n biggest files under `root`.

    `root` is a directory path as a STRING. Return a list of
    (relative_path, size_in_bytes) pairs, biggest first:

        root/
          api/logs/app.log      900 bytes
          api/logs/old.log      120 bytes
          web/index.html        400 bytes

        solve(root, 2)  ->  [("api/logs/app.log", 900), ("web/index.html", 400)]

    Details that matter:
      - Search the whole tree, at any depth. Directories are not files.
      - The path is relative to root, forward slashes, no leading "./".
      - Ties: same size, then smaller path first (plain string order).
      - Fewer than n files in the tree: return all of them.

    Say the plan out loud before you type: collect, sort, slice.
    """
    raise NotImplementedError


HINTS = [
    ("Three steps, and only the middle one is interesting: collect every file "
    "with its size, sort, take the first n. Sorting is where people stall, "
    "because you want one direction for size and the other for the path. One "
    "key expression does both, no second sort pass."),
    ("Path(root).rglob('*') walks the whole tree; p.is_file() drops the "
    "directories. p.stat().st_size is the size, p.relative_to(root).as_posix() "
    "is the name you report. Sort with key=lambda t: (-t[1], t[0]) — negating "
    "the number flips that field to descending while the string stays "
    "ascending. Then slice [:n]."),
    ("Different data, same two moves:\n"
    "    rows = [('pod-b', 3), ('pod-a', 3), ('pod-c', 9)]\n"
    "    rows.sort(key=lambda t: (-t[1], t[0]))\n"
    "    print(rows)      # [('pod-c', 9), ('pod-a', 3), ('pod-b', 3)]\n"
    "\n"
    "    from pathlib import Path\n"
    "    p = Path('/var/log/nginx/access.log')\n"
    "    print(p.relative_to('/var/log').as_posix())   # nginx/access.log\n"
    "A slice past the end is not an error, so [:n] handles the short tree "
    "for free."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
