def solve(dna_strand):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    n = r.randint(0, 24)
    return "".join(r.choice("ACGT") for _ in range(n))


def _reference(dna_strand):
    return dna_strand.translate(str.maketrans("AGCT", "UCGA"))


def test_solve():
    r = rng()
    for _ in range(6):
        dna_strand = _gen(r)
        assert solve(dna_strand) == _reference(dna_strand), f"strand {dna_strand!r}"

    # canonical cases (exercism/python practice/rna-transcription)
    assert solve("") == ""
    assert solve("C") == "G"
    assert solve("G") == "C"
    assert solve("T") == "A"
    assert solve("A") == "U"
    assert solve("ACGTGGTCTTAA") == "UGCACCAGAAUU"
