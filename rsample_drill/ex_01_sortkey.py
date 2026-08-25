"""sorted(key=...) — top-3 most-used Python in interviews."""
# READ FIRST:
#   https://docs.python.org/3/howto/sorting.html  — key=, reverse=, and why Python's sort is 'stable' (ties keep order)
#   https://realpython.com/python-sort/  — same, slower and with pictures
# (copy of exercises/ex_009_sortkey.py — same file, just placed in the take-home order)

from _lib import rng

META = {
    "topic": 1,
    "title": "sorted with key=",
    "tier": 3,
    "minutes": 10,
    "prereqs": [],
}


def solve(services: list):
    """WHY: A team lead asks "which services are crashing the most?" You have a
    list of services and how many times each one restarted this week. They
    want the list ordered worst-first so the top of the page is where the
    attention should go. Ordering a list of records by one particular field
    is the single most common data task in ops reporting.

    YOU GET: `services` — a list of two-item lists like [["api", 2], ["db",
    9]], each holding a service name and its restart count. The test creates
    it and hands it to you; you never build it yourself.

    YOU RETURN: the same two-item lists, reordered so the highest restart
    count comes first.

    ─── exact rules ───
    Each item is [name, restarts]. Return the list sorted by restarts,
    MOST restarts first. Keep the pairs intact.

        [["api", 2], ["db", 9], ["web", 5]]
        ->  [["db", 9], ["web", 5], ["api", 2]]
    """
    services = sorted(services, reverse=True, key=lambda age: age[1])
    print(services)

    return services


HINTS = [
    (
        "sorted() on pairs sorts by the FIRST element by default — the name. You "
        "need it to look at the second instead, and to count downwards."
    ),
    (
        "sorted() takes two extra arguments here: one that says which part of each "
        "item to compare, and one that flips the direction. The first wants a "
        "function, not a number."
    ),
    (
        "Different data, same shape:\n"
        "    pairs = [['ny', 8.4], ['berlin', 3.6], ['tokyo', 14.0]]\n"
        "    print(sorted(pairs, key=lambda p: p[1], reverse=True))\n"
        "    # [['tokyo', 14.0], ['ny', 8.4], ['berlin', 3.6]]\n"
        "lambda p: p[1] means 'given one pair, compare its second slot'."
    ),
]


# ─────────────────────────────  below here is the machinery  ──────────────


def _gen(r):
    names = ["api", "db", "web", "cache", "queue", "auth", "cron"]
    picked = r.sample(names, r.randint(4, 7))
    counts = r.sample(range(41), len(picked))  # distinct: no tie ambiguity
    return [[n, c] for n, c in zip(picked, counts)]


def _reference(services):
    return sorted(services, key=lambda s: s[1], reverse=True)


def test_solve():
    r = rng()
    for _ in range(4):
        svc = _gen(r)
        assert solve([list(s) for s in svc]) == _reference(svc)
