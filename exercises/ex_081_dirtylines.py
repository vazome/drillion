"""Interviewers feed you a log with junk in it on purpose; one bad line must not kill the run."""

from _lib import rng

META = {"topic": 81, "title": "defensive parsing — skip the junk, count it",
        "tier": 3, "minutes": 15, "prereqs": [43]}

LEVELS = {"DEBUG", "INFO", "WARN", "ERROR"}


def solve(lines):
    """WHY: A log export from a customer has junk mixed in: blank lines,
    lines cut short, a field that should be a number but says "N/A". Someone
    in support wants the good records loaded so they can look at response
    times. A script that crashes on the first bad line is useless; a script
    that quietly throws lines away is worse, because nobody learns that 40%
    of the data went missing. So: keep what you can, and count what you
    dropped.

    YOU GET: `lines` — a list of strings, one per log line, like
    ["2026-08-12T10:12:44Z INFO checkout 137", "", "2026-08-12T10:12:46Z
    WARN cart"]. The test builds it, junk included, and hands it to you.

    YOU RETURN: a pair (records, skipped). records is a list of
    dictionaries, one per good line, with "ts", "level", "service" and "ms"
    (a number). skipped is how many lines you threw away.

    ─── exact rules ───
    Parse the good lines out of a dirty log. Report how many you dropped.

    A good line is exactly four whitespace-separated fields:

        2026-08-12T10:12:44Z INFO checkout 137
        <timestamp>          <level> <service> <latency in ms>

    Return the tuple (records, skipped):

      - records: a list, in input order, of
        {"ts": <str>, "level": <str>, "service": <str>, "ms": <int>}
        Note ms is an int, not the string you split out.
      - skipped: how many lines you did not turn into a record.

    Skip a line, without raising, when any of these is true:
      - it is empty or only whitespace
      - it does not split into exactly 4 fields (too few or too many)
      - the level is not one of DEBUG, INFO, WARN, ERROR (case matters)
      - the last field is not a whole number

        ["2026-08-12T10:12:44Z INFO checkout 137",
         "2026-08-12T10:12:45Z info checkout 12",     # lowercase level
         "2026-08-12T10:12:46Z WARN cart",            # only 3 fields
         "2026-08-12T10:12:47Z ERROR cart N/A"]       # ms is not a number
        ->  ([{"ts": "2026-08-12T10:12:44Z", "level": "INFO",
               "service": "checkout", "ms": 137}], 3)

    The count matters as much as the parsing. A parser that silently
    drops 40% of your log is worse than one that crashes, because
    nobody finds out.
    """
    raise NotImplementedError


HINTS = [
    ("The instinct is one try/except wrapped around the whole loop. That "
    "stops at the first bad line and throws away everything after it. The "
    "unit of failure here is a single line, so the handling belongs inside "
    "the loop. Second thing to notice: only one of the four failure modes "
    "actually raises — a wrong level is just a value you have to check for "
    "yourself."),
    ("Per line: strip it, skip if falsy, parts = line.split(), skip if "
    "len(parts) != 4, skip if parts[1] not in the allowed set, then wrap "
    "int(parts[3]) in try/except ValueError. Use `continue` on every skip "
    "path so the append at the bottom only runs for lines that survived "
    "all four checks. Keep one counter alongside the results list."),
    ("Different data — reading key=value tokens where some are malformed:\n"
    "    good, bad = {}, 0\n"
    "    for token in ['cpu=2', 'mem', 'disk=x', '  ']:\n"
    "        token = token.strip()\n"
    "        key, sep, raw = token.partition('=')\n"
    "        if not sep:\n"
    "            bad += 1\n"
    "            continue\n"
    "        try:\n"
    "            good[key] = int(raw)\n"
    "        except ValueError:\n"
    "            bad += 1\n"
    "            continue\n"
    "    print(good, bad)     # {'cpu': 2} 3\n"
    "Same shape: check what you can check with `in` and len, and catch only "
    "the conversion that genuinely raises."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    services = ["checkout", "cart", "auth", "search", "billing", "cdn"]
    lines = []
    for _ in range(r.randint(8, 20)):
        ts = f"2026-08-{r.randint(1, 28):02d}T{r.randint(0, 23):02d}:{r.randint(0, 59):02d}:{r.randint(0, 59):02d}Z"
        level = r.choice(sorted(LEVELS))
        svc = r.choice(services)
        ms = r.randint(1, 4000)
        if r.random() < 0.65:
            lines.append(f"{ts} {level} {svc} {ms}")
            continue
        # corrupt it, one of several distinct ways
        kind = r.choice(["truncated", "blank", "bad-level", "bad-ms", "extra", "padded"])
        if kind == "truncated":
            lines.append(r.choice([f"{ts} {level} {svc}", f"{ts} {level}", ts]))
        elif kind == "blank":
            lines.append(r.choice(["", "   ", "\t"]))
        elif kind == "bad-level":
            lines.append(f"{ts} {r.choice(['info', 'TRACE', 'ERR', 'notice'])} {svc} {ms}")
        elif kind == "bad-ms":
            lines.append(f"{ts} {level} {svc} {r.choice(['N/A', '-', f'{ms}ms', '1.5'])}")
        elif kind == "extra":
            lines.append(f"{ts} {level} {svc} {ms} trace_id={r.randrange(16 ** 6):06x}")
        else:
            lines.append(f"   {ts} {level} {svc} {ms}   ")   # valid once stripped
    return lines


def _reference(lines):
    records = []
    skipped = 0
    for line in lines:
        line = line.strip()
        if not line:
            skipped += 1
            continue
        parts = line.split()
        if len(parts) != 4 or parts[1] not in LEVELS:
            skipped += 1
            continue
        try:
            ms = int(parts[3])
        except ValueError:
            skipped += 1
            continue
        records.append({"ts": parts[0], "level": parts[1],
                        "service": parts[2], "ms": ms})
    return records, skipped


def test_solve():
    r = rng()
    for _ in range(4):
        lines = _gen(r)
        assert solve(lines) == _reference(lines)
