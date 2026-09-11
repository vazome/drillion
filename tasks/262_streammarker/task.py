def solve(chunks, marker):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    marker = "".join(r.choice("AB") for _ in range(r.randint(2, 4)))
    text = "".join(r.choice("AB") for _ in range(r.randint(20, 60)))
    chunks, i = [], 0
    while i < len(text):
        step = r.randint(1, 7)  # ragged cuts, so markers straddle boundaries
        chunks.append(text[i : i + step])
        i += step
    return chunks, marker


def _failure(marker):
    table, i, j = [0], 0, 1
    while j < len(marker):
        if marker[i] == marker[j]:
            i += 1
        elif i > 0:
            i = table[i - 1]
            continue
        j += 1
        table.append(i)
    return table


def _reference(chunks, marker):
    table = _failure(marker)
    hits, j, passed = [], 0, 0
    for chunk in chunks:
        for k, ch in enumerate(chunk):
            while j > 0 and ch != marker[j]:
                j = table[j - 1]
            if ch == marker[j]:
                j += 1
                if j == len(marker):
                    hits.append(passed + k - len(marker) + 1)
                    j = table[j - 1]  # fall back, not reset, so overlaps are found
        passed += len(chunk)
    return hits


def _naive(text, marker):
    hits, at = [], text.find(marker)
    while at != -1:
        hits.append(at)
        at = text.find(marker, at + 1)
    return hits


def test_solve():
    r = rng()
    for _ in range(40):
        chunks, marker = _gen(r)
        joined = "".join(chunks)
        want = _reference(chunks, marker)
        assert want == _naive(joined, marker), "grader bug"
        assert solve(chunks, marker) == want, f"marker={marker!r} chunks={chunks}"

    # a boundary must not change the answer: same stream, three different cuts
    for cuts in ([1, 1, 4], [3, 3], [6]):
        chunks, at = [], 0
        for size in cuts:
            chunks.append("ABABAB"[at : at + size])
            at += size
        assert solve(chunks, "ABAB") == [0, 2], f"cut into {chunks}"

    # the marker at offset 0 is split across both chunks; a per-chunk search misses it
    assert solve(["AB", "ABAB"], "ABAB") == [0, 2], "an occurrence may straddle a boundary"
    assert solve(["hello ", "world"], "o w") == [4], "offsets count from the whole stream"
    assert solve(["AAAA"], "AA") == [0, 1, 2], "occurrences overlap"
    assert solve(["ab", "cab"], "ab") == [0, 3], "offsets are absolute, not per-chunk"
    assert solve([], "x") == []
    assert solve(["", "a", ""], "a") == [0], "an empty chunk adds nothing to the offset"
    assert solve(["abc"], "abcd") == [], "a marker longer than the stream cannot match"
