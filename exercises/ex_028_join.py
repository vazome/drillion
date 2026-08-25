"""split / join — the two directions of every parsing task."""

from _lib import rng

META = {"topic": 28, "title": "str — split, transform, join back", "tier": 3,
        "minutes": 8, "prereqs": []}


def solve(line):
    """WHY: A colleague pastes a list of service names into a ticket, separated
    by commas but with random spaces around each name. Your deploy tool
    needs the names clean, and the status page wants them shown separated by
    a vertical bar. This tidy-then-reformat step is the first line of nearly
    every script that takes text typed by a human.

    YOU GET: `line` — one string of comma-separated names with messy
    spacing, like " api, db ,cache ". The test creates it and hands it to
    you; you never build it yourself.

    YOU RETURN: one string with the names trimmed and joined by " | ", like
    "api | db | cache".

    ─── exact rules ───
    Given a comma-separated line with untidy spacing, return the fields
    trimmed and rejoined with " | ".

        "  api,  db ,cache "   ->   "api | db | cache"

    Empty fields never occur.
    """
    raise NotImplementedError


HINTS = [
    ("Three moves: break the line into pieces, clean each piece, glue them back "
    "with a different separator. You know all three by name."),
    ("split(',') gives the pieces. A string method removes whitespace from both "
    "ends of each piece. Then the separator you want does the gluing — and "
    "remember the separator owns that method, not the list."),
    ("Different data, same shape:\n"
    "    line = ' a; b ;c '\n"
    "    parts = [p.strip() for p in line.split(';')]\n"
    "    print(' - '.join(parts))    # 'a - b - c'\n"
    "join builds the gaps for you — never append separators by hand."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    words = r.sample(["api", "db", "cache", "queue", "auth", "cron", "web"],
                     r.randint(3, 6))
    pad = lambda w: " " * r.randint(0, 2) + w + " " * r.randint(0, 2)
    return ",".join(pad(w) for w in words)


def _reference(line):
    return " | ".join(p.strip() for p in line.split(","))


def test_solve():
    r = rng()
    for _ in range(4):
        line = _gen(r)
        assert solve(line) == _reference(line)
