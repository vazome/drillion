"""Every ops script starts by reading a file that is bigger than you would like."""

from _lib import rng

META = {"topic": 26, "title": "open() — stream a file line by line", "tier": 3,
        "minutes": 10, "prereqs": []}


def solve(path):
    """`path` is a log file. Every line is a LEVEL, a space, then a message:

        INFO backup ok on node-3
        ERROR disk full on node-7
        WARN cert expiring on node-2

    Open it with encoding="utf-8" and return the messages of the ERROR
    lines, in file order, newline stripped:

        ["disk full on node-7"]

    Pretend the file is 40 GB. Do not call .read() or .readlines() — an
    open file object is already an iterable that yields one line at a
    time, in constant memory. A file with no ERROR lines returns [].
    """
    raise NotImplementedError


HINTS = [
    "A file object is its own iterator: looping over it gives one line at a "
    "time and never holds the whole file. .readlines() builds the entire list "
    "in memory first — fine at 50 MB, fatal at 40 GB. One more thing: every "
    "line you get still ends with its newline character.",
    "Three pieces: with plus open(path, encoding='utf-8'), a for loop directly "
    "over the handle, and per line — strip the newline, test the level with "
    "startswith, cut the level off the front with a slice or split. Append "
    "matches to a list as you go.",
    "Different data, same skeleton — summing a column from a huge file:\n"
    "    # each line of sizes.txt looks like: '512 backup.tar'\n"
    "    total = 0\n"
    "    with open('sizes.txt', encoding='utf-8') as f:\n"
    "        for line in f:\n"
    "            total += int(line.split()[0])\n"
    "Open once, loop the handle, handle each line, never hold the whole file.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
