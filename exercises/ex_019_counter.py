"""Top-N counting — the single most-asked DevOps screen question."""

from _lib import rng

META = {"topic": 19, "title": "Counter — top N by frequency", "tier": 3,
        "minutes": 12, "prereqs": [18]}


def solve(lines, n):
    """Return the n most frequent IPs as a list of (ip, count) tuples,
    busiest first.

    Each line looks like:  "10.0.0.4 GET /health 200"
    The IP is the first field.

    Ties: whichever order your tool produces is fine.
    """
    raise NotImplementedError


HINTS = [
    "You need to count how often each IP appears, then take the biggest few. "
    "The `collections` module has a class built for exactly the counting half.",
    "collections.Counter(some_list) counts everything for you. Feed it just the "
    "IPs — one per line. Then look at Counter's methods for one that returns the "
    "top N already sorted.",
    "Different data, same shape:\n"
    "    from collections import Counter\n"
    "    words = ['a', 'b', 'a', 'c', 'a', 'b']\n"
    "    print(Counter(words).most_common(2))   # [('a', 3), ('b', 2)]\n"
    "Your job is turning `lines` into that flat list of IPs first.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    ips = [f"10.0.{r.randint(0, 5)}.{i}" for i in range(1, 6)]
    weights = r.sample([12, 8, 5, 3, 1], 5)
    pool = [ip for ip, w in zip(ips, weights) for _ in range(w)]
    r.shuffle(pool)
    paths = ["/api/users", "/health", "/api/orders"]
    lines = [f"{ip} GET {r.choice(paths)} {r.choice([200, 200, 404, 500])}" for ip in pool]
    return lines, r.choice([2, 3])


def _reference(lines, n):
    from collections import Counter
    return Counter(line.split()[0] for line in lines).most_common(n)


def test_solve():
    r = rng()
    for _ in range(4):
        lines, n = _gen(r)
        assert solve(lines, n) == _reference(lines, n)
