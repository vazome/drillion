def solve(rows: list[str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    keys = ["cpu", "mem", "disk", "net", "load", "fd"]
    good = [f"{k}={r.randint(0, 99)}" for k in r.sample(keys, r.randint(2, 4))]
    bad = r.sample(["junk", "mem=x", "cpu=", "a=b=c", "no_equals_here", "fd=1.5"],
                   r.randint(1, 3))
    rows = good + bad
    r.shuffle(rows)
    return rows


def _reference(rows):
    out = {}
    for row in rows:
        try:
            k, v = row.split("=")
            out[k] = int(v)
        except ValueError:
            continue
    return out


def test_solve():
    r = rng()
    for _ in range(4):
        rows = _gen(r)
        assert solve(list(rows)) == _reference(rows)
