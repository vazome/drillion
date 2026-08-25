"""enumerate and zip replace every clumsy `for i in range(len(...))`."""

from _lib import rng

META = {"topic": 5, "title": "enumerate + zip — pair and number", "tier": 3,
        "minutes": 8, "prereqs": []}


def solve(hosts, ips):
    """WHY: You have two lists that belong together: server names and the IP
    addresses assigned to them, in matching order. A teammate asks for a
    numbered inventory they can paste into a ticket: "1. web 10.0.0.1",
    "2. db 10.0.0.2", and so on. Walking two lists side by side while
    numbering the lines is one of the most common small jobs in ops
    scripting.

    YOU GET: `hosts` — a list of server names like ["web", "db"].
    `ips` — a list of IP address strings like ["10.0.0.1", "10.0.0.2"], the
    same length, in the same order. The test creates them and hands them to
    you; you never build them yourself.

    YOU RETURN: a list of strings, one per server, numbered from 1.

    ─── exact rules ───
    Pair each host with its ip and number the lines starting from 1.
    Return a list of strings shaped "N. host ip":

        ["web", "db"], ["10.0.0.1", "10.0.0.2"]
        ->  ["1. web 10.0.0.1", "2. db 10.0.0.2"]

    The lists are always the same length. No manual counter and no
    range(len(...)) — that avoidance is the whole drill.
    """
    raise NotImplementedError


HINTS = [
    ("Two jobs at once: walking two lists in step, and counting from 1. "
    "Python has one builtin for each; used together they hand you everything "
    "the loop body needs."),
    ("zip(hosts, ips) yields pairs. enumerate(..., start=1) wraps any "
    "iterable and yields (number, item) — here the item IS a pair, so the "
    "for line unpacks a number and a parenthesised pair."),
    ("Different data, same shape:\n"
    "    names = ['ada', 'linus']\n"
    "    langs = ['math', 'c']\n"
    "    for i, (n, lang) in enumerate(zip(names, langs), start=1):\n"
    "        print(f'{i}: {n} likes {lang}')\n"
    "    # 1: ada likes math\n"
    "    # 2: linus likes c\n"
    "Collect into a list instead of printing."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    pool = ["web", "db", "cache", "auth", "queue", "cron", "proxy"]
    hosts = r.sample(pool, r.randint(3, 6))
    ips = [f"10.0.{r.randint(0, 9)}.{r.randint(1, 99)}" for _ in hosts]
    return hosts, ips


def _reference(hosts, ips):
    return [f"{i}. {h} {ip}"
            for i, (h, ip) in enumerate(zip(hosts, ips), start=1)]


def test_solve():
    r = rng()
    for _ in range(4):
        hosts, ips = _gen(r)
        assert solve(list(hosts), list(ips)) == _reference(hosts, ips)
