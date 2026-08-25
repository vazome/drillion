"""Dedupe with a set — the runner-up trap."""

from _lib import rng

META = {"topic": 22, "title": "set — second-highest distinct value", "tier": 3,
        "minutes": 8, "prereqs": []}


def solve(scores):
    """WHY: A performance review ranks people by score and the runner-up gets a
    bonus. Two people tied for first. The naive "second item of the sorted
    list" picks the other first-place person, not the real runner-up. The
    business wants the second-highest distinct value, so duplicates have to
    be treated as one value before picking. This is a well-known interview
    trap.

    YOU GET: `scores` — a list of numbers like [2, 3, 6, 6, 5], always with
    at least two different values. The test creates it and hands it to you;
    you never build it yourself.

    YOU RETURN: one number: the second-highest value once duplicates are
    ignored.

    ─── exact rules ───
    Return the second-HIGHEST distinct score.

        [2, 3, 6, 6, 5]  ->  5      (6 appears twice; it is still one value)

    There are always at least two distinct values.
    """
    raise NotImplementedError


HINTS = [
    ("Sorting alone isn't enough: the top two slots can hold the same number "
    "twice. Duplicates have to disappear before you index anything."),
    ("One built-in type refuses to hold duplicates. Convert, sort what's left, "
    "then pick a position."),
    ("Different data, same shape:\n"
    "    vals = [4, 9, 1, 9, 7]\n"
    "    uniq = sorted(set(vals))\n"
    "    print(uniq)        # [1, 4, 7, 9]\n"
    "    print(uniq[-2])    # 7  — second from the end\n"
    "sorted() ascending plus a negative index, or reverse=True plus [1]."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    base = r.sample(range(1, 60), r.randint(3, 7))
    # always duplicate the maximum: sorted(vals)[-2] without a set must fail
    vals = base + [max(base)] + [r.choice(base) for _ in range(r.randint(0, 2))]
    r.shuffle(vals)
    return vals


def _reference(scores):
    return sorted(set(scores))[-2]


def test_solve():
    r = rng()
    for _ in range(4):
        s = _gen(r)
        assert solve(list(s)) == _reference(s)
