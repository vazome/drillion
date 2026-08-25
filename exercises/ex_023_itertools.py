"""itertools glues paged streams together; groupby bites everyone exactly once."""

from _lib import rng

META = {"topic": 23, "title": "itertools — chain, islice, groupby (sort first)", "tier": 3,
        "minutes": 15, "prereqs": [9]}


def solve(pages, first_n):
    """WHY: An on-call engineer is paged at 2am. The log service hands back log
    lines in pages (batches), the way an API says "here are the next 50
    results". The incident lead asks: "in the first N lines after the alert
    fired, how many came from each service?" to see which service got noisy
    first. You stitch the pages into one stream, stop after N lines, and
    count per service.

    YOU GET: `pages` — a list of lists of strings; each inner list is one
    page of log lines, like [["api ERROR boom", "db INFO ok"], ["api WARN
    slow"]]. Every line starts with the service name. The test creates it
    and hands it to you; you never build it yourself.

    YOU GET: `first_n` — a whole number like 3: how many lines from the
    start of the combined stream to look at.

    YOU RETURN: a list of (service, count) pairs sorted by service name,
    like [("api", 2), ("db", 1)].

    ─── exact rules ───
    Count log lines per service in the head of a paged stream.

    pages is a list of pages, each page a list of log lines — the shape a
    paginated API hands you. The service name is the first word of a line.
    Look at only the FIRST first_n lines of the combined stream, and return
    [(service, count), ...] sorted by service name.

        pages = [["api ERROR boom", "db INFO ok"], ["api WARN slow", "db INFO ok"]]
        solve(pages, 3)  ->  [("api", 2), ("db", 1)]

    Use itertools: chain the pages into one stream, islice the head, groupby
    to count. The lines are interleaved on purpose — groupby on unsorted
    data will give you the same service more than once.
    """
    raise NotImplementedError


HINTS = [
    ("Three small jobs: flatten the pages into one stream, cut it to the first "
    "N, count per service. itertools has a tool for each. The counting one has "
    "a famous catch: it only merges neighbours."),
    ("chain.from_iterable(pages) flattens; islice(stream, n) takes the head "
    "without materialising the rest; groupby(rows, key=...) yields (key, group) "
    "pairs — but only for ADJACENT equal keys, so sort by that same key first. "
    "len(list(group)) counts a group."),
    ("Different data, same trap:\n"
    "    from itertools import groupby\n"
    "    animals = ['cat', 'dog', 'cat', 'cat', 'dog']\n"
    "    print([(k, len(list(g))) for k, g in groupby(animals)])\n"
    "    # [('cat', 1), ('dog', 1), ('cat', 2), ('dog', 1)]   <- unsorted: wrong\n"
    "    print([(k, len(list(g))) for k, g in groupby(sorted(animals))])\n"
    "    # [('cat', 3), ('dog', 2)]\n"
    "groupby is a run-length grouper, not SQL GROUP BY."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    services = r.sample(["api", "auth", "billing", "cron", "db", "ingest"], r.randint(3, 4))
    lines = [f"{s} {r.choice(['INFO', 'WARN', 'ERROR'])} req={r.randint(100, 999)}"
             for s in services for _ in range(r.randint(2, 5))]
    total = len(lines)
    first_n = r.randint(max(4, total * 2 // 3), total - 1)
    while True:                      # ensure the head really is interleaved
        r.shuffle(lines)
        keys = [ln.split()[0] for ln in lines[:first_n]]
        runs = sum(1 for i, k in enumerate(keys) if i == 0 or k != keys[i - 1])
        if runs > len(set(keys)):    # some service occurs in two separate runs
            break
    cut = sorted(r.sample(range(1, total), r.randint(1, 2)))
    pages = [lines[i:j] for i, j in zip([0] + cut, cut + [total])]
    return pages, first_n


def _reference(pages, first_n):
    from itertools import chain, groupby, islice
    svc = lambda line: line.split()[0]
    head = sorted(islice(chain.from_iterable(pages), first_n), key=svc)
    return [(s, len(list(grp))) for s, grp in groupby(head, key=svc)]


def test_solve():
    r = rng()
    for _ in range(4):
        pages, first_n = _gen(r)
        assert solve([list(p) for p in pages], first_n) == _reference(pages, first_n)
