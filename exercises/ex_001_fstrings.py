"""f-string format specs — every ops report and CLI table uses them."""

from _lib import rng

META = {"topic": 1, "title": "f-strings — aligned report columns", "tier": 3,
        "minutes": 10, "prereqs": []}


def solve(rows):
    """Each row is (name, value); value is a float. Return ONE string,
    lines joined with "\\n", no trailing newline. Per line:

      - name left-aligned in a 14-wide column
      - value right-aligned in a 12-wide column, with a thousands
        separator and exactly 2 decimals

        [("api", 1234.5), ("db", 7.25)]  returns a string that prints as:

        api               1,234.50
        db                    7.25

    Names are always shorter than 14 chars, values under a million.
    """
    raise NotImplementedError


HINTS = [
    "Everything after the colon inside the braces is a format spec. You need "
    "three effects: pad-and-left-align the name, pad-and-right-align the "
    "number, and give the number commas plus fixed decimals. Then join the "
    "lines.",
    "The pieces: < left-aligns, > right-aligns, a number is the width, a "
    "comma turns on thousands separators, .2f fixes two decimals. They stack "
    "in one spec, in that order. Build one f-string per row, then "
    "'\\n'.join the lot.",
    "Different data, same shape:\n"
    "    for city, pop in [('oslo', 709037), ('york', 202821)]:\n"
    "        print(f'{city:<8}{pop:>12,}')\n"
    "    # oslo         709,037\n"
    "    # york         202,821\n"
    "For floats, add .2f right after the comma: {v:>12,.2f}.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    names = ["api", "db", "cache", "queue", "ingest", "worker", "gateway"]
    picked = r.sample(names, r.randint(3, 6))
    rows = [(n, round(r.uniform(0, 999), 2)) for n in picked]
    i = r.randrange(len(rows))
    rows[i] = (rows[i][0], round(r.uniform(1000, 99999), 2))
    return rows


def _reference(rows):
    return "\n".join(f"{name:<14}{value:>12,.2f}" for name, value in rows)


def test_solve():
    r = rng()
    for _ in range(4):
        rows = _gen(r)
        assert solve(list(rows)) == _reference(rows)
