def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import re
from itertools import groupby

from _lib import rng

_RUNS = ["A", "B", "C", "W", "X", "Y", "Z", "a", "b", "c", "q", "w", "z", " ", " "]


def _gen(r):
    chunks = []
    for _ in range(r.randint(0, 8)):
        chunks.append(r.choice(_RUNS) * r.randint(1, 14))
    return "".join(chunks)


def _reference():
    def encode(text):
        pieces = []
        for char, group in groupby(text):
            size = len(list(group))
            pieces.append(char if size == 1 else f"{size}{char}")
        return "".join(pieces)

    def decode(text):
        return re.sub(r"(\d+)(\D)", lambda run: run.group(2) * int(run.group(1)), text)

    return {"encode": encode, "decode": decode}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert set(got) == {"encode", "decode"}, "solve() must return both functions"
    for _ in range(6):
        text = _gen(r)
        encoded = want["encode"](text)
        assert got["encode"](text) == encoded, f"encode {text!r}"
        assert got["decode"](encoded) == text, f"decode {encoded!r}"

    # canonical cases (exercism/python practice/run-length-encoding)
    assert got["encode"]("") == ""
    assert got["encode"]("XYZ") == "XYZ"
    assert got["encode"]("AABBBCCCC") == "2A3B4C"
    assert got["encode"]("WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWB") == "12WB12W3B24WB"
    assert got["encode"]("  hsqq qww  ") == "2 hs2q q2w2 "
    assert got["decode"]("") == ""
    assert got["decode"]("2A3B4C") == "AABBBCCCC"
    assert got["decode"]("2 hs2q q2w2 ") == "  hsqq qww  "
    assert got["decode"]("12WB12W3B24WB") == "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWB"
    assert got["decode"](got["encode"]("zzz ZZ  zZ")) == "zzz ZZ  zZ"
