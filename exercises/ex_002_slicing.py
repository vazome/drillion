"""Slicing — the fastest way to grab exactly the part of a list you mean."""

from _lib import rng

META = {"topic": 2, "title": "slicing — combine start, stop, step", "tier": 3,
        "minutes": 10, "prereqs": []}


def solve(xs):
    """Return a dict with five slices of xs. Do not modify xs.

        "trim":   everything except the first and last item
        "odds":   every 2nd item, starting from index 1
        "rev":    the whole list backwards
        "inner":  every 2nd item of the trimmed list — one slice,
                  all three of start, stop and step
        "last3":  the last three items

        [10, 11, 12, 13, 14, 15]
        ->  {"trim": [11, 12, 13, 14], "odds": [11, 13, 15],
             "rev": [15, 14, 13, 12, 11, 10], "inner": [11, 13],
             "last3": [13, 14, 15]}

    xs always has at least 5 items. No loops needed anywhere.
    """
    raise NotImplementedError


HINTS = [
    "The full form is [start:stop:step]; every part is optional and negatives "
    "count from the end. stop is exclusive. Work out which of the three parts "
    "each key actually needs — only one key needs all of them.",
    "trim is a start of 1 with a stop of -1. odds is a start of 1 with a step "
    "of 2. rev is a step of -1 on its own. inner is trim's start and stop "
    "with odds' step, in one slice. last3 is a negative start with no stop.",
    "Different data, same moves:\n"
    "    s = 'abcdefg'\n"
    "    print(s[1:-1])    # 'bcdef'\n"
    "    print(s[1::2])    # 'bdf'\n"
    "    print(s[::-1])    # 'gfedcba'\n"
    "    print(s[2:-2:2])  # 'ce'\n"
    "Strings and lists slice identically.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    return [r.randint(10, 99) for _ in range(r.randint(5, 10))]


def _reference(xs):
    return {
        "trim": xs[1:-1],
        "odds": xs[1::2],
        "rev": xs[::-1],
        "inner": xs[1:-1:2],
        "last3": xs[-3:],
    }


def test_solve():
    r = rng()
    for _ in range(4):
        xs = _gen(r)
        assert solve(list(xs)) == _reference(xs)
