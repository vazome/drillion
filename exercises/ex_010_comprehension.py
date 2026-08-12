"""Comprehension with a filter — transform some, skip the rest."""

from _lib import rng

META = {"topic": 10, "title": "comprehension — transform + filter", "tier": 3,
        "minutes": 8, "prereqs": []}


def solve(records):
    """Each record is [name, score]. Return the NAMES of everyone whose
    score is 50 or more, uppercased, in the order they appear.

        [["ana", 80], ["bo", 12], ["cy", 50]]  ->  ["ANA", "CY"]

    Write it as a single list comprehension.
    """
    raise NotImplementedError


HINTS = [
    "Two jobs in one line: throw away the low scorers (a filter), and change "
    "what survives into an uppercase name (a transform).",
    "Skeleton, fill the three slots:\n"
    "    [ ???? for r in records if ???? ]\n"
    "Remember r is one whole [name, score] pair — index into it.",
    "Different data, same shape:\n"
    "    pairs = [['ny', 8], ['berlin', 3], ['tokyo', 14]]\n"
    "    big = [p[0].upper() for p in pairs if p[1] > 5]\n"
    "    print(big)      # ['NY', 'TOKYO']",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    names = ["ana", "bo", "cy", "dee", "eli", "fay", "gus", "hal"]
    return [[n, r.randint(0, 100)] for n in r.sample(names, r.randint(4, 8))]


def _reference(records):
    return [name.upper() for name, score in records if score >= 50]


def test_solve():
    r = rng()
    for _ in range(4):
        recs = _gen(r)
        assert solve(recs) == _reference(recs)
