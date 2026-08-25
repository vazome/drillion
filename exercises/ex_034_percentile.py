"""Mean latency lies; the p95 is the number on the dashboard and in the interview."""

from _lib import rng

META = {"topic": 34, "title": "p95 latency — nearest-rank percentile", "tier": 3,
        "minutes": 10, "prereqs": [], "tags": ["files-text"]}


def solve(values, pct):
    """WHY: The service promise (SLO) says 95 percent of requests must finish
    under 300 ms. An average hides the slow requests that make customers
    complain, so the dashboard shows the p95: the response time that 95
    percent of requests are faster than. Given a list of measured response
    times, you compute that number the way the team has agreed to define it.

    YOU GET: `values` — a list of numbers (response times), like [0.1, 0.5,
    0.9, 0.3]. The test creates it and hands it to you; you never build it
    yourself.

    YOU GET: `pct` — a whole number from 1 to 100, like 95.

    YOU RETURN: one number — an actual element of the list, the pct-th
    percentile.

    ─── exact rules ───
    Return the pct-th percentile of values using the nearest-rank
    method: sort ascending, take the element at index ceil(pct/100 * n) - 1.

        solve([0.1, 0.5, 0.9, 0.3], 95)  ->  0.9
        solve([4, 1, 3, 2], 50)          ->  2

    Rules: values is never empty; 1 <= pct <= 100; return an actual
    element of the list, never an average of neighbours (no interpolation
    — this is the same definition the nginx drill uses). Do not modify
    the caller's list.
    """
    raise NotImplementedError


HINTS = [
    ("Percentile questions are really sorting questions. p95 means: line the "
    "values up ascending and point at the one 95 percent of the way along. "
    "The whole exercise is the off-by-one — ranks count from 1, list indexes "
    "from 0."),
    ("sorted(values) — not .sort(), the caller keeps their list. math.ceil of "
    "pct / 100 times the length gives the 1-based rank; subtract 1 to index. "
    "That is nearest-rank: you always return a real sample."),
    ("Different data, same three moves:\n"
    "    import math\n"
    "    vals = [12, 7, 45, 30, 22]\n"
    "    rank = math.ceil(90 / 100 * len(vals))   # 5\n"
    "    print(sorted(vals)[rank - 1])            # 45\n"
    "p50, p95, p99 are the same code — only the fraction changes."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    values = [round(r.uniform(0.001, 3.0), 3) for _ in range(r.randint(1, 40))]
    return values, r.choice([50, 90, 95, 99, 100])


def _reference(values, pct):
    import math
    return sorted(values)[math.ceil(pct / 100 * len(values)) - 1]


def test_solve():
    r = rng()
    for _ in range(6):
        values, pct = _gen(r)
        assert solve(list(values), pct) == _reference(values, pct)
