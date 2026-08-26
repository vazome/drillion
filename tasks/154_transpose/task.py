def solve(text):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .-"


def _gen(r):
    shape = r.random()
    if shape < 0.15:
        lengths = [r.randint(1, 8)] * r.randint(1, 5)
    elif shape < 0.40:
        lengths = sorted(r.randint(1, 9) for _ in range(r.randint(2, 6)))
    elif shape < 0.65:
        lengths = sorted((r.randint(1, 9) for _ in range(r.randint(2, 6))), reverse=True)
    else:
        lengths = [r.randint(1, 9) for _ in range(r.randint(1, 6))]
    rows = []
    for length in lengths:
        row = "".join(r.choice(_ALPHABET) for _ in range(length))
        rows.append(row.rstrip() or r.choice("XYZ"))
    return "\n".join(rows)


def _reference(text):
    rows = text.splitlines()
    padded = []
    needed = 0
    for row in reversed(rows):
        needed = max(needed, len(row))
        padded.append(row.ljust(needed))
    padded.reverse()
    width = max((len(row) for row in padded), default=0)
    return "\n".join("".join(row[index] for row in padded if index < len(row))
                     for index in range(width))


def test_solve():
    r = rng()
    for _ in range(6):
        text = _gen(r)
        assert solve(text) == _reference(text), f"text {text!r}"

    # canonical cases (exercism/python practice/transpose)
    assert solve("") == ""
    assert solve("A1") == "A\n1"
    assert solve("A\n1") == "A1"
    assert solve("ABC\n123") == "A1\nB2\nC3"
    assert solve("T\nEE\nAAA\nSSSS\nEEEEE\nRRRRRR") == "TEASER\n EASER\n  ASER\n   SER\n    ER\n     R"
    assert solve("11\n2\n3333\n444\n555555\n66666") == "123456\n1 3456\n  3456\n  3 56\n    56\n    5"
    assert solve("FRACTURE\nOUTLINED\nBLOOMING\nSEPTETTE") == "FOBS\nRULE\nATOP\nCLOT\nTIME\nUNIT\nRENT\nEDGE"
