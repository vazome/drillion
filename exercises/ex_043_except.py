"""try/except — catch the specific thing, not everything."""

from _lib import rng

META = {"topic": 43, "title": "try/except — survive bad input", "tier": 3,
        "minutes": 10, "prereqs": [], "tags": ["errors"]}


def solve(rows):
    """WHY: A monitoring agent sends metrics as lines like "cpu=90". Now and
    then a line is garbage: truncated, missing the equals sign, or with a
    value that is not a number. A parser that crashes on the first bad line
    takes the whole dashboard down. The team wants a parser that keeps the
    good lines and quietly skips the bad ones, but only for the specific
    errors bad input causes, so real bugs still surface.

    YOU GET: `rows` — a list of strings, like ["cpu=90", "junk", "mem=x",
    "disk=12"]. The test creates it and hands it to you; you never build it
    yourself.

    YOU RETURN: a dict from name to whole number for the rows that parsed,
    like {"cpu": 90, "disk": 12}.

    ─── exact rules ───
    Each row is a string that SHOULD look like "name=42".

    Return {name: number} for every row that parses, silently skipping rows
    that are malformed (no "=", or a right-hand side that isn't a whole number).

        ["cpu=90", "junk", "mem=x", "disk=12"]  ->  {"cpu": 90, "disk": 12}

    Do not use a bare `except:` — catch the specific errors. Real log parsers
    live or die on this, and interviewers feed you dirty data on purpose.
    """
    raise NotImplementedError


HINTS = [
    ("Two different things can blow up: splitting a row with no '=' in it, and "
    "int() on something that isn't a number. Find out what each one raises."),
    ("int('x') raises ValueError. Unpacking 'junk'.split('=') into two names "
    "raises ValueError too. So one except clause covers both here — but write "
    "the name, never a bare except."),
    ("Different data, same shape:\n"
    "    out = {}\n"
    "    for item in ['a:1', 'oops', 'b:2']:\n"
    "        try:\n"
    "            k, v = item.split(':')\n"
    "            out[k] = int(v)\n"
    "        except ValueError:\n"
    "            continue          # skip it, keep going\n"
    "    print(out)     # {'a': 1, 'b': 2}"),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    keys = ["cpu", "mem", "disk", "net", "load", "fd"]
    good = [f"{k}={r.randint(0, 99)}" for k in r.sample(keys, r.randint(2, 4))]
    bad = r.sample(["junk", "mem=x", "cpu=", "a=b=c", "no_equals_here", "fd=1.5"],
                   r.randint(1, 3))
    rows = good + bad
    r.shuffle(rows)
    return rows


def _reference(rows):
    out = {}
    for row in rows:
        try:
            k, v = row.split("=")
            out[k] = int(v)
        except ValueError:
            continue
    return out


def test_solve():
    r = rng()
    for _ in range(4):
        rows = _gen(r)
        assert solve(list(rows)) == _reference(rows)
