"""Pulling fields out of log lines is the regex work ops actually does."""

from _lib import rng

META = {"topic": 29, "title": "re — named groups on log lines", "tier": 3,
        "minutes": 15, "prereqs": []}


def solve(text):
    """Extract structured records from a raw log blob.

    text is one multi-line string. The lines you want look like:

        2026-08-12T09:14:02 level=ERROR host=web-1 msg="disk full on /var" trace="a9f3c2"

    Return a list of dicts, one per matching line, in file order:

        [{"level": "ERROR", "host": "web-1", "msg": "disk full on /var"}, ...]

    Ignore the timestamp and trace. Some lines are noise (stack-trace
    continuations and the like) — they match nothing and must be skipped.
    Careful: msg contains spaces, and there is another quoted field after
    it. A greedy .* will eat its way into trace.
    """
    raise NotImplementedError


HINTS = [
    "One pattern, compiled once, applied across the whole text. Named groups "
    "give you a dict per match instead of counting parentheses. And look at "
    "how many double quotes sit after msg= on a line — think about which one "
    "a greedy match stops at (hint: the last one).",
    "re.compile the pattern; (?P<name>...) names a group; pat.finditer(text) "
    "yields match objects and m.groupdict() is exactly the dict you need "
    "(findall would hand you bare tuples, names lost). For the quoted msg "
    "use .*? or [^\"]* so it stops at the FIRST closing quote.",
    "Different data, same shape:\n"
    "    import re\n"
    "    pat = re.compile(r'user=(?P<user>\\w+) cmd=\"(?P<cmd>.*?)\"')\n"
    "    log = 'user=ann cmd=\"rm -rf /tmp\" id=\"7\"\\nplain noise\\nuser=bo cmd=\"ls\" id=\"9\"'\n"
    "    print([m.groupdict() for m in pat.finditer(log)])\n"
    "    # [{'user': 'ann', 'cmd': 'rm -rf /tmp'}, {'user': 'bo', 'cmd': 'ls'}]\n"
    "With a greedy .* the first cmd would swallow everything up to id=\"7\".",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    hosts = [f"{r.choice(['web', 'db', 'cache'])}-{r.randint(1, 9)}" for _ in range(3)]
    msgs = ["disk full on /var", "connection reset by peer", "cert expires in 3 days",
            "OOM killed worker 4", "replica lag high", "retry budget exhausted"]
    noise = ["    at worker.py:88 in flush()",
             "Traceback (most recent call last):",
             "    retrying in 5s..."]
    lines = []
    for _ in range(r.randint(5, 10)):
        ts = (f"2026-08-{r.randint(10, 28):02d}T"
              f"{r.randint(0, 23):02d}:{r.randint(0, 59):02d}:{r.randint(0, 59):02d}")
        lines.append(f'{ts} level={r.choice(["INFO", "WARN", "ERROR"])} '
                     f'host={r.choice(hosts)} msg="{r.choice(msgs)}" '
                     f'trace="{r.randint(0, 16**6 - 1):06x}"')
        if r.random() < 0.4:
            lines.append(r.choice(noise))
    return "\n".join(lines)


def _reference(text):
    import re
    pat = re.compile(r'level=(?P<level>[A-Z]+) host=(?P<host>[\w-]+) msg="(?P<msg>.*?)"')
    return [m.groupdict() for m in pat.finditer(text)]


def test_solve():
    r = rng()
    for _ in range(4):
        text = _gen(r)
        assert solve(text) == _reference(text)
