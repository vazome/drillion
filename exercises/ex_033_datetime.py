"""'When did it break, and for how long' is a datetime question, every time."""

from _lib import rng

META = {"topic": 33, "title": "datetime — strptime, deltas, busiest minute",
        "tier": 3, "minutes": 15, "prereqs": [], "tags": ["files-text"]}


def solve(lines):
    """WHY: After an outage the incident review asks two questions: how long
    did the event window last, from the first request to the last, and which
    minute was the busiest? The web server's access log gives one line per
    request with a timestamp, but the lines are out of order because several
    servers' logs were merged. You turn the timestamps into real times you
    can subtract and count.

    YOU GET: `lines` — a list of strings, each starting with a timestamp,
    like ["2026-08-12 10:31:04 GET /api/users", ...], in shuffled order. The
    test creates it and hands it to you; you never build it yourself.

    YOU RETURN: a dict with "span_seconds" (a whole number of seconds from
    the earliest to the latest line) and "busiest_minute" (a string like
    "2026-08-12 10:31").

    ─── exact rules ───
    Each line starts with a timestamp, then a request:

        2026-08-12 10:31:04 GET /api/users

    The lines arrive SHUFFLED, not in time order. Return:

        {"span_seconds": 517,                       # whole seconds, first event to last
         "busiest_minute": "2026-08-12 10:31"}      # minute with most events; ties -> earliest

    The timestamp is exactly the first 19 characters of a line; parse it
    with the format "%Y-%m-%d %H:%M:%S". span_seconds is an int.

    These stamps are naive — no timezone attached. In production you want
    an offset in the log and %z in the format so comparisons survive DST
    and multiple regions; Python refuses to compare naive with aware.
    """
    raise NotImplementedError


HINTS = [
    ("Strings that look like times are still strings. ISO-shaped ones happen "
    "to sort correctly, but you cannot subtract them — the moment the "
    "question is 'how long between', you need real datetime objects. Parse "
    "everything first; the rest is min, max and one subtraction."),
    ("Slice the first 19 characters, parse with datetime.strptime and the "
    "given format. Subtracting two datetimes gives a timedelta; its "
    ".total_seconds() is the number you want, wrapped in int. For the busy "
    "minute, strftime each datetime back down to '%Y-%m-%d %H:%M', count "
    "with Counter, and on a tie prefer the smallest minute string."),
    ("Different data, same moves:\n"
    "    from datetime import datetime\n"
    "    fmt = '%Y-%m-%d %H:%M:%S'\n"
    "    a = datetime.strptime('2026-01-05 09:15:30', fmt)\n"
    "    b = datetime.strptime('2026-01-05 09:18:00', fmt)\n"
    "    print(int((b - a).total_seconds()))   # 150\n"
    "    print(a.strftime('%Y-%m-%d %H:%M'))   # 2026-01-05 09:15\n"
    "Parse at the edge, compute in datetime-land, format back out only at "
    "the end."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    from datetime import datetime, timedelta
    base = datetime(2026, r.randint(1, 12), r.randint(1, 28),  # noqa: DTZ001 — naive log times
                    r.randint(0, 22), r.randint(0, 50))
    methods = ["GET", "GET", "POST", "DELETE"]
    paths = ["/api/users", "/health", "/login", "/metrics", "/api/orders"]
    lines = []
    for _ in range(r.randint(10, 25)):
        t = base + timedelta(minutes=r.randint(0, 8), seconds=r.randint(0, 59))
        lines.append(f'{t.strftime("%Y-%m-%d %H:%M:%S")} '
                     f'{r.choice(methods)} {r.choice(paths)}')
    r.shuffle(lines)
    return lines


def _reference(lines):
    from collections import Counter
    from datetime import datetime
    times = [datetime.strptime(l[:19], "%Y-%m-%d %H:%M:%S") for l in lines]  # noqa: DTZ007
    counts = Counter(t.strftime("%Y-%m-%d %H:%M") for t in times)
    busiest = min(counts, key=lambda m: (-counts[m], m))
    return {"span_seconds": int((max(times) - min(times)).total_seconds()),
            "busiest_minute": busiest}


def test_solve():
    r = rng()
    for _ in range(4):
        lines = _gen(r)
        assert solve(list(lines)) == _reference(lines)
