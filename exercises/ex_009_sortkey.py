"""sorted(key=...) — top-3 most-used Python in interviews."""

from _lib import rng

META = {"topic": 9, "title": "sorted with key=", "tier": 3,
        "minutes": 10, "prereqs": []}


def solve(services):
    """Each item is [name, restarts]. Return the list sorted by restarts,
    MOST restarts first. Keep the pairs intact.

        [["api", 2], ["db", 9], ["web", 5]]
        ->  [["db", 9], ["web", 5], ["api", 2]]
    """
    raise NotImplementedError


HINTS = [
    "sorted() on pairs sorts by the FIRST element by default — the name. You "
    "need it to look at the second instead, and to count downwards.",
    "sorted() takes two extra arguments here: one that says which part of each "
    "item to compare, and one that flips the direction. The first wants a "
    "function, not a number.",
    "Different data, same shape:\n"
    "    pairs = [['ny', 8.4], ['berlin', 3.6], ['tokyo', 14.0]]\n"
    "    print(sorted(pairs, key=lambda p: p[1], reverse=True))\n"
    "    # [['tokyo', 14.0], ['ny', 8.4], ['berlin', 3.6]]\n"
    "lambda p: p[1] means 'given one pair, compare its second slot'.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    names = ["api", "db", "web", "cache", "queue", "auth", "cron"]
    picked = r.sample(names, r.randint(4, 7))
    counts = r.sample(range(0, 41), len(picked))    # distinct: no tie ambiguity
    return [[n, c] for n, c in zip(picked, counts)]


def _reference(services):
    return sorted(services, key=lambda s: s[1], reverse=True)


def test_solve():
    r = rng()
    for _ in range(4):
        svc = _gen(r)
        assert solve([list(s) for s in svc]) == _reference(svc)
