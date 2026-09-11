from array import array


def solve(blob, readings):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    kept = [r.randint(-32768, 32767) for _ in range(r.randint(0, 4))]
    readings = []
    for _ in range(r.randint(3, 8)):
        # a third of the readings are outside the type, split between the two ends
        pick = r.random()
        if pick < 0.2:
            readings.append(r.randint(32768, 90000))
        elif pick < 0.35:
            readings.append(r.randint(-90000, -32769))
        else:
            readings.append(r.randint(-32768, 32767))
    return array("h", kept).tobytes(), readings


def _reference(blob, readings):
    stored, skipped = array("h", blob), []
    for value in readings:
        try:
            stored.append(value)
        except OverflowError:
            skipped.append(value)
    return {"stored": stored, "skipped": skipped, "nbytes": len(stored) * stored.itemsize}


def test_solve():
    r = rng()
    for _ in range(24):
        blob, readings = _gen(r)
        got, want = solve(blob, readings), _reference(blob, readings)
        assert got == want, f"for blob={blob!r} readings={readings}: got {got}"
        assert set(got) == {"stored", "skipped", "nbytes"}, f"exactly three keys, got {sorted(got)}"
        assert isinstance(got["stored"], array), f"stored must be an array, got {type(got['stored']).__name__}"
        assert got["stored"].typecode == "h", f"typecode must be 'h', got {got['stored'].typecode!r}"
        assert type(got["skipped"]) is list, "skipped is a plain list of ints"

    # the negative end is as real as the positive one, and -32768 is inside it
    edges = solve(b"", [-32768, 32767, 32768, -32769])
    assert edges == {"stored": array("h", [-32768, 32767]), "skipped": [32768, -32769], "nbytes": 4}, edges

    # skipped, never clamped: the refused reading must not reappear as the nearest one that fits
    clamped = solve(b"", [70000])
    assert list(clamped["stored"]) == [], f"a reading that will not fit is left out, got {list(clamped['stored'])}"
    assert clamped == {"stored": array("h"), "skipped": [70000], "nbytes": 0}, clamped

    kept = solve(array("h", [7, -7]).tobytes(), [1])
    assert list(kept["stored"]) == [7, -7, 1], "the blob comes first, then the readings that fit"
