def solve(strand_a: str, strand_b: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


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
