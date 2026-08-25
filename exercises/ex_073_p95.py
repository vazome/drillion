"""Whole-task drill: the nginx log question, end to end.

Combines topics 19 (Counter), 22 (set), 28 (str), 34 (percentile).
Passing this cleanly pushes those components further out too.
"""

from _lib import rng

META = {"topic": 73, "title": "DRILL: nginx log -> top IPs, status mix, p95",
        "tier": 4, "minutes": 30, "prereqs": [19, 28],
        "practices": [19, 22, 28, 34], "tags": ["whole-task"]}


def solve(lines):
    """WHY: The site was slow last night and the manager wants a quick read of
    the web server's access log: which three visitors (IP addresses) made
    the most requests, how the responses split between success and error
    classes (2xx, 4xx, 5xx), and how slow the slowest requests were. That
    last one is the "p95": the time that 95 percent of requests came in
    under. This is the single most common hands-on question in DevOps
    interviews.

    YOU GET: `lines` — a list of strings, one per request, each in the
    standard nginx log format, like
    '10.0.0.1 - - [07/Aug/2026:10:12:33 +1000] "GET /api/users HTTP/1.1"
    200 1234 0.043'. The test generates them and hands them to you.

    YOU RETURN: a dict with three keys: "top_ips" (a list of the 3 busiest
    (ip, count) pairs, busiest first), "statuses" (a dict like {"2xx": 5,
    "4xx": 1}, only for classes that occur) and "p95" (a number of seconds).

    ─── exact rules ───
    Parse access-log lines and return a summary dict:

        {"top_ips":  [(ip, count), ...],   # 3 busiest, most first
         "statuses": {"2xx": 5, "4xx": 1}, # only classes that occur
         "p95":      0.418}                # 95th percentile duration

    A line looks like:

        10.0.0.1 - - [07/Aug/2026:10:12:33 +1000] "GET /api/users HTTP/1.1" 200 1234 0.043
        ^ip                                        ^method ^path            ^status ^bytes ^seconds

    p95 uses the nearest-rank method: sort ascending, take the value at
    index ceil(0.95 * len) - 1. No interpolation.

    This is the most-asked DevOps screen question in existence. Narrate it
    out loud while you write it.
    """
    raise NotImplementedError


HINTS = [
    ("Do it in four separate passes, not one clever loop. Parse first: turn "
    "every line into the few fields you need, then answer each question from "
    "that. Clear beats compact — and the interviewer is listening to you "
    "explain, not admiring your line count."),
    ("Fields come from line.split(). The status is at index 8, the duration is "
    "last. Status class: 500 // 100 gives 5, so f'{500//100}xx' builds '5xx'. "
    "For p95 you need math.ceil."),
    ("Different data, same shape — the percentile piece alone:\n"
    "    import math\n"
    "    vals = [0.5, 0.1, 0.9, 0.3]\n"
    "    idx = math.ceil(0.95 * len(vals)) - 1\n"
    "    print(sorted(vals)[idx])     # 0.9\n"
    "The other three pieces are exercises you have already passed."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    ips = [f"10.0.{r.randint(0, 3)}.{i}" for i in range(1, 6)]
    paths = ["/api/users", "/health", "/api/orders", "/metrics"]
    # distinct hit-counts per IP: no ties, so top-3 order is unambiguous
    hits = r.sample(range(2, 12), len(ips))
    pool = [ip for ip, n in zip(ips, hits) for _ in range(n)]
    r.shuffle(pool)
    lines = []
    for ip in pool:
        st = r.choice([200, 200, 200, 201, 404, 500])
        dur = round(r.uniform(0.001, 2.0), 3)
        ts = f"0{r.randint(1,9)}/Aug/2026:10:{r.randint(10,59)}:{r.randint(10,59)} +1000"
        lines.append(f'{ip} - - [{ts}] "GET {r.choice(paths)} HTTP/1.1" '
                     f'{st} {r.randint(0, 2000)} {dur}')
    return lines


def _reference(lines):
    import math
    from collections import Counter
    parts = [line.split() for line in lines]
    ips = Counter(p[0] for p in parts)
    statuses = Counter(f"{int(p[8]) // 100}xx" for p in parts)
    durs = sorted(float(p[-1]) for p in parts)
    return {"top_ips": ips.most_common(3),
            "statuses": dict(statuses),
            "p95": durs[math.ceil(0.95 * len(durs)) - 1]}


def test_solve():
    r = rng()
    for _ in range(3):
        lines = _gen(r)
        assert solve(list(lines)) == _reference(lines)
