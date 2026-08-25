"""Grouping records by a key is the most-typed loop in ops scripting."""

from _lib import rng

META = {"topic": 20, "title": "defaultdict(list) — group log lines by host", "tier": 3,
        "minutes": 10, "prereqs": [18], "tags": ["data-structures"]}


def solve(lines):
    """WHY: A central log collector mixes messages from every host into one
    stream. An engineer investigating an incident asks "show me everything
    each host said, host by host, in order". You need to sort the lines into
    buckets by host name, keeping the message text but dropping the severity
    word. Grouping records by a key is the most-typed loop in ops scripting.

    YOU GET: `lines` — a list of log lines like "web-1 ERROR disk full": a
    host name, a level word, then the message (which may contain spaces).
    The test creates it and hands it to you; you never build it yourself.

    YOU RETURN: a dict mapping each host to the list of its messages, in the
    order they appeared.

    ─── exact rules ───
    Group log messages by host. Return {host: [messages, in original order]}.

    Each line is "host level message":

        ["web-1 ERROR disk full",
         "db-1 WARN slow query",
         "web-1 INFO restarted"]
        ->
        {"web-1": ["disk full", "restarted"], "db-1": ["slow query"]}

    The message may contain spaces — keep it exactly as-is. Drop the level.
    A plain dict or a defaultdict both pass the test.
    """
    raise NotImplementedError


HINTS = [
    ("The pattern: for each record, work out its key, then append to that key's "
    "list. A plain dict raises KeyError the first time a key appears, so you'd "
    "be writing an if-check on every loop. There is a dict that skips that."),
    ("collections.defaultdict(list) creates the empty list the first time you "
    "touch a missing key, so the loop body is a single append. To split each "
    "line into exactly three parts, give split a maxsplit so the message keeps "
    "its spaces."),
    ("Different data, same shape:\n"
    "    from collections import defaultdict\n"
    "    by_team = defaultdict(list)\n"
    "    for team, player in [('red', 'ann'), ('blue', 'bo'), ('red', 'cy')]:\n"
    "        by_team[team].append(player)\n"
    "    print(dict(by_team))   # {'red': ['ann', 'cy'], 'blue': ['bo']}\n"
    "The first touch of by_team['red'] silently created the empty list."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    hosts = [f"{p}-{r.randint(1, 4)}" for p in r.sample(["web", "db", "cache", "worker", "proxy"], r.randint(2, 4))]
    msgs = ["disk full", "slow query on users", "restarted", "cert expires soon",
            "conn reset by peer", "high load", "OOM killed worker"]
    levels = ["INFO", "WARN", "ERROR"]
    return [f"{r.choice(hosts)} {r.choice(levels)} {r.choice(msgs)}"
            for _ in range(r.randint(8, 16))]


def _reference(lines):
    from collections import defaultdict
    groups = defaultdict(list)
    for line in lines:
        host, _level, msg = line.split(" ", 2)
        groups[host].append(msg)
    return dict(groups)


def test_solve():
    r = rng()
    for _ in range(4):
        lines = _gen(r)
        assert solve(list(lines)) == _reference(lines)
