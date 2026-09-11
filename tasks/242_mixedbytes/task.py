def solve(records):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_PIECES = ["started", "café", "naïve", "level=warn", "日本", "user=ada", "ratio=0.5", "°C"]


def _gen(r):
    records = []
    for _ in range(r.randint(4, 8)):
        line = " ".join(r.sample(_PIECES, r.randint(1, 3))).encode()
        if r.random() < 0.3:
            # a byte no UTF-8 sequence can start with, spliced into otherwise valid text
            line = line + bytes([r.choice([0xE9, 0xFF, 0x80])]) + b"end"
        records.append(line)
    # one record that is valid UTF-8 and really does contain a replacement character
    records.insert(r.randrange(len(records) + 1), f"repaired � by {r.choice(_PIECES)}".encode())
    return records


def _reference(records):
    text, bad = [], []
    for i, raw in enumerate(records):
        try:
            text.append(raw.decode("utf-8"))
        except UnicodeDecodeError:
            bad.append(i)
            text.append(raw.decode("utf-8", errors="replace"))
    return {"text": text, "bad": bad, "ascii": "\n".join(text).encode("ascii", "backslashreplace")}


def test_solve():
    r = rng()
    seen_bad = False
    for _ in range(24):
        records = _gen(r)
        got, want = solve(records), _reference(records)
        assert got == want, f"for records={records}: got {got}"
        assert set(got) == {"text", "bad", "ascii"}, f"exactly three keys, got {sorted(got)}"
        assert len(got["text"]) == len(records), "every record comes through, repaired or not"
        assert isinstance(got["ascii"], bytes), f"ascii must be bytes, got {type(got['ascii']).__name__}"
        assert max(got["ascii"], default=0) < 128, "ascii must contain no byte above 127"
        seen_bad = seen_bad or bool(want["bad"])
    assert seen_bad, "generator should produce invalid records"

    canonical = solve([b"caf\xc3\xa9", b"caf\xe9", "already � here".encode()])
    assert canonical == {
        "text": ["café", "caf�", "already � here"],
        "bad": [1],
        "ascii": b"caf\\xe9\ncaf\\ufffd\nalready \\ufffd here",
    }, canonical

    # a record that was valid UTF-8 and already held a replacement character is not a bad record
    innocent = solve(["�".encode()])
    assert innocent["bad"] == [], f"searching for \\ufffd is not the test: got bad={innocent['bad']}"
    assert innocent["text"] == ["�"], innocent["text"]
