"""tail -f in Python: keep the newest few lines, forget the rest automatically."""

from _lib import rng

META = {"topic": 21, "title": "deque(maxlen) — tail of a stream", "tier": 3,
        "minutes": 10, "prereqs": []}


def solve(lines, n):
    """WHY: An incident is in progress and the on-call engineer asks "what were
    the last five errors?" The log is a live stream, far too large to hold
    in memory, and you only get to read it once, front to back. You need to
    keep just the newest few matching lines as you go and forget the rest
    automatically. This is tail -f done in Python.

    YOU GET: `lines` — a stream of log lines like "10:01 ERROR boom" that
    you can walk through exactly once. `n` — how many of the latest ERROR
    lines to keep, like 3. The test creates them and hands them to you; you
    never build them yourself.

    YOU RETURN: a list of the last `n` lines containing "ERROR", oldest
    first (or all of them if there were fewer than `n`).

    ─── exact rules ───
    Return the last n ERROR lines of a log stream, oldest first, as a list.

    lines is an ITERATOR — you can loop over it exactly once. No len(),
    no lines[-n:], and buffering everything into a list defeats the point
    (pretend the stream is 10 GB).

        iter(["10:00 INFO ok", "10:01 ERROR boom", "10:02 ERROR again"]), 1
        ->  ["10:02 ERROR again"]

    A line counts if it contains "ERROR". If fewer than n match, return
    all of them.
    """
    raise NotImplementedError


HINTS = [
    ("You cannot slice an iterator, and keeping every line just to throw most "
    "away is the wrong shape. You want a container that holds at most n items "
    "and evicts the oldest by itself when a new one arrives."),
    ("collections.deque(maxlen=n). Loop once over the stream, append each "
    "matching line; once the deque is full, every append silently drops the "
    "oldest entry. Wrap it in list() at the end."),
    ("Different data, same shape:\n"
    "    from collections import deque\n"
    "    last3 = deque(maxlen=3)\n"
    "    for x in range(1, 8):\n"
    "        last3.append(x)\n"
    "    print(list(last3))   # [5, 6, 7]\n"
    "Same trick with lines instead of numbers, plus your filter before the append."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    n = r.randint(3, 6)
    total = r.randint(10, 30)
    err_rate = r.choice([0.15, 0.3, 0.6])
    msgs = ["disk full", "timeout upstream", "restarted", "cache miss",
            "slow query", "conn reset"]
    lines = []
    for i in range(total):
        level = "ERROR" if r.random() < err_rate else r.choice(["INFO", "WARN"])
        lines.append(f"10:{i:02d} {level} {r.choice(msgs)}")
    return lines, n


def _reference(lines, n):
    from collections import deque
    tail = deque(maxlen=n)
    for line in lines:
        if "ERROR" in line:
            tail.append(line)
    return list(tail)


def test_solve():
    r = rng()
    for _ in range(4):
        lines, n = _gen(r)
        assert solve(iter(lines), n) == _reference(iter(lines), n)
