def solve(lines):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    msgs = ["disk full", "conn reset", "slow query", "cache miss", "upstream timeout"]
    out = []
    for i in range(r.randint(4, 12)):
        level = r.choice(["ERROR", "INFO", "WARN", "ERROR"])
        out.append(f"10:{i:02d} {level} {r.choice(msgs)}")
    return out


def _reference(lines):
    def is_error(line):
        return line.split(maxsplit=2)[1] == "ERROR"

    def message(line):
        return line.split(maxsplit=2)[2]

    return map(message, filter(is_error, lines))


def test_solve():
    r = rng()
    for _ in range(6):
        lines = _gen(r)
        got = solve(iter(lines))
        assert iter(got) is got, "return an iterator, not a list"
        assert list(got) == list(_reference(lines)), f"lines={lines}"

    # laziness: taking two messages must not have walked the whole log
    read = []

    def watched(lines):
        for line in lines:
            read.append(line)
            yield line

    lines = ["10:00 ERROR a", "10:01 ERROR b"] + [f"10:{i:02d} ERROR x" for i in range(2, 40)]
    it = solve(watched(lines))
    next(it), next(it)
    assert len(read) < 10, f"read {len(read)} lines to produce 2 messages"
