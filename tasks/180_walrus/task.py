def solve(read):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    words = ["disk", "full", "conn", "reset", "ok", "slow", "query"]
    return [r.choice(words) for _ in range(r.randint(0, 6))]


def _source(chunks, calls):
    rest = list(chunks)

    def read():
        calls.append(1)
        return rest.pop(0) if rest else ""

    return read


def _reference(read):
    out = []
    while chunk := read():
        out.append(chunk)
    return out


def test_solve():
    r = rng()
    for chunks in [[], ["ab", "cd"]] + [_gen(r) for _ in range(6)]:
        calls = []
        assert solve(_source(chunks, calls)) == list(chunks), f"chunks={chunks}"
        assert len(calls) == len(chunks) + 1, (
            f"{len(calls)} calls to read() for {len(chunks)} chunks, expected {len(chunks) + 1}")
