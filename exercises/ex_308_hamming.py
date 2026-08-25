"""hamming — count differing positions, and refuse the comparison that makes no sense."""
# SOURCE: exercism/python practice/hamming (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/library/functions.html#zip  — zip() walks two sequences side by
#       side and stops at the shorter one (which is why you must check lengths yourself)
#   https://docs.python.org/3/tutorial/errors.html#raising-exceptions  — raise, and why the
#       message matters as much as the exception type
#   https://docs.python.org/3/reference/expressions.html#generator-expressions  — the
#       (x for y in z) form you can hand straight to sum()

import pytest
from _lib import rng

META = {"topic": 308, "title": "hamming — how many positions do two strands differ in?",
        "minutes": 10, "prereqs": [200, 206, 209, 221, 227],
        "tags": ["exercism", "generator-expressions", "raising-and-handling-errors",
                 "sequences", "data-structures"]}


def solve(strand_a, strand_b):
    """WHY: When a cell divides, its DNA is copied, and copies pick up
    mistakes. Lay two strands side by side, count the positions where the
    letters disagree, and you have measured how many mistakes crept in —
    the Hamming distance. The same count is used far outside biology: how
    many bits of a checksum differ, how many fields drifted between two
    config versions. The second half of the job matters just as much:
    comparing strands of different lengths is not a small answer, it is a
    bug in whoever called you, so it has to fail loudly instead of quietly
    measuring the overlap.

    YOU GET:
      `strand_a`, `strand_b` — two strings of the DNA letters A, C, G and
      T, e.g. "GAGCCTACTAACGGGAT". Either may be empty.

    YOU RETURN: an int — the number of positions at which the two strands
    hold different letters.

    ─── exact rules ───
    Compare position by position: position 0 with position 0, and so on.
    Two empty strands differ in nothing, so the answer is 0.

    If the two strands are NOT the same length, raise `ValueError` with
    exactly this message:

        Strands must be of equal length.

    Do not return a number in that case and do not compare only the part
    they have in common — an empty strand against a one-letter strand is
    an error too.

        solve("GGACTGAAATCTG", "GGACTGAAATCTG")  ->  0
        solve("GGACGGATTCTG", "AGGACGGATTCT")    ->  9
        solve("AATG", "AAA")                     ->  raises ValueError
    """
    raise NotImplementedError


HINTS = [
    ("Two jobs in one function, and the order matters: first decide whether this "
    "comparison is even legal, then do the counting. The legality test is about "
    "lengths only — nothing to do with which letters are in the strands."),
    ("For the guard: compare the two lengths and `raise ValueError(\"...\")` with "
    "the message spelled exactly as the caller expects, full stop included. For "
    "the count: `zip(a, b)` hands you the pairs one position at a time, and a "
    "comparison like `x != y` is already worth 1 when you add it up, because "
    "True counts as 1 — so a single sum() over a generator expression finishes "
    "the job."),
    ("Different data, same two shapes:\n"
    "    changed = sum(old[k] != new[k] for k in keys)   # count of drifted keys\n"
    "and the guard you have written in every HTTP handler — validate the input, "
    "raise on nonsense, and only then do the work. Note that zip() silently "
    "stops at the shorter input, so without the guard you would happily return "
    "a wrong, plausible-looking number."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    n = r.randint(0, 22)
    strand_a = "".join(r.choice("ACGT") for _ in range(n))
    strand_b = list(strand_a)
    for i in r.sample(range(n), r.randint(0, n)) if n else []:
        strand_b[i] = r.choice("ACGT")
    return strand_a, "".join(strand_b)


def _reference(strand_a, strand_b):
    if len(strand_a) != len(strand_b):
        raise ValueError("Strands must be of equal length.")
    return sum(a != b for a, b in zip(strand_a, strand_b, strict=True))


def test_solve():
    r = rng()
    for _ in range(6):
        strand_a, strand_b = _gen(r)
        assert solve(strand_a, strand_b) == _reference(strand_a, strand_b), \
            f"{strand_a} vs {strand_b}"

    # canonical cases (exercism/python practice/hamming)
    assert solve("", "") == 0
    assert solve("G", "T") == 1
    assert solve("GGACTGAAATCTG", "GGACTGAAATCTG") == 0
    assert solve("GGACGGATTCTG", "AGGACGGATTCT") == 9
    with pytest.raises(ValueError, match=r"Strands must be of equal length\."):
        solve("AATG", "AAA")
    with pytest.raises(ValueError, match=r"Strands must be of equal length\."):
        solve("G", "")
