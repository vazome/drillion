r"""Whole-task drill: watch a log that never ends and alert with context.

Combines topics 26 (line iteration), 29 (regex), 21 (deque).
"""

from _lib import rng

META = {"topic": 78, "title": "DRILL: tail a growing log, alert with context",
        "tier": 4, "minutes": 25, "prereqs": [21],
        "practices": [26, 29, 21]}


def solve(stream, pattern, window):
    r"""Follow a log as it grows and raise an alert on every match.

    `stream` is an ITERATOR of lines, the way tail -f hands them over: one
    line at a time, in order, each with its trailing newline. You cannot
    look ahead, you cannot count them first, and you must assume it never
    ends. `pattern` is a regex string with a named group "code".

    Return one dict per matching line:

        lines:   "10:02 INFO ok", "10:03 WARN slow", "10:04 ERROR E503 upstream"
        pattern: "ERROR (?P<code>E\d+)"
        window:  2

        ->  [{"line_no": 3,
              "code": "E503",
              "before": ["10:02 INFO ok", "10:03 WARN slow"]}]

    Rules:
      - line_no is 1-based and counts every line seen, not just matches.
      - Strip the trailing newline off every line you store.
      - "before" holds the last `window` lines seen before the match,
        oldest first. Near the start of the stream there are fewer, and
        that is fine. A matching line can itself show up in a later
        alert's "before".
      - Hold at most `window` lines in memory. Buffering the whole stream
        is the wrong answer even though the test would not catch it.

    "How would you alert on this log without reading 10 GB" is a real
    question. Say the memory argument out loud.
    """
    raise NotImplementedError


HINTS = [
    "Two things happen per line and they are independent: you ask whether "
    "this line matches, and you keep a rolling memory of the few lines behind "
    "it. The memory is the interesting half — a plain list plus a slice grows "
    "forever, and the container you want throws the oldest item away by "
    "itself.",
    "collections.deque(maxlen=window) for the history. re.compile(pattern) "
    "once, above the loop, never inside it, then m = rx.search(line) and "
    "m.group('code') for the named group. enumerate(stream, start=1) gives "
    "you the line number. Order matters at the end of the loop body: snapshot "
    "with list(history) while you build the alert, and append the current "
    "line after that, so a line is never in its own context.",
    "Different data, same three moves:\n"
    "    import re\n"
    "    from collections import deque\n"
    "    rx = re.compile(r'user=(?P<who>\\w+)')\n"
    "    seen = deque(maxlen=2)\n"
    "    for i, line in enumerate(['boot', 'idle', 'login user=ana'], start=1):\n"
    "        m = rx.search(line)\n"
    "        if m:\n"
    "            print(i, m.group('who'), list(seen))   # 3 ana ['boot', 'idle']\n"
    "        seen.append(line)\n"
    "Yours strips the newline first and collects dicts instead of printing.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    style = r.choice(["plain", "logfmt"])
    codes = ["E500", "E503", "E404", "E429"]
    msgs = ["upstream timeout", "disk full", "conn reset", "slow query",
            "cache miss"]
    rate = r.choice([0.15, 0.3, 0.5])
    lines = []
    for i in range(r.randint(12, 30)):
        msg = r.choice(msgs)
        if r.random() < rate:
            code = r.choice(codes)
            lines.append(f"10:{i:02d} ERROR {code} {msg}\n" if style == "plain"
                         else f't=10:{i:02d} level=error code={code} msg="{msg}"\n')
        else:
            level = r.choice(["INFO", "WARN"])
            lines.append(f"10:{i:02d} {level} {msg}\n" if style == "plain"
                         else f't=10:{i:02d} level={level.lower()} msg="{msg}"\n')
    pattern = (r"ERROR (?P<code>E\d+)" if style == "plain"
               else r"level=error code=(?P<code>E\d+)")
    return lines, pattern, r.randint(2, 4)


def _reference(stream, pattern, window):
    import re
    from collections import deque
    rx = re.compile(pattern)
    history = deque(maxlen=window)
    alerts = []
    for line_no, raw in enumerate(stream, start=1):
        line = raw.rstrip("\n")
        m = rx.search(line)
        if m:
            alerts.append({"line_no": line_no, "code": m.group("code"),
                           "before": list(history)})
        history.append(line)
    return alerts


def test_solve():
    r = rng()
    for _ in range(4):
        lines, pattern, window = _gen(r)
        assert (solve(iter(lines), pattern, window)
                == _reference(iter(lines), pattern, window))
