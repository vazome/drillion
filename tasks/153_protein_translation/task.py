def solve(strand: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_CODONS = {"AUG": "Methionine", "UUU": "Phenylalanine", "UUC": "Phenylalanine",
           "UUA": "Leucine", "UUG": "Leucine", "UCU": "Serine", "UCC": "Serine",
           "UCA": "Serine", "UCG": "Serine", "UAU": "Tyrosine", "UAC": "Tyrosine",
           "UGU": "Cysteine", "UGC": "Cysteine", "UGG": "Tryptophan",
           "UAA": "STOP", "UAG": "STOP", "UGA": "STOP"}

_CODING = [codon for codon, name in _CODONS.items() if name != "STOP"]
_STOPS = [codon for codon, name in _CODONS.items() if name == "STOP"]


def _gen(r):
    codons = [r.choice(_CODING) for _ in range(r.randint(1, 8))]
    roll = r.random()
    if roll < 0.35:
        codons.insert(r.randrange(len(codons) + 1), r.choice(_STOPS))
    elif roll < 0.50:
        codons.append(r.choice(_STOPS))
    return "".join(codons)


def _reference(strand):
    names = []
    for start in range(0, len(strand), 3):
        name = _CODONS[strand[start:start + 3]]
        if name == "STOP":
            break
        names.append(name)
    return names


def test_solve():
    r = rng()
    for _ in range(6):
        strand = _gen(r)
        assert solve(strand) == _reference(strand), f"strand {strand!r}"

    # canonical cases (exercism/python practice/protein-translation)
    assert solve("AUG") == ["Methionine"]
    assert solve("UGG") == ["Tryptophan"]
    assert solve("UAA") == []
    assert solve("AUGUUUUGG") == ["Methionine", "Phenylalanine", "Tryptophan"]
    assert solve("UGGUAG") == ["Tryptophan"]
    assert solve("AUGAUG") == ["Methionine", "Methionine"]
    assert solve("UGGUGUUAUUAAUGGUUU") == ["Tryptophan", "Cysteine", "Tyrosine"]
